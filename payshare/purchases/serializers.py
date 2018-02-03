from rest_framework import serializers

from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Purchase


class CollectiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collective
        fields = "__all__"


class LiquidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Liquidation
        fields = "__all__"


class PurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = "__all__"
