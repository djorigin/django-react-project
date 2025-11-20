"""
Core utility functions for RPAS management system
"""

from guardian.conf import settings as guardian_settings

from django.contrib.auth import get_user_model

User = get_user_model()


def get_anonymous_user_instance(User=None):
    """
    Get or create the anonymous user instance for Guardian permissions.

    This function is required by django-guardian for object-level permissions
    when dealing with anonymous users.

    Args:
        User: The User model class (passed by guardian)

    Returns:
        User: The anonymous user instance
    """
    if User is None:
        User = get_user_model()

    return User(
        email=guardian_settings.ANONYMOUS_USER_NAME,
        is_active=False,
        is_staff=False,
        is_superuser=False,
    )
