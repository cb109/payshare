# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import authentication
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payshare.purchases.models import Collective
from payshare.purchases.serializers import CollectiveSerializer
from payshare.purchases.serializers import TransferSerializer


CANNOT_ADD_ZERO_MONEY = "The amount of money must be larger than zero"


def collective_from_key(key):
    return Collective.objects.get(key=key)


class HeaderAuthentication(authentication.BaseAuthentication):
    """Allow authenticating through header using either password or token.

    Header name is 'HTTP_AUTHORIZATION'. Its value is either the raw
    password or a string like 'Token <TOKEN>'.

    """
    def authenticate(self, request):
        token_or_password = get_authorization_header(request).decode("utf-8")
        possible_token = token_or_password.replace("Token ", "")

        # Accessing the URL params of the request is a bit tedious here.
        key = request._request.resolver_match.kwargs["key"]

        collective = collective_from_key(key)
        if not (str(collective.token) == possible_token or
                collective.check_password(token_or_password)):
            raise AuthenticationFailed

        # Since we don't deal with Users here, just return None for "success".
        return (None, None)


@api_view(("GET",))
@authentication_classes((HeaderAuthentication,))
def collective(request, key):
    collective = collective_from_key(key)
    serialized_collective = CollectiveSerializer(collective).data
    return Response(serialized_collective)


class TransfersPagination(PageNumberPagination):
    page_size = 20


class TransfersViewSet(ListModelMixin, GenericViewSet):
    """Return sorted Purchases and Liquidations for a Collective."""
    authentication_classes = (HeaderAuthentication,)
    pagination_class = TransfersPagination
    serializer_class = TransferSerializer

    def get_queryset(self):
        key = self.kwargs["key"]
        collective = collective_from_key(key)
        transfers = (
            list(collective.purchase_set.all()) +
            list(collective.liquidation_set.all())
        )
        transfers.sort(key=lambda obj: obj.created_at, reverse=True)
        return transfers
