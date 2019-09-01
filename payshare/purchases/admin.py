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
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_editable = (
        "username",
        "email",
        "first_name",
        "last_name",
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "avatar_image_url_link",
        "avatar_image_url",
        "id",
    )

    list_editable = (
        "avatar_image_url",
    )

    def avatar_image_url_link(self, obj):
        template = '''
            <image src="{0}"
                   style="max-width: 200px; max-height: 200px"/>
            <a href="{1}" target="blank_">
                Edit on https://getavataaars.com
            </a>
        '''
        image_url = obj.avatar_image_url
        editor_url = ""
        if image_url.startswith("https://avataaars.io"):
            editor_url = image_url.replace("https://avataaars.io",
                                           "https://getavataaars.com")
        html = template.format(image_url, editor_url)
        return mark_safe(html)


class CollectiveAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)
    list_display = (
        "name",
        "key",
        "password",
        "currency_symbol",
        "readonly",
        "id",
    )


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
