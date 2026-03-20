"""Quiz URL routes."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListCreateView.as_view(), name='quiz-list'),
    path('create/', views.QuizListCreateView.as_view(), name='quiz-create'),
    path('generate/', views.QuizGenerateView.as_view(), name='quiz-generate'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
]
