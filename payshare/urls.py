from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from payshare.purchases import api
from payshare.purchases import views


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api-auth/", include("rest_framework.urls",
                               namespace="rest_framework")),

    url(r"^(?P<uuid>[a-f0-9-]{36})/$", views.app, name="app"),

    path(r"api/v1/version", api.version),
    path(r"api/v1/<uuid:key>", api.collective),
    path(r"api/v1/<uuid:key>/stats", api.financial_stats),
    path(r"api/v1/<uuid:key>/transfers", api.TransfersViewSet.as_view({'get': 'list'})),  # noqa
    path(r"api/v1/<uuid:key>/purchase", api.create_purchase),
    path(r"api/v1/<uuid:key>/liquidation", api.create_liquidation),
    path(r"api/v1/<uuid:key>/reaction", api.create_reaction),
    path(r"api/v1/<uuid:key>/<str:kind>/<int:pk>", api.softdelete_transfer),
]
