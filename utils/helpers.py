"""Shared utility functions."""
from django.utils import timezone


def get_current_time():
    """Return the current timezone-aware datetime."""
    return timezone.now()


def calculate_percentage(part, total):
    """Return percentage rounded to 2 decimal places, or 0 if total is 0."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)
