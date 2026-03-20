"""Attempt and Answer models."""
from django.db import models
from django.conf import settings


class Attempt(models.Model):
    """A user's attempt at taking a quiz."""

    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    quiz = models.ForeignKey(
        'quizzes.Quiz',
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')

    class Meta:
        db_table = 'attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} → {self.quiz.title} ({self.status})"

    @property
    def total_questions(self):
        return self.quiz.questions.count()

    @property
    def answered_count(self):
        return self.answers.count()


class Answer(models.Model):
    """A single answer within an attempt."""

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(
        'quizzes.Question',
        on_delete=models.CASCADE,
        related_name='answers',
    )
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'answers'
        unique_together = ('attempt', 'question')  # one answer per question per attempt

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.question.question_text[:40]}"
