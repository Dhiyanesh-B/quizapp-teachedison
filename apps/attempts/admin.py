"""Admin registration for Attempt and Answer models."""
from django.contrib import admin
from .models import Attempt, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_answer', 'is_correct')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'quiz__title')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)
