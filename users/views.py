from .serializers import UserCreateSerializer, UserLoginSerializer, UserRequestCreateSerializer, UserRequestUpdateSerializer
from .services import UserService, UserRequestService
from utils import db_manager
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from passlib.context import CryptContext
from .models import User, UserSession
# from .permissions import IsAuthorized, IsAuthenticated
from .auth import AuthService
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserViewSet(ViewSet):
    # permission_classes = [IsAuthenticated]

    def create(self, request):
        with db_manager.get_db() as db_session:
            # Use the serializer for validation
            serializer = UserCreateSerializer(data=request.data, db_session=db_session)
            if serializer.is_valid():
                user_service = UserService(db_session)
                try:
                    user = user_service.create_user(
                        validated_data=serializer.validated_data
                    )
                    return Response(
                        {
                            "message": "User created successfully",
                            "user_id": user.id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except ValueError as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        """
                Authenticate a user and provide a session token.
                """
        with db_manager.get_db() as db_session:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    session_data = AuthService.authenticate_user(
                        email=serializer.validated_data["email"],
                        password=serializer.validated_data["password"]
                    )
                    user_service = UserService(db_session)
                    practice_role = user_service.get_user_practice_role(user_id=session_data["user_id"])
                    return Response({
                        "message": "Login successful",
                        "session_token": session_data["session_token"],
                        "expires_at": session_data["expires_at"].isoformat(),
                        "username": session_data["username"],
                        "is_super_admin": session_data["is_super_admin"],
                        "email": session_data["email"],
                        "name": session_data["first_name"] + " " + session_data["last_name"],
                        "role": practice_role,
                    }, status=status.HTTP_200_OK)
                except AuthenticationFailed as e:
                    return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def logout(self, request):
        try:
            # Validate the session and get the user (this ensures the session is active)
            session_token = None  # Optional if request headers contain the token
            user = AuthService.validate_session(session_token=session_token, request=request)

            # Invalidate the session
            AuthService.invalidate_session(request.session_token)

            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class UserRequestViewSet(ViewSet):
    """
    A ViewSet for managing user requests.
    """
    def create(self, request):
        """
        Create a new entry in the UserRequestTable.
        """
        serializer = UserRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            with db_manager.get_db() as db_session:
                try:
                    new_entry = UserRequestService.create_entry(serializer.validated_data, db_session)
                    return Response({
                        "message": "Entry created successfully",
                        "entry": {
                            "id": new_entry.id,
                            "user_id": new_entry.user_id,
                            "practice_id": new_entry.practice_id,
                            "role": new_entry.role.value,
                            "is_active": new_entry.is_active,
                            "status": new_entry.status,
                        }
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        Update the status and is_active fields of a UserRequestTable entry.

        This does not use pk but instead requires user_id and practice_id in the request body.
        """
        serializer = UserRequestUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data["user_id"]
            practice_id = serializer.validated_data["practice_id"]

            with db_manager.get_db() as db_session:
                try:
                    updated_entry = UserRequestService.update_status_and_active(
                        user_id=user_id,
                        practice_id=practice_id,
                        status=serializer.validated_data["status"],
                        is_active=serializer.validated_data["is_active"],
                        db_session=db_session
                    )
                    return Response({
                        "message": "Entry updated successfully",
                        "entry": {
                            "id": updated_entry.id,
                            "user_id": updated_entry.user_id,
                            "practice_id": updated_entry.practice_id,
                            "role": updated_entry.role.value,
                            "is_active": updated_entry.is_active,
                            "status": updated_entry.status,
                        }
                    }, status=status.HTTP_200_OK)
                except ValueError as e:
                    return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
