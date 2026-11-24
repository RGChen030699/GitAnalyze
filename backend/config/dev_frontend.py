"""Serve frontend/ from Django in local development, so pages and /api/ share one origin.

The routes mirror frontend/vercel.json. In production Vercel serves the pages, and these views
answer 404 because DEBUG is off.
"""

from collections.abc import Callable
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import URLPattern, path, re_path
from django.views.static import serve

FRONTEND_DIR = Path(settings.BASE_DIR).parent / "frontend"
ASSET_PATTERN = r"^(?P<name>[A-Za-z0-9_-]+\.(?:js|css))$"


def _serve(request: HttpRequest, name: str) -> HttpResponse:
    if not settings.DEBUG:
        raise Http404("The frontend is served by Vercel outside local development")
    return serve(request, name, document_root=str(FRONTEND_DIR))


def _page(name: str) -> Callable[..., HttpResponse]:
    def view(request: HttpRequest, **_: str) -> HttpResponse:
        return _serve(request, name)

    return view


def _asset(request: HttpRequest, name: str) -> HttpResponse:
    return _serve(request, name)


urlpatterns: list[URLPattern] = [
    path("", _page("index.html")),
    path("repo/<str:owner>/<str:name>", _page("repo.html")),
    path("compare", _page("compare.html")),
    path("about", _page("about.html")),
    path("about/<str:section>", _page("about.html")),
    re_path(ASSET_PATTERN, _asset),
]
