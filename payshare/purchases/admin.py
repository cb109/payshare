from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe

from payshare.purchases.models import Collective
from payshare.purchases.models import Liquidation
from payshare.purchases.models import Membership
from payshare.purchases.models import Purchase
from payshare.purchases.models import PurchaseWeight
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
    search_fields = ("username", "first_name", "last_name", "email", "id")


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "avatar_image_url_link",
        "avatar_image_url",
        "paypal_me_username",
        "id",
    )
    autocomplete_fields = ("user",)
    list_editable = ("avatar_image_url",)

    def avatar_image_url_link(self, profile):
        image_url = profile.avatar_image_url
        editor_url = ""
        is_avataaars_url = image_url.startswith("https://avataaars.io")
        if is_avataaars_url:
            editor_url = image_url.replace(
                "https://avataaars.io", "https://getavataaars.com"
            )
        template = """
            <image src="{0}"
                   style="max-width: 200px; max-height: 200px"/>
        """
        if is_avataaars_url:
            template += """
                <a href="{1}" target="blank_">
                    Edit on https://getavataaars.com
                </a>
            """
            html = template.format(image_url, editor_url)
        else:
            html = template.format(image_url)
        return mark_safe(html)


class CollectiveAdmin(admin.ModelAdmin):
    class MembershipInline(admin.TabularInline):
        model = Membership
        autocomplete_fields = ("member",)

        def get_queryset(self, request):
            return (
                super()
                .get_queryset(request)
                .order_by(
                    "member__first_name",
                    "member__last_name",
                )
            )

    inlines = (MembershipInline,)

    readonly_fields = ("key",)
    list_display = (
        "name",
        "url",
        "created_at",
        "readonly",
        "currency_symbol",
        "id",
    )
    search_fields = ("name", "id")

    @mark_safe
    def url(self, collective):
        url = reverse("app", args=[collective.key])
        return f"<a href='{url}'>Visit in App: {collective.name}</a>"


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ["name", "active", "price", "buyer", "id", "collective"]
    list_filter = ("collective",)
    autocomplete_fields = ("buyer", "collective")
    search_fields = ("name", "collective__name")

    def active(self, purchase):
        return not purchase.deleted

    active.boolean = True


class PurchaseWeightAdmin(admin.ModelAdmin):
    list_display = ["purchase", "member", "weight", "id"]
    autocomplete_fields = ("purchase", "member")


class LiquidationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "active",
        "amount",
        "creditor",
        "debtor",
        "id",
        "collective",
    ]
    list_filter = ("collective",)
    autocomplete_fields = ("creditor", "debtor", "collective")

    def active(self, liquidation):
        return not liquidation.deleted

    active.boolean = True


class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        "collective",
        "member",
        "created_at",
        "id",
    ]
    list_filter = ("collective",)
    autocomplete_fields = ("member", "collective")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Collective, CollectiveAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchaseWeight, PurchaseWeightAdmin)
admin.site.register(Liquidation, LiquidationAdmin)
