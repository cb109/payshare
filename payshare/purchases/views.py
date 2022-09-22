from django.conf import settings
from django.shortcuts import render


def app(request, uuid):
    """Dehydrate the Vue app from its dist folder.

    Args:
        uuid (uuid): Collective key, simply passed through.

    """
    return render(request, settings.CLIENT_APP_TEMPLATE)
