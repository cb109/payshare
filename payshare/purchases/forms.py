from django import forms

from payshare.purchases.models import Collective
from payshare.purchases.models import Membership
from payshare.purchases.models import Purchase


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["name", "description", "price", "buyer", "collective"]
