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

    def to_json(self):
        return {
            "debtor": self.debtor.id,
            "creditor": self.creditor.id,
            "amount": self.amount,
        }


def calc_paybacks(collective):
    creditors = []
    debtors = []
    paybacks = []

    members = collective.members
    numBaseMembers = len(members)

    purchases = collective.purchases
    prices = [float(purchase.price.amount) for purchase in purchases]
    overall_purchased = sum(prices)
    eachBaseMember_must_pay = float(overall_purchased) / float(numBaseMembers)
    member_to_balance = {}
    for member in collective.members:
        member_purchased = sum([
            float(purchase.price.amount) for purchase in purchases
            if purchase.buyer == member
        ])
        balance = float(member_purchased) - eachBaseMember_must_pay
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
        if debtor.balance == 0:
            continue
        for creditor in creditors:
            if creditor.balance == 0:
                continue
            payback = debtor.pay_debt_to(creditor)
            paybacks.append(payback)

    return paybacks
