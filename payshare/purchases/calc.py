from collections import namedtuple
from decimal import Decimal
from functools import lru_cache

CollectiveMember = namedtuple("CollectiveMember", ["member", "amount"])
"""A member of the Collective and the absolute amount they owe or are owed."""

MemberSlot = namedtuple("MemberSlot", ["role", "index"])
"""Reference to a CollectiveMember via its role ('debtor'/'creditor') and list index."""

Transfer = namedtuple("Transfer", ["debtor_index", "creditor_index", "amount"])


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


def _minimum_paybacks(member_to_balance, member_to_disbursed):
    def most_disbursed_first(collective_member):
        return (
            -member_to_disbursed[collective_member.member],
            -collective_member.amount,
            collective_member.member.id,
        )

    debtors = sorted(
        [
            CollectiveMember(member, abs(balance))
            for member, balance in member_to_balance.items()
            if balance < 0
        ],
        key=most_disbursed_first,
    )
    creditors = sorted(
        [
            CollectiveMember(member, balance)
            for member, balance in member_to_balance.items()
            if balance > 0
        ],
        key=most_disbursed_first,
    )

    def member_for_slot(slot):
        collective_members = debtors if slot.role == "debtor" else creditors
        return collective_members[slot.index]

    activity_priority = sorted(
        [MemberSlot("debtor", index) for index in range(len(debtors))]
        + [MemberSlot("creditor", index) for index in range(len(creditors))],
        key=lambda slot: (
            -member_to_disbursed[member_for_slot(slot).member],
            slot.role,
            slot.index,
        ),
    )

    def score(transfers):
        debtor_counts = [0] * len(debtors)
        creditor_counts = [0] * len(creditors)
        for transfer in transfers:
            debtor_counts[transfer.debtor_index] += 1
            creditor_counts[transfer.creditor_index] += 1
        activity_counts = tuple(
            debtor_counts[slot.index]
            if slot.role == "debtor"
            else creditor_counts[slot.index]
            for slot in activity_priority
        )
        return len(transfers), activity_counts

    @lru_cache(maxsize=None)
    def settle(debts, credits):
        if not any(debts) or not any(credits):
            return ()

        best = None
        best_score = None
        debtor_index = next(index for index, debt in enumerate(debts) if debt)
        debt = debts[debtor_index]
        for creditor_index, credit in enumerate(credits):
            if credit == 0:
                continue

            amount = min(debt, credit)
            remaining_debts = list(debts)
            remaining_credits = list(credits)
            remaining_debts[debtor_index] -= amount
            remaining_credits[creditor_index] -= amount
            transfers = (
                Transfer(debtor_index, creditor_index, amount),
            ) + settle(tuple(remaining_debts), tuple(remaining_credits))
            transfers_score = score(transfers)
            if best_score is None or transfers_score < best_score:
                best = transfers
                best_score = transfers_score

        return best or ()

    transfers = settle(
        tuple(debtor.amount for debtor in debtors),
        tuple(creditor.amount for creditor in creditors),
    )
    return [
        Payback(
            debtors[transfer.debtor_index].member,
            creditors[transfer.creditor_index].member,
            transfer.amount,
        )
        for transfer in transfers
    ]


def calc_paybacks(collective):
    from payshare.purchases.models import get_member_share_of_purchase  # noqa

    members = collective.members
    num_members = len(members)

    purchases = collective.purchases

    member_to_balance = {}
    member_to_disbursed = {}
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
        credit = sum(
            liquidation.amount.amount
            for liquidation in collective.liquidations.filter(creditor=member)
        )
        debt = sum(
            liquidation.amount.amount
            for liquidation in collective.liquidations.filter(debtor=member)
        )
        balance = owed_from_collective - owed_to_collective + credit - debt
        member_to_balance[member] = balance
        member_to_disbursed[member] = sum(
            purchase.price.amount for purchase in purchases.filter(buyer=member)
        )

    balance_residue = sum(member_to_balance.values(), Decimal("0"))
    if balance_residue:
        largest_balance_member = max(
            member_to_balance, key=lambda member: abs(member_to_balance[member])
        )
        member_to_balance[largest_balance_member] -= balance_residue

    return _minimum_paybacks(member_to_balance, member_to_disbursed)
