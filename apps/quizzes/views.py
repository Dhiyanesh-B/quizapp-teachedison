"""Quiz views."""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from apps.users.permissions import IsAdmin, IsAdminOrReadOnly
from .models import Quiz, Question
from .serializers import (
    QuizSerializer,
    QuizDetailSerializer,
    QuizCreateSerializer,
    QuizGenerateSerializer,
)
from .services import create_quiz_from_ai


class QuizListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/quizzes/          — List all quizzes (any authenticated user).
    POST /api/quizzes/create/   — Create a quiz manually (admin only).
    """
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return (
            Quiz.objects
            .select_related('created_by')
            .annotate(question_count=Count('questions'))
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateSerializer
        return QuizSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuizDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/quizzes/{id}/  — Retrieve a single quiz with questions.
    DELETE /api/quizzes/{id}/  — Delete a quiz (admin only).
    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = QuizDetailSerializer

    def get_queryset(self):
        return Quiz.objects.select_related('created_by').prefetch_related('questions')


class QuizGenerateView(APIView):
    """
    POST /api/quizzes/generate/  — Generate a quiz using AI.

    Input: {"topic": "DSA", "difficulty": "medium", "count": 5}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topic = serializer.validated_data['topic']
        difficulty = serializer.validated_data['difficulty']
        count = serializer.validated_data['count']

        quiz = create_quiz_from_ai(
            topic=topic,
            difficulty=difficulty,
            count=count,
            user=request.user,
        )

        return Response(
            QuizDetailSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )
