# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from payshare.purchases.models import Collective
from payshare.purchases.models import Membership
from payshare.purchases.models import Purchase
from payshare.purchases.models import Liquidation


class CollectiveAdmin(admin.ModelAdmin):
    readonly_fields = ["key"]


admin.site.register(Collective, CollectiveAdmin)
admin.site.register(Membership)
admin.site.register(Purchase)
admin.site.register(Liquidation)
