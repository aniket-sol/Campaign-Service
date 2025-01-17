from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from users.auth import AuthService
from users.models import Practice, UserRoleType
from .serializers import PracticeSerializer
from utils import db_manager


class PracticeViewSet(viewsets.ViewSet):
    """
    A ViewSet for performing CRUD operations on the Practice model.
    """

    # This method checks if the user is authenticated for reading
    def check_authenticated(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return Response({"error": "Authorization header is missing"}, status=400)

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({"error": "Invalid authorization header format"}, status=400)

        session_token = parts[1]

        if not AuthService.validate_session(session_token):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # This method checks if the user is authorized (admin role) for modifying data
    def check_authorized(self, request):
        session_token = request.data.get("session_token")
        user_id = request.data.get("user_id")
        if not AuthService.is_authorized(user_id, [UserRoleType.admin, UserRoleType.super_admin]):
            raise PermissionDenied("You do not have permission to perform this action")

    def list(self, request):
        """
        List all practices (accessible for authenticated users).
        """
        # Check if the user is authenticated
        if self.check_authenticated(request):
            return self.check_authenticated(request)

        with db_manager.get_db() as db_session:
            practices = db_session.query(Practice).all()
            serializer = PracticeSerializer(practices, many=True)
            return Response(serializer.data)

    def create(self, request):
        self.check_authorized(request)

        data = request.data
        with db_manager.get_db() as db_session:
            try:
                practice = Practice(
                    name=data['name'],
                    is_active=data.get('is_active', True)
                )
                db_session.add(practice)
                db_session.commit()
                return Response({"message": "Practice created successfully", "practice_id": practice.id},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                db_session.rollback()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific practice (accessible for authenticated users).
        """
        # Check if the user is authenticated
        if self.check_authenticated(request):
            return self.check_authenticated(request)

        with db_manager.get_db() as db_session:
            practice = db_session.query(Practice).filter(Practice.id == pk).first()

            if not practice:
                return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PracticeSerializer(practice)
            return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update a specific practice (accessible for admins).
        """
        # Check if the user is authorized (admin)
        self.check_authorized(request)

        data = request.data
        with db_manager.get_db() as db_session:
            practice = db_session.query(Practice).filter(Practice.id == pk).first()

            if not practice:
                return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update the practice fields
            practice.name = data.get('name', practice.name)
            practice.is_active = data.get('is_active', practice.is_active)
            db_session.commit()

            return Response({"message": "Practice updated successfully"})

    def destroy(self, request, pk=None):
        """
        Delete a specific practice (accessible for admins).
        """
        # Check if the user is authorized (admin)
        self.check_authorized(request)

        with db_manager.get_db() as db_session:
            practice = db_session.query(Practice).filter(Practice.id == pk).first()

            if not practice:
                return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)

            db_session.delete(practice)
            db_session.commit()

            return Response({"message": "Practice deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
