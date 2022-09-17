# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db.models import Q
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
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ViewSet

from payshare.purchases.calc import calc_paybacks
from payshare.purchases.models import Collective, PurchaseWeight
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase
from payshare.purchases.models import Reaction
from payshare.purchases.serializers import CollectiveSerializer
from payshare.purchases.serializers import LiquidationSerializer
from payshare.purchases.serializers import PurchaseSerializer
from payshare.purchases.serializers import ReactionSerializer
from payshare.purchases.serializers import TransferSerializer

USER_MUST_BE_MEMBER = "User must be member of Collective"
CANNOT_ADD_ZERO_MONEY = "The amount of money must not be zero"


def key_from_resolvermatch(resolver_match):
    return resolver_match.kwargs["key"]


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
        key = key_from_resolvermatch(request._request.resolver_match)

        collective = collective_from_key(key)
        if not (
            str(collective.token) == possible_token
            or collective.check_password(token_or_password)
        ):
            raise AuthenticationFailed

        # Since we don't deal with Users here, just return None for "success".
        return (None, None)


@api_view(("GET",))
@authentication_classes((HeaderAuthentication,))
def collective(request, key):
    collective = collective_from_key(key)
    serialized_collective = CollectiveSerializer(
        collective, context={"request": request}
    ).data
    return Response(serialized_collective)


@api_view(("GET",))
def version(request):
    """Return current payshare backend version (!= API version)."""
    from payshare import __version__  # noqa

    return Response(__version__)


class TransfersPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        response = super(TransfersPagination, self).get_paginated_response(data)
        response.data["num_pages"] = self.page.paginator.num_pages
        return response


class TransfersViewSet(ListModelMixin, GenericViewSet):
    """Return sorted Purchases and Liquidations for a Collective.

    URL Args:
        key (str): Collective key

    GET Args:
        search (str): Optional search text. Is matched against name
            and usernames of transfers (case insensitive).

    Returns:
        list[Purchase|Liquidation]

    """

    authentication_classes = (HeaderAuthentication,)
    pagination_class = TransfersPagination
    serializer_class = TransferSerializer

    def get_queryset(self):
        key = self.kwargs["key"]
        collective = collective_from_key(key)

        purchase_query = Q(deleted=False)
        liquidation_query = Q(deleted=False)

        search_text = self.request.query_params.get("search")
        if search_text is not None:
            purchase_query = purchase_query & Q(
                Q(name__icontains=search_text)
                | Q(buyer__username__icontains=search_text)
            )
            liquidation_query = liquidation_query & Q(
                Q(name__icontains=search_text)
                | Q(debtor__username__icontains=search_text)
                | Q(creditor__username__icontains=search_text)
            )

        purchases = collective.purchase_set.filter(purchase_query)
        liquidations = collective.liquidation_set.filter(liquidation_query)

        transfers = list(purchases) + list(liquidations)
        transfers.sort(key=lambda obj: obj.created_at, reverse=True)
        return transfers


def _raise_if_wrong_amount(amount):
    if amount == 0:
        raise ValidationError(CANNOT_ADD_ZERO_MONEY)


