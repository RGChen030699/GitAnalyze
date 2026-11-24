"""Repository page endpoint (F1 L4)."""

from django.utils import timezone
from github_client import GitHubClient
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from repositories.fetch import get_or_fetch
from repositories.serializers import serialize_detail


class RepositoryDetailView(APIView):
    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request, owner: str, name: str) -> Response:
        client = GitHubClient(clock=timezone.now, wait_for_rate_limit=False)
        repo = get_or_fetch(client, owner, name, timezone.now())
        return Response(serialize_detail(repo))
