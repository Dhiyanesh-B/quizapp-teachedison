"""Global exception handler for DRF."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent JSON error responses.

    Format:
        {"error": "<message>", "details": {...}}
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': _get_error_message(response),
            'details': response.data if isinstance(response.data, dict) else {'info': response.data},
        }
        response.data = error_data
        return response

    # Unhandled exceptions — return 500
    return Response(
        {'error': 'Internal server error', 'details': {'info': str(exc)}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _get_error_message(response):
    """Extract a human-readable error message from the DRF response."""
    status_messages = {
        400: 'Bad request',
        401: 'Authentication required',
        403: 'Permission denied',
        404: 'Not found',
        405: 'Method not allowed',
        429: 'Too many requests',
    }
    return status_messages.get(response.status_code, 'An error occurred')
