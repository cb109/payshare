from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from payshare.purchases import api
from payshare.purchases import views


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api-auth/", include("rest_framework.urls",
                               namespace="rest_framework")),
    url(r"^(?P<uuid>[a-f0-9-]{36})/$", views.app, name="app"),

    path("api/v1/<uuid:key>", api.collective),
    path("api/v1/<uuid:key>/cashup", api.cashup),
    path("api/v1/<uuid:key>/liquidation", api.create_liquidation),
    path("api/v1/<uuid:key>/liquidation/<int:pk>", api.LiquidationDetailView.as_view()),  # noqa
    path("api/v1/<uuid:key>/purchase", api.create_purchase),
    path("api/v1/<uuid:key>/purchase/<int:pk>", api.PurchaseDetailView.as_view()),  # noqa
    path("api/v1/<uuid:key>/reaction", api.create_reaction),
    path("api/v1/<uuid:key>/reaction/<int:pk>", api.delete_reaction),
    path("api/v1/<uuid:key>/stats", api.financial_stats),
    path("api/v1/<uuid:key>/transfers", api.TransfersViewSet.as_view({'get': 'list'})),  # noqa
    path("api/v1/version", api.version),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
