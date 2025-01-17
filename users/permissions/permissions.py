# # users/permissions.py
# from rest_framework.permissions import BasePermission
# from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
# from app.auth.auth_service import verify_token
#
# class IsAuthenticated(BasePermission):
#     """
#     Permission class to check if the user is authenticated.
#     """
#     def has_permission(self, request, view):
#         token = request.headers.get("Authorization")
#         if not token:
#             raise AuthenticationFailed("Authentication token is missing.")
#
#         user = verify_token(token)
#         if not user:
#             raise AuthenticationFailed("Invalid or expired token.")
#
#         request.user = user  # Attach the authenticated user to the request
#         return True
#
#
# class IsAuthorized(BasePermission):
#     """
#     Permission class to check if the user has the required role.
#     """
#     def __init__(self, required_roles=None):
#         self.required_roles = required_roles or []
#
#     def has_permission(self, request, view):
#         user = getattr(request, "user", None)
#         if not user:
#             raise PermissionDenied("User not authenticated.")
#
#         if user.role not in self.required_roles:
#             raise PermissionDenied("You do not have permission to access this resource.")
#
#         return True
