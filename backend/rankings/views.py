"""Database-only rankings endpoint (F7)."""

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rankings.queries import ordered_repositories
from rankings.serializers import serialize_row


class RankingsView(APIView):
    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({"results": [serialize_row(repo) for repo in ordered_repositories()]})
