# -*- coding: utf-8 -*-


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
        return ("{self.debtor.username} pays back {self.amount} "
                "to {self.creditor.username}".format(self=self))

    def swap_roles(self):
        temp = self.debtor
        self.debtor = self.creditor
        self.creditor = temp

    def to_json(self):
        return {
            "debtor": self.debtor.id,
            "creditor": self.creditor.id,
            "amount": self.amount,
        }


# FIXME: There is a lot of redundancy when looking at Collective.stats
def calc_paybacks(collective):
    creditors = []
    debtors = []
    paybacks = []

    members = collective.members
    num_members = len(members)

    purchases = collective.purchases
    prices = [float(purchase.price.amount) for purchase in purchases]
    overall_purchased = sum(prices)
    try:
        each_member_must_pay = float(overall_purchased) / float(num_members)
    except ZeroDivisionError:
        each_member_must_pay = 0
    member_to_balance = {}
    for member in collective.members:
        member_purchased = sum([
            float(purchase.price.amount) for purchase in purchases
            if purchase.buyer == member
        ])
        balance = float(member_purchased) - each_member_must_pay
        member_to_balance[member] = balance

    sorted_balances = sorted(
        member_to_balance.items(),
        key=lambda item: item[1],
        reverse=True)

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
        liquidation_user_ids = sorted([liquidation.creditor.id,
                                       liquidation.debtor.id])
        for payback in paybacks:
            payback_user_ids = sorted([payback.creditor.id,
                                       payback.debtor.id])
            if liquidation_user_ids == payback_user_ids:
                return payback
        return None

    liquidations = sorted(collective.liquidations,
                          key=lambda liq: liq.amount.amount)
    for liquidation in liquidations:
        liquidation_amount = float(liquidation.amount.amount)
        payback = _get_matching_payback(paybacks, liquidation)
        if payback is not None:
            if liquidation.debtor.id == payback.debtor.id:
                payback.amount += liquidation_amount
            else:
                payback.amount -= liquidation_amount
            if payback.amount < 0:
                payback.swap_roles()
                payback.amount = abs(payback.amount)
        else:
            payback = Payback(liquidation.debtor,
                              liquidation.creditor,
                              liquidation_amount)
            paybacks.append(payback)

    return paybacks
