"""Attempt views."""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Attempt
from .serializers import (
    AttemptSerializer,
    AttemptListSerializer,
    StartAttemptSerializer,
    SubmitAnswerSerializer,
)
from .services import start_attempt, record_answer, submit_attempt


class StartAttemptView(APIView):
    """POST /api/attempts/start/ — Begin a new quiz attempt."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartAttemptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attempt = start_attempt(
                user=request.user,
                quiz_id=serializer.validated_data['quiz_id'],
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            AttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )


class AnswerQuestionView(APIView):
    """POST /api/attempts/{id}/answer/ — Answer a question in an attempt."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attempt = Attempt.objects.select_related('quiz').get(pk=pk, user=request.user)
        except Attempt.DoesNotExist:
            return Response(
                {'error': 'Attempt not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            answer = record_answer(
                attempt=attempt,
                question_id=serializer.validated_data['question_id'],
                selected_answer=serializer.validated_data['selected_answer'],
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'message': 'Answer recorded.',
            'is_correct': answer.is_correct,
            'question_id': answer.question.id,
            'selected_answer': answer.selected_answer,
        })


class SubmitAttemptView(APIView):
    """POST /api/attempts/{id}/submit/ — Submit and finalize an attempt."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            attempt = Attempt.objects.select_related('quiz').get(pk=pk, user=request.user)
        except Attempt.DoesNotExist:
            return Response(
                {'error': 'Attempt not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            attempt = submit_attempt(attempt)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(AttemptSerializer(attempt).data)


class AttemptHistoryView(ListAPIView):
    """GET /api/attempts/history/ — List all attempts for the current user."""
    permission_classes = [IsAuthenticated]
    serializer_class = AttemptListSerializer

    def get_queryset(self):
        return (
            Attempt.objects
            .filter(user=self.request.user)
            .select_related('quiz')
            .order_by('-started_at')
        )
