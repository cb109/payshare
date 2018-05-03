# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from payshare.purchases.models import Collective
from payshare.purchases.serializers import CollectiveSerializer
from payshare.purchases.serializers import PurchaseSerializer
from payshare.purchases.serializers import LiquidationSerializer


CANNOT_ADD_ZERO_MONEY = "The amount of money must be larger than zero"


def collective_from_key(key):
    return Collective.objects.get(key=key)


def header_authentication(view):
    def wrapper(request, key, *args, **kwargs):
        password = get_authorization_header(request)
        collective = collective_from_key(key)
        if not collective.check_password(password):
            raise AuthenticationFailed
        response = view(request, key, *args, **kwargs)
        return response
    return wrapper


@api_view(("GET",))
@header_authentication
def collective(request, key):
    collective = collective_from_key(key)
    serialized_collective = CollectiveSerializer(collective).data
    return Response(serialized_collective)


@api_view(("GET",))
@header_authentication
def transfers(request, key):
    collective = collective_from_key(key)
    serialized_purchases = PurchaseSerializer(
        collective.purchase_set.all(),
        many=True).data
    serialized_liquidations = LiquidationSerializer(
        collective.liquidation_set.all(),
        many=True).data
    transfers = serialized_purchases + serialized_liquidations
    transfers.sort(key=lambda obj: obj["created_at"], reverse=True)
    return Response(transfers)


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
