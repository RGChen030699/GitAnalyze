"""URL configuration for GitAnalyze."""

from django.contrib import admin
from django.urls import path
from rankings.views import RankingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/rankings", RankingsView.as_view(), name="rankings"),
]
