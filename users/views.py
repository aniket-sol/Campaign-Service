from .serializers import UserCreateSerializer, UserLoginSerializer, UserRequestCreateSerializer, UserRequestUpdateSerializer, UserRequestTableSerializer
from .services import UserService, UserRequestService
from utils import db_manager
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from passlib.context import CryptContext
from .models import User, UserSession, UserRoleType
# from .permissions import IsAuthorized, IsAuthenticated
from .auth import AuthService
from .auth import authenticate, authorize
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
                        "role": practice_role["role"] if practice_role else None,
                        "practice_name": practice_role["practice_name"] if practice_role else None,
                        "practice_id": practice_role["practice_id"] if practice_role else None,
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

    @authenticate
    @authorize([])
    def list_active_entries(self, request):
        """
        List all active user request entries (where is_active is True).
        """
        with db_manager.get_db() as db_session:
            active_entries = UserRequestService.get_active_entries(db_session)
            if not active_entries:
                return Response({"message": "No active entries found"}, status=status.HTTP_404_NOT_FOUND)
            serialized_entries = UserRequestTableSerializer(active_entries, many=True)
            # print(serialized_entries.data)
            return Response({
                "message": "Active entries fetched successfully",
                "entries": serialized_entries.data
            }, status=status.HTTP_200_OK)

    @authenticate
    @authorize([UserRoleType.admin])
    def list_active_entries_practice_wise(self, request, pk):
        """
        List all active user request entries (where is_active is True).
        """
        # print("Got the request")
        with db_manager.get_db() as db_session:
            active_entries = UserRequestService.get_active_entries_practice_wise(db_session, pk)
            if not active_entries:
                return Response({"message": "No active entries found"}, status=status.HTTP_404_NOT_FOUND)
            serialized_entries = UserRequestTableSerializer(active_entries, many=True)
            # print(serialized_entries.data)
            return Response({
                "message": "Active entries fetched successfully",
                "entries": serialized_entries.data
            }, status=status.HTTP_200_OK)

    @authenticate
    def create(self, request):
        """
        Create a new entry in the UserRequestTable.
        """
        serializer = UserRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            with db_manager.get_db() as db_session:
                try:
                    new_entry = UserRequestService.create_entry(serializer.validated_data, db_session, request.user.id)
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

    @authenticate
    @authorize([UserRoleType.admin])
    def partial_update(self, request, pk=None):
        """
        Update the status and is_active fields of a UserRequestTable entry.

        This does not use pk but instead requires user_id and practice_id in the request body.
        """
        # print(request.data)
        serializer = UserRequestUpdateSerializer(data=request.data)
        if serializer.is_valid():
            with db_manager.get_db() as db_session:
                try:
                    updated_entry = UserRequestService.update_status_and_active(
                        entry_id = pk,
                        user_id=serializer.validated_data["user_id"],
                        practice_id=serializer.validated_data["practice_id"],
                        status=serializer.validated_data["status"],
                        role=serializer.validated_data["role"],
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

