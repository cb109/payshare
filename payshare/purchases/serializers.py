from django.contrib.auth.models import User
from moneyed import Money
from rest_framework import serializers

from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class CollectiveSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Collective
        fields = (
            "id",
            "name",
            "key",
            "members",
        )


class MoneyField(serializers.Field):
    """https://github.com/django-money/django-money/issues/179"""

    def to_representation(self, obj):
        return {
            "amount": "%f" % (obj.amount),
            "currency": "%s" % (obj.currency),
        }

    def to_internal_value(self, data):
        return Money(data["amount"], data["currency"])


class LiquidationSerializer(serializers.ModelSerializer):
    amount = MoneyField()

    class Meta:
        model = Liquidation
        fields = (
            "id",
            "description",
            "amount",
            "debtor",
            "creditor",
            "created_at",
            "modified_at",
            "kind",
        )


class PurchaseSerializer(serializers.ModelSerializer):
    price = MoneyField()

    class Meta:
        model = Purchase
        fields = (
            "id",
            "name",
            "description",
            "price",
            "buyer",
            "created_at",
            "modified_at",
            "kind",
        )
