"""Attempt URL routes."""
from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.StartAttemptView.as_view(), name='attempt-start'),
    path('<int:pk>/answer/', views.AnswerQuestionView.as_view(), name='attempt-answer'),
    path('<int:pk>/submit/', views.SubmitAttemptView.as_view(), name='attempt-submit'),
    path('history/', views.AttemptHistoryView.as_view(), name='attempt-history'),
]
