# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from payshare.purchases.models import Collective
from payshare.purchases.serializers import CollectiveSerializer


CANNOT_ADD_ZERO_MONEY = "The amount of money must be larger than zero"


def is_collective_password_correct(view):
    def wrapper(request, collective_key, *args, **kwargs):
        password = get_authorization_header(request)
        collective = Collective.objects.get(key=collective_key)
        if not collective.check_password(password):
            raise AuthenticationFailed
        response = view(request, collective_key, *args, **kwargs)
        return response
    return wrapper


@api_view(("GET",))
@is_collective_password_correct
def collective(request, collective_key):
    collective = Collective.objects.get(key=collective_key)
    serialized_collective = CollectiveSerializer(collective).data
    return Response(serialized_collective)


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
