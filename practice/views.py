from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from users.auth import authenticate, authorize
from users.models import Practice, UserRoleType
from .serializers import PracticeSerializer
from utils import db_manager


class PracticeViewSet(viewsets.ViewSet):

    @authenticate
    def list(self, request):
        with db_manager.get_db() as db_session:
            practices = db_session.query(Practice).all()
            serializer = PracticeSerializer(practices, many=True)
            return Response(serializer.data)


    @authenticate
    @authorize([UserRoleType.super_admin])
    def create(self, request):
        try:
            data = request.data
            with db_manager.get_db() as db_session:
                practice = Practice(
                    name=data['name'],
                    is_active=data.get('is_active', True)
                )
                db_session.add(practice)
                db_session.commit()
                return Response(
                    {"message": "Practice created successfully", "practice_id": practice.id},
                    status=status.HTTP_201_CREATED
                )
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @authenticate
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific practice (accessible for authenticated users).
        """
        with db_manager.get_db() as db_session:
            practice = db_session.query(Practice).filter(Practice.id == pk).first()

            if not practice:
                return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PracticeSerializer(practice)
            return Response(serializer.data)

    @authenticate
    @authorize([UserRoleType.super_admin])
    def update(self, request, pk=None):
        """
        Update a specific practice (accessible for admins).
        """
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

    @authenticate
    @authorize([UserRoleType.super_admin])
    def destroy(self, request, pk=None):
        """
        Delete a specific practice (accessible for admins).
        """
        print(pk)

        with db_manager.get_db() as db_session:
            practice = db_session.query(Practice).filter(Practice.id == pk).first()

            if not practice:
                return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Perform soft delete by setting is_active to False
            practice.is_active = False
            db_session.commit()

            return Response({"message": "Practice soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

