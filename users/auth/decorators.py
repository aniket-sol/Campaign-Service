from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from users.auth.auth_service import AuthService  # Adjust import path if necessary
from users.models import UserRoleType  # Adjust import path if necessary


def authenticate(func):
    """
    Decorator to authenticate a user using the AuthService.
    Validates the session token and attaches the user to the request.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            # Validate session and attach user to request
            request.user = AuthService.validate_session(request=request)
            return func(self, request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    return wrapper


def authorize(allowed_roles):
    """
    Decorator to authorize a user based on their role.
    Requires the user to be authenticated first (authenticate decorator must be used).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # Ensure the user is authorized
                AuthService.is_authorized(request.user.id, allowed_roles)
                return func(self, request, *args, **kwargs)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return wrapper
    return decorator
