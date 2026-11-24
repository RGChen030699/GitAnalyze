"""Repository page endpoint (F1 L4)."""

from django.utils import timezone
from github_client import GitHubClient
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from repositories.fetch import RepoNotFound, get_or_fetch
from repositories.serializers import serialize_detail


class RepositoryDetailView(APIView):
    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request, owner: str, name: str) -> Response:
        client = GitHubClient(clock=timezone.now, wait_for_rate_limit=False)
        now = timezone.now()
        try:
            repo = get_or_fetch(client, owner, name, now)
        except RepoNotFound as error:
            return Response({"detail": str(error)}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_detail(repo, now))
