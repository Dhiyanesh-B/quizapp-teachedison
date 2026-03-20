"""Quiz and Question models."""
from django.db import models
from django.conf import settings


class Quiz(models.Model):
    """A quiz containing multiple questions."""

    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=100, db_index=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']
        verbose_name_plural = 'quizzes'

    def __str__(self):
        return f"{self.title} ({self.topic} - {self.difficulty})"




class Question(models.Model):
    """A single question belonging to a quiz."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField(help_text='List of answer options, e.g. ["A", "B", "C", "D"]')
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'questions'
        ordering = ['id']

    def __str__(self):
        return self.question_text[:60]
