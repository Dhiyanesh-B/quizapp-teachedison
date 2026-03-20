"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AI Quiz API",
        default_version='v1',
        description="AI-Powered Quiz Generation & Management API",
        contact=openapi.Contact(email="admin@quizapi.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # App routes
    path('api/auth/', include('apps.users.urls')),
    path('api/quizzes/', include('apps.quizzes.urls')),
    path('api/attempts/', include('apps.attempts.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    # Swagger / ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
