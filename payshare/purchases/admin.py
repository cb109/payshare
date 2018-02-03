# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from payshare.purchases.models import Collective
from payshare.purchases.models import Membership
from payshare.purchases.models import Purchase
from payshare.purchases.models import Liquidation


class CollectiveAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ("name", "key", "password", "id",)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ["name", "deleted", "price", "buyer", "id", "collective"]


class LiquidationAdmin(admin.ModelAdmin):
    list_display = ["description", "deleted", "amount", "creditor", "debtor",
                    "id", "collective"]


admin.site.register(Collective, CollectiveAdmin)
admin.site.register(Membership)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Liquidation)
