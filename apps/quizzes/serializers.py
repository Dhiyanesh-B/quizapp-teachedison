"""Quiz serializers."""
from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for individual questions."""

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options', 'correct_answer', 'explanation']
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for quiz list view."""
    created_by = serializers.StringRelatedField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic', 'difficulty', 'created_by', 'question_count', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz detail view — includes nested questions."""
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic', 'difficulty', 'created_by', 'questions', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for manual quiz creation (admin)."""
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic', 'difficulty', 'questions']
        read_only_fields = ['id']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for q_data in questions_data:
            Question.objects.create(quiz=quiz, **q_data)
        return quiz


class QuizGenerateSerializer(serializers.Serializer):
    """Serializer for AI quiz generation request."""
    topic = serializers.CharField(max_length=100)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'])
    count = serializers.IntegerField(min_value=1, max_value=20, default=5)
