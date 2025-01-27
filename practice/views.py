from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from users.auth import authenticate, authorize
from .serializers import PracticeSerializer
from .services import PracticeService


class PracticeViewSet(viewsets.ViewSet):

    @authenticate
    def list(self, request):
        try:
            practices, error = PracticeService.get_practices()

            if error:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize the practice data
            serializer = PracticeSerializer(practices, many=True)
            return Response(serializer.data)

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @authenticate
    @authorize([])
    def create(self, request):
        try:
            data = request.data
            practice, error = PracticeService.create_practice(data)

            if error:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            practice, error = PracticeService.get_practice_by_id(pk)

            if error:
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the practice data
            serializer = PracticeSerializer(practice)
            return Response(serializer.data)

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([])
    def update(self, request, pk=None):
        """
        Update a specific practice (accessible for admins).
        """
        try:
            data = request.data
            practice, error = PracticeService.update_practice(pk, data)

            if error:
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Practice updated successfully"})

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([])
    def destroy(self, request, pk=None):
        """
        Delete a specific practice (accessible for admins).
        """
        try:
            practice, error = PracticeService.soft_delete_practice(pk)

            if error:
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Practice soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

