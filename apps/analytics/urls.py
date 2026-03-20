"""Analytics URL routes."""
from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.OverviewView.as_view(), name='analytics-overview'),
    path('topic/', views.TopicPerformanceView.as_view(), name='analytics-topic'),
]
