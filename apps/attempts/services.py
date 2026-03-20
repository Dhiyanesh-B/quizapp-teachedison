"""Attempt service functions."""
from django.utils import timezone
from .models import Attempt, Answer
from apps.quizzes.models import Quiz, Question


def start_attempt(user, quiz_id):
    """
    Start a new quiz attempt for the user.

    Raises ValueError if the quiz doesn't exist or user already has
    an in-progress attempt for this quiz.
    """
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        raise ValueError("Quiz not found.")

    # Check for existing in-progress attempt
    existing = Attempt.objects.filter(user=user, quiz=quiz, status='in_progress').first()
    if existing:
        raise ValueError("You already have an in-progress attempt for this quiz.")

    attempt = Attempt.objects.create(user=user, quiz=quiz, status='in_progress')
    return attempt


def record_answer(attempt, question_id, selected_answer):
    """
    Record an answer for a question within an attempt.

    Raises ValueError on invalid state.
    """
    if attempt.status != 'in_progress':
        raise ValueError("This attempt has already been completed.")

    try:
        question = Question.objects.get(pk=question_id, quiz=attempt.quiz)
    except Question.DoesNotExist:
        raise ValueError("Question not found in this quiz.")

    # Check if already answered
    if Answer.objects.filter(attempt=attempt, question=question).exists():
        raise ValueError("This question has already been answered in this attempt.")

    is_correct = selected_answer.strip() == question.correct_answer.strip()

    answer = Answer.objects.create(
        attempt=attempt,
        question=question,
        selected_answer=selected_answer,
        is_correct=is_correct,
    )
    return answer


def submit_attempt(attempt):
    """
    Submit (finalize) an attempt — calculate score, mark as completed.

    Raises ValueError if already completed.
    """
    if attempt.status == 'completed':
        raise ValueError("This attempt has already been submitted.")

    correct_count = attempt.answers.filter(is_correct=True).count()
    attempt.score = correct_count
    attempt.status = 'completed'
    attempt.completed_at = timezone.now()
    attempt.save()

    return attempt
