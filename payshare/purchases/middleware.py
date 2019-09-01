import logging

from django.urls.base import resolve

from payshare.purchases import api
from payshare.purchases.models import CollectiveReadOnlyError

logger = logging.getLogger(__name__)


def debugging_middleware(get_response):

    def middleware(request):
        from pprint import pprint
        pprint(dict(request.META))

        response = get_response(request)
        return response

    return middleware


def readonly_middleware(get_response):
    """Reject all requests that may change data when Collective is readonly.

    This middleware must come after the AuthenticationMiddleware so we
    can identify the Collective.

    """
    def middleware(request):
        if request.method not in ("GET", "OPTIONS"):

            resolver_match = resolve(request.path)
            key = api.key_from_resolvermatch(resolver_match)
            collective = api.collective_from_key(key)

            if collective.readonly:
                raise CollectiveReadOnlyError(collective)

        response = get_response(request)
        return response

    return middleware
