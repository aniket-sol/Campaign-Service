from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from sqlalchemy.exc import NoResultFound
from .serializers import UserCampaignSerializer
from users.models import UserRoleType
from users.auth import authenticate, authorize
from .services import CampaignService
from datetime import datetime


class CampaignViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, creating, retrieving, updating, and deleting campaigns.
    """

    @authenticate
    @authorize([UserRoleType.admin, UserRoleType.super_admin])
    def list(self, request):
        try:
            campaigns = CampaignService.list_campaigns()
            return Response({'campaigns': campaigns}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin])
    @action(detail=False, methods=['post'])
    def create(self, request):
        serializer = UserCampaignSerializer(data=request.data)
        if serializer.is_valid():
            try:
                campaign_data = CampaignService.create_campaign(serializer.validated_data, request.user)
                return Response({'message': 'Campaign created successfully', 'campaign': campaign_data},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin, UserRoleType.admin])
    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        try:
            campaign = CampaignService.retrieve_campaign(pk)
            return Response({'campaign': campaign}, status=status.HTTP_200_OK)
        except NoResultFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin])
    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        try:
            campaign_data = CampaignService.update_campaign(pk, request.data)
            return Response({'message': 'Campaign updated successfully', 'campaign': campaign_data},
                            status=status.HTTP_200_OK)
        except NoResultFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin])
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        def destroy(self, request, pk=None):
            try:
                CampaignService.delete_campaign(pk)
                return Response({'message': 'Campaign soft deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except NoResultFound as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
