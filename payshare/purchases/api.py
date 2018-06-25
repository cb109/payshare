# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from moneyed import Money, EUR

from rest_framework import authentication
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payshare.purchases.calc import calc_paybacks
from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase
from payshare.purchases.models import Reaction
from payshare.purchases.serializers import CollectiveSerializer
from payshare.purchases.serializers import LiquidationSerializer
from payshare.purchases.serializers import PurchaseSerializer
from payshare.purchases.serializers import ReactionSerializer
from payshare.purchases.serializers import TransferSerializer


USER_MUST_BE_MEMBER = "User must be member of Collective"
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


@api_view(("GET",))
def version(request):
    """Return current payshare backend version (!= API version)."""
    from payshare import __version__  # noqa
    return Response(__version__)


class TransfersPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        response = super(TransfersPagination,
                         self).get_paginated_response(data)
        response.data["num_pages"] = self.page.paginator.num_pages
        return response


class TransfersViewSet(ListModelMixin, GenericViewSet):
    """Return sorted Purchases and Liquidations for a Collective."""
    authentication_classes = (HeaderAuthentication,)
    pagination_class = TransfersPagination
    serializer_class = TransferSerializer

    def get_queryset(self):
        key = self.kwargs["key"]
        collective = collective_from_key(key)
        transfers = (
            list(collective.purchase_set.filter(deleted=False)) +
            list(collective.liquidation_set.filter(deleted=False))
        )
        transfers.sort(key=lambda obj: obj.created_at, reverse=True)
        return transfers


@api_view(("POST",))
@authentication_classes((HeaderAuthentication,))
def create_purchase(request, key):
    """Create a new Purchase and return it in a seriailzed representation.

    URL Args:
        key (str): Collective key

    POST Args:
        name (str)
        buyer (int): User id
        price (float)

    Returns:
        Serialized Purchase

    """
    name = request.data["name"]
    buyer_id = request.data["buyer"]

    collective = collective_from_key(key)

    buyer = User.objects.get(id=buyer_id)
    if not collective.is_member(buyer):
        raise ValidationError(USER_MUST_BE_MEMBER)

    # FIXME: Either don't allow something else than euro or handle here.
    price_value = float(request.data["price"])
    if price_value <= 0:
        raise ValidationError(CANNOT_ADD_ZERO_MONEY)
    price = Money(price_value, EUR)

    purchase = Purchase.objects.create(
        name=name,
        price=price,
        collective=collective,
        buyer=buyer,
    )
    serialized_purchase = PurchaseSerializer(purchase).data
    return Response(serialized_purchase)


@api_view(("POST",))
@authentication_classes((HeaderAuthentication,))
def create_liquidation(request, key):
    """Create a new Liquidation and return it in a seriailzed representation.

    URL Args:
        key (str): Collective key

    POST Args:
        name (str)
        creditor (int): User id
        debtor (int): User id
        amount (float)

    Returns:
        Serialized Liquidation

    """
    name = request.data["name"]
    creditor_id = request.data["creditor"]
    debtor_id = request.data["debtor"]

    collective = collective_from_key(key)

    creditor = User.objects.get(id=creditor_id)
    if not collective.is_member(creditor):
        raise ValidationError(USER_MUST_BE_MEMBER)

    debtor = User.objects.get(id=debtor_id)
    if not collective.is_member(debtor):
        raise ValidationError(USER_MUST_BE_MEMBER)

    # FIXME: Either don't allow something else than euro or handle here.
    amount_value = float(request.data["amount"])
    if amount_value <= 0:
        raise ValidationError(CANNOT_ADD_ZERO_MONEY)
    amount = Money(amount_value, EUR)

    liquidation = Liquidation.objects.create(
        name=name,
        amount=amount,
        collective=collective,
        creditor=creditor,
        debtor=debtor,
    )
    serialized_liquidation = LiquidationSerializer(liquidation).data
    return Response(serialized_liquidation)


@api_view(("DELETE",))
@authentication_classes((HeaderAuthentication,))
def softdelete_transfer(request, key, kind, pk):
    """Softdeletes given Purchase or Liquidation.

    URL Args:
        key (str): Collective key
        kind (str): 'purchase' or 'liquidation'
        pk (int)

    """
    collective = collective_from_key(key)

    if kind == "purchase":
        cls = Purchase
    elif kind == "liquidation":
        cls = Liquidation

    transfer = cls.objects.get(pk=pk)
    if not transfer.collective.id == collective.id:
        raise ValidationError("Object to delete is not from given Collective")

    transfer.deleted = True
    transfer.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(("GET",))
@authentication_classes((HeaderAuthentication,))
def financial_stats(request, key):
    collective = collective_from_key(key)
    return Response(collective.stats)


@api_view(("GET",))
@authentication_classes((HeaderAuthentication,))
def cashup(request, key):
    collective = collective_from_key(key)
    paybacks = [payback.to_json() for payback in calc_paybacks(collective)]
    return Response(paybacks)


@api_view(("POST",))
@authentication_classes((HeaderAuthentication,))
def create_reaction(request, key):
    """Create a Member Reaction to a Purchase or Liquidation.

    If the User already reacted before, that Reaction is replaced by the
    new one (e.g. if he changed his mind).

    URL Args:
        key (str): Collective key

    POST Args:
        transfer_kind (str): 'purchase' or 'liquidation'
        transfer_id (int): Purchase or Liquidation ID
        meaning (str): One of Reaction.available_meanings
        member (int): User ID

    """
    collective = collective_from_key(key)

    transfer_kind = request.data["transfer_kind"]
    if transfer_kind == "purchase":
        cls = Purchase
    elif transfer_kind == "liquidation":
        cls = Liquidation

    transfer_id = request.data["transfer_id"]
    transfer = cls.objects.get(id=transfer_id)
    if not transfer.collective.id == collective.id:
        raise ValidationError(
            "Object to react to is not from given Collective")

    member_id = request.data["member"]
    member = User.objects.get(id=member_id)
    if member not in collective.members:
        raise ValidationError("Can only react as member of the Collective")

    meaning = request.data["meaning"]
    if meaning not in Reaction.get_available_meanings():
        raise ValidationError("Unknown meaning: {}".format(meaning))

    # Replace existing Reaction, if there is one.
    try:
        old_reaction = transfer.reactions.get(member=member)
        old_reaction.delete()
    except Reaction.DoesNotExist:
        pass
    reaction = Reaction.objects.create(member=member,
                                       meaning=meaning,
                                       content_object=transfer)

    serialized_reaction = ReactionSerializer(reaction).data
    return Response(serialized_reaction)
