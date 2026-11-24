"""Allow the configured frontend origin to read the JSON API."""

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_vary_headers

API_PREFIX = "/api/"
ALLOWED_METHODS = "GET, OPTIONS"


def _is_preflight(request: HttpRequest) -> bool:
    return request.method == "OPTIONS" and "Access-Control-Request-Method" in request.headers


class FrontendCorsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.path.startswith(API_PREFIX):
            return self.get_response(request)
        allowed = request.headers.get("Origin") == settings.FRONTEND_ORIGIN
        if allowed and _is_preflight(request):
            response = HttpResponse(status=204)
            response["Access-Control-Allow-Methods"] = ALLOWED_METHODS
        else:
            response = self.get_response(request)
        patch_vary_headers(response, ["Origin"])
        if allowed:
            response["Access-Control-Allow-Origin"] = settings.FRONTEND_ORIGIN
        return response
