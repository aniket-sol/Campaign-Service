from .serializers import UserCreateSerializer, UserLoginSerializer
from .services import UserService
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
                    user = user_service.create_user_with_practice(
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
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                session_data = AuthService.authenticate_user(
                    email=serializer.validated_data["email"],
                    password=serializer.validated_data["password"]
                )
                return Response({
                    "message": "Login successful",
                    "session_token": session_data["session_token"],
                    "expires_at": session_data["expires_at"].isoformat(),
                    "username": session_data["username"],
                    "roleType": session_data["role"],
                    "email": session_data["email"],
                    "name": session_data["first_name"] + " " + session_data["last_name"],
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

