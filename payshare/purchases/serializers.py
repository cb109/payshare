from moneyed import Money
from rest_framework import serializers

from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase


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
    kind = serializers.SerializerMethodField()
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

    def get_kind(self, obj):
        return "liquidation"


class PurchaseSerializer(serializers.ModelSerializer):
    kind = serializers.SerializerMethodField()
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

    def get_kind(self, obj):
        return "purchase"
