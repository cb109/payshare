"""payshare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from payshare.purchases import views


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api-auth/", include("rest_framework.urls",
                               namespace="rest_framework")),

    url(r"^api/v1/transfers/(?P<collective_id>[0-9]+)$", views.list_transfers_for_collective),  # noqa

    url(r"^purchase/create/$", views.purchase_create, name="purchase-create"),
    url(r"^purchase/delete/(?P<pk>[0-9]+)/$", views.purchase_delete,
        name="purchase-delete"),

    url(r"^liquidation/create/$", views.liquidation_create,
        name="liquidation-create"),
    url(r"^liquidation/delete/(?P<pk>[0-9]+)/$", views.liquidation_delete,
        name="liquidation-delete"),

    url(r"^(?P<uuid>[a-f0-9-]{36})/$", views.index, name="index"),
]
