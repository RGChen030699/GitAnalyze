"""URL configuration for GitAnalyze."""

from django.contrib import admin
from django.urls import include, path
from rankings.views import RankingsView
from repositories.views import RepositoryDetailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/rankings", RankingsView.as_view(), name="rankings"),
    path("api/repos/<str:owner>/<str:name>", RepositoryDetailView.as_view(), name="repo-detail"),
    path("", include("config.dev_frontend")),  # local development only; 404 unless DEBUG
]
