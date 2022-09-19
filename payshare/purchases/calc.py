from decimal import Decimal


class BaseMember(object):
    """Member with a negative balance owes, positive means he'll get money."""

    def __init__(self, user, balance):
        self.user = user
        self.balance = balance

    def __repr__(self):
        return "{self.member.username} {self.balance}".format(self=self)


class Debtor(BaseMember):
    """This guy is in debt to the Collective."""

    def pay_debt_to(self, creditor):
        if self.balance == 0 or creditor.balance == 0:
            return None

        max_repayment = abs(self.balance)
        if abs(creditor.balance) < max_repayment:
            max_repayment = abs(creditor.balance)

        payback = Payback(self.user, creditor.user, max_repayment)
        self.balance += max_repayment
        creditor.balance -= max_repayment
        return payback


class Creditor(BaseMember):
    """The Collective owes this guy money."""


class Payback(object):
    def __init__(self, debtor_user, creditor_user, amount):
        self.debtor = debtor_user
        self.creditor = creditor_user
        self.amount = amount

    def __repr__(self):
        return (
            "{self.debtor.username} pays back {self.amount} "
            "to {self.creditor.username}".format(self=self)
        )

    def _swap_roles(self):
        temp = self.debtor
        self.debtor = self.creditor
        self.creditor = temp

    def enforce_positive_amount(self):
        if self.amount < 0:
            self._swap_roles()
            self.amount = abs(self.amount)

    def to_json(self):
        return {
            "debtor": self.debtor.id,
            "creditor": self.creditor.id,
            "amount": float(self.amount),
        }


def calc_paybacks(collective):
    from payshare.purchases.models import get_member_share_of_purchase  # noqa

    creditors = []
    debtors = []
    paybacks = []

    members = collective.members
    num_members = len(members)

    purchases = collective.purchases

    member_to_balance = {}
    for member in collective.members:
        owed_to_collective = sum(
            [
                get_member_share_of_purchase(purchase, member, num_members)
                for purchase in purchases.exclude(buyer=member)
            ]
        )
        owed_from_collective = sum(
            [
                purchase.price.amount
                - get_member_share_of_purchase(purchase, member, num_members)
                for purchase in purchases.filter(buyer=member)
            ]
        )
        balance = owed_from_collective - owed_to_collective
        member_to_balance[member] = balance

    sorted_balances = sorted(
        member_to_balance.items(), key=lambda item: item[1], reverse=True
    )

    for member, balance in sorted_balances:
        if balance > 0:
            creditors.append(Creditor(member, balance))
        elif balance < 0:
            debtors.append(Debtor(member, balance))

    for debtor in debtors:
        for creditor in creditors:
            payback = debtor.pay_debt_to(creditor)
            if payback is not None:
                paybacks.append(payback)

    def _get_matching_payback(paybacks, liquidation):
        """Return Payback that uses the same Users as the Liquidation.

        It does not matter if creditor/debtor roles are reversed, return
        it anyway or None.
        """
        liquidation_user_ids = sorted([liquidation.creditor.id, liquidation.debtor.id])
        for payback in paybacks:
            payback_user_ids = sorted([payback.creditor.id, payback.debtor.id])
            if liquidation_user_ids == payback_user_ids:
                return payback
        return None

    liquidations = sorted(collective.liquidations, key=lambda liq: liq.amount.amount)
    for liquidation in liquidations:
        liquidation_amount = liquidation.amount.amount
        payback = _get_matching_payback(paybacks, liquidation)
        if payback is not None:
            if liquidation.debtor.id == payback.debtor.id:
                payback.amount += liquidation_amount
            else:
                payback.amount -= liquidation_amount
            payback.enforce_positive_amount()
        else:
            payback = Payback(
                liquidation.debtor, liquidation.creditor, liquidation_amount
            )
            payback.enforce_positive_amount()
            paybacks.append(payback)

    return paybacks
