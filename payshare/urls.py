from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from payshare.purchases import api
from payshare.purchases import views


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api-auth/", include("rest_framework.urls",
                               namespace="rest_framework")),

    path(r"api/v1/<uuid:key>", api.collective),
    path(r"api/v1/<uuid:key>/transfers", api.transfers),

    # url(r"^api/v1/transfers/(?P<collective_id>[0-9]+)$", views.list_transfers_for_collective),  # noqa

    url(r"^purchase/create/$", views.purchase_create, name="purchase-create"),
    url(r"^purchase/delete/(?P<pk>[0-9]+)/$", views.purchase_delete,
        name="purchase-delete"),

    url(r"^liquidation/create/$", views.liquidation_create,
        name="liquidation-create"),
    url(r"^liquidation/delete/(?P<pk>[0-9]+)/$", views.liquidation_delete,
        name="liquidation-delete"),

    url(r"^(?P<uuid>[a-f0-9-]{36})/$", views.index, name="index"),
]
