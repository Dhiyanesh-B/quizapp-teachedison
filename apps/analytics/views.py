"""Analytics views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import get_user_overview, get_topic_performance


class OverviewView(APIView):
    """GET /api/analytics/overview/ — User performance overview."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_user_overview(request.user)
        return Response(data)


class TopicPerformanceView(APIView):
    """GET /api/analytics/topic/ — Per-topic performance breakdown."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_topic_performance(request.user)
        return Response(data)
