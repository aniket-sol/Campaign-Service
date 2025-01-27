from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from sqlalchemy.exc import NoResultFound
from .serializers import UserCampaignSerializer, UserCampaignSequenceSerializer
from users.models import UserRoleType
from users.auth import authenticate, authorize
from .services import CampaignService, CampaignSequenceService
from datetime import datetime


class CampaignViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, creating, retrieving, updating, and deleting campaigns.
    """

    @authenticate
    @authorize([UserRoleType.admin])
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
        # print(serializer)
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
    @action(detail=True, methods=['patch'])
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
        try:
            CampaignService.delete_campaign(pk)
            return Response({'message': 'Campaign soft deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except NoResultFound as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CampaignSequenceViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, creating, retrieving, updating, and deleting campaign sequences.
    """

    @authenticate
    @authorize([UserRoleType.admin])
    def list(self, request):
        try:
            campaign_sequences = CampaignSequenceService.list_campaign_sequences()
            return Response({'campaign_sequences': campaign_sequences}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin, UserRoleType.admin])
    @action(detail=False, methods=['post'])
    def create(self, request):
        print(request.data)
        # Extract practice_ids and roles from the request data
        practice_ids = request.data.get('practices', [])
        roles = request.data.get('roles', [])
        user_campaign_id = request.data.get('user_campaign_id')

        # Validate the input
        if not practice_ids or not roles:
            return Response({'error': 'Both practice_ids and roles are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Call the service to create the campaign targets and sequence
            campaign_sequence_data = CampaignSequenceService.create_campaign_with_targets(
                user_campaign_id, practice_ids, roles, request.data, request.user
            )

            return Response({
                'message': 'Campaign sequence and targets created successfully',
                'campaign_sequence': campaign_sequence_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request):
    #     # print(request.data)
    #     practice_ids = request.data.get('practice_ids', [])
    #     roles = request.data.get('roles', [])
    #     user_campaign_id = request.data.get('user_campaign_id')
    #
    #     if not practice_ids or not roles:
    #         return Response({'error': 'Both practice_ids and roles are required.'}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     serializer = UserCampaignSequenceSerializer(data=request.data)
    #     if serializer.is_valid():
    #         try:
    #             campaign_sequence_data = CampaignSequenceService.create_campaign_sequence(serializer.validated_data, request.user)
    #             return Response({'message': 'Campaign sequence created successfully', 'campaign_sequence': campaign_sequence_data},
    #                              status=status.HTTP_201_CREATED)
    #         except Exception as e:
    #             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin, UserRoleType.admin])
    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        try:
            campaign_sequence = CampaignSequenceService.retrieve_campaign_sequence(pk)
            return Response({'campaign_sequence': campaign_sequence}, status=status.HTTP_200_OK)
        except NoResultFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin, UserRoleType.admin])
    @action(detail=True, methods=['patch'])
    def update(self, request, pk=None):
        try:
            campaign_sequence_data = CampaignSequenceService.update_campaign_sequence(pk, request.data)
            return Response({'message': 'Campaign sequence updated successfully', 'campaign_sequence': campaign_sequence_data},
                            status=status.HTTP_200_OK)
        except NoResultFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @authenticate
    @authorize([UserRoleType.super_admin, UserRoleType.admin])
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        try:
            CampaignSequenceService.delete_campaign_sequence(pk)
            return Response({'message': 'Campaign sequence soft deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except NoResultFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


