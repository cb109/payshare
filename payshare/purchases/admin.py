# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Membership
from payshare.purchases.models import Purchase
from payshare.purchases.models import UserProfile


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
    )
    list_editable = (
        "first_name",
        "last_name",
        "username",
        "email",
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "avatar_image_url_link",
        "id",
    )

    def avatar_image_url_link(self, obj):
        template = '''
            <image src="{0}"
                   style="max-width: 200px; max-height: 200px"/>
        '''
        html = template.format(obj.avatar_image_url)
        return mark_safe(html)


class CollectiveAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = ("name", "key", "password", "id",)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ["name", "deleted", "price", "buyer", "id", "collective"]


class LiquidationAdmin(admin.ModelAdmin):
    list_display = ["name", "deleted", "amount", "creditor", "debtor",
                    "id", "collective"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Collective, CollectiveAdmin)
admin.site.register(Membership)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Liquidation)
