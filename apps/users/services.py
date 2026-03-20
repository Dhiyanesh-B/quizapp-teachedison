"""User service functions."""
from .models import User


def get_user_by_id(user_id):
    """Fetch a user by their primary key, or None."""
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def get_all_users():
    """Return a queryset of all users."""
    return User.objects.all()
