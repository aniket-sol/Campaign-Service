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
        # Open a database session
        with db_manager.get_db() as db_session:
            # Initialize the serializer with the database session
            serializer = UserCreateSerializer(data=request.data, db_session=db_session)
            if serializer.is_valid():
                # Pass the validated data to the service class
                user_service = UserService(db_session)
                user = user_service.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    first_name=serializer.validated_data.get('first_name'),
                    last_name=serializer.validated_data.get('last_name')
                )
                return Response({
                    "message": "User created successfully",
                    "user_id": user.id
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        # Serialize the request data
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Authenticate user using AuthService (no need to pass db_session)
            session_data = AuthService.authenticate_user(email, password)

            # Return response with session token and expiration time
            return Response({
                "message": "Login successful",
                "session_token": session_data["session_token"],
                "expires_at": session_data["expires_at"].isoformat()
            }, status=status.HTTP_200_OK)

        # If serializer is invalid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def logout(self, request):
        session_token = request.data.get('session_token')

        if not session_token:
            return Response({"error": "Session token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Invalidate the session using the AuthService method without passing db_session
            AuthService.invalidate_session(session_token)
            return Response({
                "message": "User logged out successfully"
            }, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            # If session invalidation fails, return the error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

