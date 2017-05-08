# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from moneyed import Money, EUR

from payshare.purchases.models import Collective
from payshare.purchases.models import Purchase
from payshare.purchases.models import Liquidation
from payshare.purchases.forms import PurchaseForm
from payshare.purchases.forms import LiquidationForm


def index(request, uuid):
    try:
        collective = Collective.objects.get(key=uuid)
    except (Collective.DoesNotExist, ValidationError):
        return HttpResponse("This does not exist :(", status=404)

    members = [ms.member for ms in collective.membership_set.all()]
    members = sorted(members, key=lambda m: m.username)

    purchases = []
    for member in members:
        purchases.extend(Purchase.objects.filter(collective=collective,
                                                 buyer=member))
    liquidations = list(Liquidation.objects.filter(collective=collective))

    overall_purchased = sum([purchase.price for purchase in purchases])
    per_member = float(overall_purchased) / float(len(members))

    member_summary = {}
    for member in members:
        member_purchased = sum([purchase.price for purchase in purchases
                                if purchase.buyer == member])

        credit = sum([liq.amount for liq in liquidations
                     if liq.creditor == member])
        debt = sum([liq.amount for liq in liquidations
                    if liq.debtor == member])
        has_to_pay = (
            per_member -
            float(member_purchased) -
            float(credit) +
            float(debt)
        )

        balance = has_to_pay * -1
        if balance == 0:  # Remove '-' from the display.
            balance = 0
        member_summary[member] = balance

    transactions = purchases + liquidations
    transactions = sorted(transactions, key=lambda t: t.created_at,
                          reverse=True)
    transactions = [
        ("purchase" if isinstance(t, Purchase) else "liquidation", t)
        for t in transactions
    ]

    return render(request, "index.html", {
        "collective": collective,
        "members": members,
        "transactions": transactions,
        "overall_purchased": overall_purchased,
        "member_summary": member_summary,
        "purchase_form": PurchaseForm(initial={"collective": collective}),
        "liquidation_form": LiquidationForm(
            initial={"collective": collective}),
    })


def purchase_create(request):
    from pprint import pprint
    pprint(request.POST)
    name = request.POST["name"]

    collective_id = request.POST["collective"][0]
    collective = Collective.objects.get(id=collective_id)
    collective_url = "/{}".format(collective.key)

    buyer_id = request.POST["buyer"][0]
    buyer = User.objects.get(id=buyer_id)

    # FIXME: Either don't allow something else than euro or handle here.
    price_value = float(request.POST["price_0"])
    price = Money(price_value, EUR)

    Purchase.objects.create(
        name=name,
        price=price,
        collective=collective,
        buyer=buyer,
    )

    return redirect(collective_url)
