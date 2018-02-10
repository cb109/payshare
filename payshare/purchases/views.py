# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from moneyed import Money, EUR

from payshare.purchases.models import Collective
from payshare.purchases.models import Purchase
from payshare.purchases.models import Liquidation
from payshare.purchases.serializers import CollectiveSerializer
from payshare.purchases.serializers import LiquidationSerializer
from payshare.purchases.serializers import PurchaseSerializer


CANNOT_ADD_ZERO_MONEY = "The amount of money must be larger than zero"


def index(request, uuid):
    """TODO: This view does way too many things. Login, logout, content
    view etc. please refactor!
    """
    from pprint import pprint
    pprint(request.POST)
    try:
        collective = Collective.objects.get(key=uuid)
    except (Collective.DoesNotExist, ValidationError):
        return HttpResponse("This does not exist :(", status=404)

    collective_url = request.build_absolute_uri(request.get_full_path())

    logout = request.POST.get("logout", None)
    if logout is not None:
        request.session.flush()
        return render(request, "index.html", {
            "authenticated": False,
            "collective": collective,
            "next": collective_url,
        })

    members = [ms.member for ms in collective.membership_set.all()]
    members = sorted(members, key=lambda m: m.username)

    if not request.user.is_authenticated():
        password = request.POST.get("password", None)
        if password is not None:
            if not check_password(password, collective.password):
                return render(request, "index.html", {
                    "wrong_password": True,
                    "authenticated": False,
                    "collective": collective,
                    "next": collective_url,
                })
            else:
                # This will set a session id cookie which we can use to
                # authenticate subsequent requests for convience. The
                # member we choose is not important here, we just want
                # to make use of the builtin User authentication system
                # for now.
                first_member = members[0]
                login(request, first_member)

    purchases = []
    for member in members:
        purchases.extend(Purchase.objects.filter(collective=collective,
                                                 buyer=member,
                                                 deleted=False))
    liquidations = list(Liquidation.objects.filter(collective=collective,
                                                   deleted=False))

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
        "authenticated": request.user.is_authenticated(),
        "collective": collective,
        "next": collective_url,
        "members": members,
        "transactions": transactions,
        "overall_purchased": overall_purchased,
        "member_summary": member_summary,
    })


# def login_and_redirect(request):
#     print request.POST
#     return render(request, "index.html", {
#         "authenticated": True,
#     })


def get_collective_url(collective):
    collective_url = "/{}".format(collective.key)
    return collective_url


def purchase_create(request):
    name = request.POST["name"]

    collective_id = request.POST["collective"][0]
    collective = Collective.objects.get(id=collective_id)

    buyer_id = request.POST["buyer"][0]
    buyer = User.objects.get(id=buyer_id)

    # FIXME: Either don't allow something else than euro or handle here.
    price_value = float(request.POST["price_0"])
    if price_value <= 0:
        raise ValueError(CANNOT_ADD_ZERO_MONEY)
    price = Money(price_value, EUR)

    Purchase.objects.create(
        name=name,
        price=price,
        collective=collective,
        buyer=buyer,
    )

    return redirect(get_collective_url(collective))


def liquidation_create(request):
    description = request.POST["description"]

    collective_id = request.POST["collective"][0]
    collective = Collective.objects.get(id=collective_id)

    debtor_id = request.POST["debtor"][0]
    debtor = User.objects.get(id=debtor_id)

    creditor_id = request.POST["creditor"][0]
    creditor = User.objects.get(id=creditor_id)

    # FIXME: Either don't allow something else than euro or handle here.
    amount_value = float(request.POST["amount_0"])
    if amount_value <= 0:
        raise ValueError(CANNOT_ADD_ZERO_MONEY)
    amount = Money(amount_value, EUR)

    Liquidation.objects.create(
        description=description,
        amount=amount,
        debtor=debtor,
        creditor=creditor,
        collective=collective,
    )

    return redirect(get_collective_url(collective))


def purchase_delete(request, pk):
    purchase = Purchase.objects.get(pk=pk)
    collective_id = int(request.POST["collective"])
    if not purchase.collective.id == collective_id:
        return HttpResponse(status=403)

    purchase.delete()

    return redirect(get_collective_url(purchase.collective))


def liquidation_delete(request, pk):
    liquidation = Liquidation.objects.get(pk=pk)
    collective_id = int(request.POST["collective"])
    if not liquidation.collective.id == collective_id:
        return HttpResponse(status=403)

    liquidation.delete()

    return redirect(get_collective_url(liquidation.collective))
