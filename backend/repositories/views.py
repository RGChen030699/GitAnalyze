"""Repository page endpoint (F1 L4)."""

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from repositories.models import Repository
from repositories.serializers import serialize_detail


class RepositoryDetailView(APIView):
    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    def get(self, request: Request, owner: str, name: str) -> Response:
        repo = Repository.objects.get(full_name__iexact=f"{owner}/{name}")
        return Response(serialize_detail(repo))
