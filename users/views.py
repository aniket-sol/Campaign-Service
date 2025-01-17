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
                    "expires_at": session_data["expires_at"].isoformat()
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

