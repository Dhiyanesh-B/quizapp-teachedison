"""Attempt serializers."""
from rest_framework import serializers
from .models import Attempt, Answer
from apps.quizzes.serializers import QuizSerializer


class AnswerSerializer(serializers.ModelSerializer):
    """Read-only serializer for answers."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_text', 'selected_answer', 'is_correct']
        read_only_fields = ['id', 'is_correct']


class AttemptSerializer(serializers.ModelSerializer):
    """Serializer for attempt list / detail."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_topic = serializers.CharField(source='quiz.topic', read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    answered_count = serializers.IntegerField(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = [
            'id', 'quiz', 'quiz_title', 'quiz_topic',
            'started_at', 'completed_at', 'score', 'status',
            'total_questions', 'answered_count', 'answers',
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'score', 'status']


class AttemptListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for attempt history list."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_topic = serializers.CharField(source='quiz.topic', read_only=True)
    total_questions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attempt
        fields = [
            'id', 'quiz', 'quiz_title', 'quiz_topic',
            'started_at', 'completed_at', 'score', 'status', 'total_questions',
        ]


class StartAttemptSerializer(serializers.Serializer):
    """Input serializer for starting an attempt."""
    quiz_id = serializers.IntegerField()


class SubmitAnswerSerializer(serializers.Serializer):
    """Input serializer for answering a question."""
    question_id = serializers.IntegerField()
    selected_answer = serializers.CharField(max_length=255)
