# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.contrib.auth.models import User
from django.shortcuts import render
# from django.http import HttpResponse
# from moneyed import Money, EUR

from payshare.purchases.models import Collective
# from payshare.purchases.models import Purchase
from payshare.purchases.forms import PurchaseForm
from payshare.purchases.forms import LiquidationForm


def index(request):
    collective = Collective.objects.first()
    return render(request, "index.html", {
        "collective": collective,
        "purchase_form": PurchaseForm(initial={"collective": collective}),
        "liquidation_form": LiquidationForm(
            initial={"collective": collective}),
        "purchases": collective.purchase_set.all().order_by("-created_at"),
    })


# def purchase_create(request):
#     # <QueryDict: {u'price_1': [u'EUR'], u'price_0': [u'50'], u'name': [u'551'], u'collective': [u'1'], u'buyer': [u'2'], u'csrfmiddlewaretoken': [u'xLRW08hDiRNGfcm2KMDdnGmQoAToTRY7Wknu99t7VTI2OG0PPo0VJsmwKBAEWg0b']}>

#     from pprint import pprint
#     pprint(dict(request.POST))

#     name = request.POST["name"][0]

#     collective_id = request.POST["collective"][0]
#     collective = Collective.objects.get(collective_id)

#     buyer_id = request.POST["buyer"][0]
#     buyer = User.objects.get(buyer_id)

#     # FIXME: Either don't allow something else than euro or handle here.
#     price_value = request.POST["price_0"][0]
#     price = Money(price_value, EUR)

#     Purchase.objects.create(
#         name=name,
#         price=price,
#         collective=collective,
#         buyer=buyer,
#     )

#     return HttpResponse()
