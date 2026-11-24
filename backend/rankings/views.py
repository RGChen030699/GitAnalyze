"""Database-only rankings endpoint (F7)."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rankings.params import InvalidRankingParams, parse_params
from rankings.queries import coverage, language_counts, ordered_repositories, trending_key
from rankings.serializers import serialize_row


class RankingsView(APIView):
    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        try:
            params = parse_params(request.query_params)
        except InvalidRankingParams as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        repositories = ordered_repositories(params)
        start = (params.page - 1) * params.limit
        key = trending_key(params) if params.sort == "trending" else None
        rows = [serialize_row(repo, key) for repo in repositories[start : start + params.limit]]
        return Response(
            {
                **coverage(),
                "count": repositories.count(),
                "page": params.page,
                "limit": params.limit,
                "languages": language_counts(),
                "results": rows,
            }
        )
