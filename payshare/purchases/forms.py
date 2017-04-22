from django import forms

from payshare.purchases.models import Purchase
from payshare.purchases.models import Liquidation


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["name", "price", "buyer", "collective"]


class LiquidationForm(forms.ModelForm):
    class Meta:
        model = Liquidation
        fields = ["amount", "debtor", "creditor", "collective"]