@api_view(("POST",))
@authentication_classes((HeaderAuthentication,))
def create_purchase(request, key):
    """Create a new Purchase and return it in a serialized representation.

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
    _raise_if_wrong_amount(price_value)
    price = Money(price_value, EUR)

    purchase = Purchase.objects.create(
        name=name,
        price=price,
        collective=collective,
        buyer=buyer,
    )
    serialized_purchase = PurchaseSerializer(purchase).data
    return Response(serialized_purchase)


class PurchaseDetailView(APIView):
    authentication_classes = (HeaderAuthentication,)

    def put(self, request, key, pk):
        """Update a Purchase and return it serialized.

        URL Args:
            key (str): Collective key
            pk (int) Purchase ID

        POST Args:
            name (str)
            buyer (int): User id
            price (float)

        Returns:
            Serialized Purchase

        """
        collective = collective_from_key(key)

        buyer = User.objects.get(id=request.data["buyer"])
        if not collective.is_member(buyer):
            raise ValidationError(USER_MUST_BE_MEMBER)

        price_value = float(request.data["price"])
        _raise_if_wrong_amount(price_value)
        price = Money(price_value, EUR)
        weights = request.data.get("weights", None)

        purchase = Purchase.objects.get(pk=pk)

        # Handle different weights per Member.
        if weights is None:
            purchase.weights.clear()
        else:
            # Remove weights that are all even, which removes their purpose.
            all_same = (
                len(set([serialized_weight["weight"] for serialized_weight in weights]))
                == 1
            )
            if all_same:
                purchase.weights.clear()
            else:
                for serialized_weight in weights:
                    member_id = serialized_weight["member"]
                    member = User.objects.get(id=member_id)
                    weight_value = serialized_weight["weight"]
                    try:
                        weight_instance = PurchaseWeight.objects.get(
                            purchase=purchase, member=member
                        )
                        weight_instance.weight = weight_value
                        weight_instance.save()
                    except PurchaseWeight.DoesNotExist:
                        weight_instance = PurchaseWeight.objects.create(
                            purchase=purchase, member=member, weight=weight_value
                        )

        purchase.name = request.data["name"]
        purchase.price = price
        purchase.buyer = buyer
        purchase.save()

        serialized_purchase = PurchaseSerializer(purchase).data
        return Response(serialized_purchase)

    def delete(self, request, key, pk):
        """Softdeletes given Purchase.

        URL Args:
            key (str): Collective key
            pk (int)

        """
        collective = collective_from_key(key)
        purchase = Purchase.objects.get(pk=pk)
        if not purchase.collective.id == collective.id:
            raise ValidationError("Purchase to delete is not from given Collective")

        purchase.deleted = True
        purchase.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(("POST",))
@authentication_classes((HeaderAuthentication,))
def create_liquidation(request, key):
    """Create a new Liquidation and return it in a serialized representation.

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
    _raise_if_wrong_amount(amount_value)
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


class LiquidationDetailView(APIView):
    authentication_classes = (HeaderAuthentication,)

    def put(self, request, key, pk):
        """Update a new Liquidation.

        URL Args:
            key (str): Collective key
            pk (int): Liquidation ID

        POST Args:
            name (str)
            creditor (int): User id
            debtor (int): User id
            amount (float)

        Returns:
            Serialized Liquidation

        """
        creditor_id = request.data["creditor"]
        debtor_id = request.data["debtor"]

        collective = collective_from_key(key)

        creditor = User.objects.get(id=creditor_id)
        if not collective.is_member(creditor):
            raise ValidationError(USER_MUST_BE_MEMBER)

        debtor = User.objects.get(id=debtor_id)
        if not collective.is_member(debtor):
            raise ValidationError(USER_MUST_BE_MEMBER)

        amount_value = float(request.data["amount"])
        _raise_if_wrong_amount(amount_value)
        amount = Money(amount_value, EUR)

        liquidation = Liquidation.objects.get(pk=pk)
        liquidation.name = request.data["name"]
        liquidation.debtor = debtor
        liquidation.creditor = creditor
        liquidation.amount = amount
        liquidation.save()

        serialized_liquidation = LiquidationSerializer(liquidation).data
        return Response(serialized_liquidation)

    def delete(self, request, key, pk):
        """Softdeletes given Liquidation.

        URL Args:
            key (str): Collective key
            pk (int)

        """
        collective = collective_from_key(key)
        liquidation = Liquidation.objects.get(pk=pk)
        if not liquidation.collective.id == collective.id:
            raise ValidationError("Liquidation to delete is not from given Collective")

        liquidation.deleted = True
        liquidation.save()
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


class ReactionViewSet(ViewSet):
    authentication_classes = (HeaderAuthentication,)

    def create(self, request, key):
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
            raise ValidationError("Object to react to is not from given Collective")

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
        reaction = Reaction.objects.create(
            member=member, meaning=meaning, content_object=transfer
        )

        serialized_reaction = ReactionSerializer(reaction).data
        return Response(serialized_reaction)

    def destroy(self, request, key, pk):
        """Remove a Reaction.

        URL Args:
            key (str): Collective key
            pk (int): Reaction ID

        """
        collective = collective_from_key(key)

        reaction_id = pk
        reaction = Reaction.objects.get(
            id=reaction_id, member__membership__collective=collective
        )
        reaction.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


create_reaction = ReactionViewSet.as_view({"post": "create"})
delete_reaction = ReactionViewSet.as_view({"delete": "destroy"})
