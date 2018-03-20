# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.contrib.auth import login
# from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User

# from moneyed import Money, EUR
# from rest_framework import mixins
# from rest_framework import viewsets
# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAdminUser
# from rest_framework.response import Response

from payshare.purchases.models import Collective
# from payshare.purchases.models import Liquidation
# from payshare.purchases.models import Purchase
# from payshare.purchases.serializers import LiquidationSerializer
# from payshare.purchases.serializers import PurchaseSerializer


CANNOT_ADD_ZERO_MONEY = "The amount of money must be larger than zero"


def collective(request, collective_key):
    collective = Collective.objects.get(key=collective_key)
    return collective


# def transfers(request):
#     """Paginated list of Purchases and Liquidations for a Collective."""
#     pass


# class PurchasesView(mixins.CreateModelMixin,
#                     mixins.RetrieveModelMixin,
#                     viewsets.GenericViewSet):
#     serializer_class = PurchaseSerializer

#     def get_queryset(self):
#         collective_id = self.request.data["collective"]
#         return Purchase.objects.filter(collective__id=collective_id)


# class LiquidationsView(mixins.CreateModelMixin,
#                        mixins.RetrieveModelMixin,
#                        viewsets.GenericViewSet):
#     serializer_class = LiquidationSerializer

#     def get_queryset(self):
#         collective_id = self.request.data["collective"]
#         return Liquidation.objects.filter(collective__id=collective_id)
