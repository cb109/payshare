from django.contrib.auth.models import User
from moneyed import Money
from rest_framework import serializers

from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "avatar",
            "first_name",
            "full_name",
            "id",
            "last_name",
            "username",
        )

    def get_avatar(self, user):
        return user.profile.avatar_image_url

    def get_full_name(self, user):
        return user.get_full_name()


class CollectiveSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Collective
        fields = (
            "id",
            "name",
            "key",
            "token",
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


class TransferSerializer(serializers.Serializer):
    """Accept both Purchase and Liquidation and delegate."""

    def to_representation(self, instance):
        if instance.__class__ == Purchase:
            return PurchaseSerializer(instance).data
        elif instance.__class__ == Liquidation:
            return LiquidationSerializer(instance).data
        raise ValueError("Cannot serialize this thing: {}".format(instance))
