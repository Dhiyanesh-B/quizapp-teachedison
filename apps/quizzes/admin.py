"""Admin registration for Quiz and Question models."""
from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'created_by', 'created_at')
    list_filter = ('difficulty', 'topic')
    search_fields = ('title', 'topic')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'correct_answer')
    list_filter = ('quiz__topic',)
    search_fields = ('question_text',)
