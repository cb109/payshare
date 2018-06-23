import logging

logger = logging.getLogger(__name__)


def debugging_middleware(get_response):

    def middleware(request):
        from pprint import pprint
        pprint(dict(request.META))

        response = get_response(request)
        return response

    return middleware
