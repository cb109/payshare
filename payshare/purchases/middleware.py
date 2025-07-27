import logging

from django.urls.base import resolve

from payshare.purchases import api
from payshare.purchases.models import Collective
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
    """Reject all requests that may change data when Collective is readonly."""
    def middleware(request):
        if request.method not in ("GET", "OPTIONS"):
            try:
                resolver_match = resolve(request.path)
                key = api.key_from_resolvermatch(resolver_match)
                collective = api.collective_from_key(key)
                if collective.readonly:
                    raise CollectiveReadOnlyError(collective)
            except (KeyError, Collective.DoesNotExist):
                pass

        response = get_response(request)
        return response

    return middleware
