from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets
from .serializers import MessageSerializer
from .services import MessageService
from utils.db_manager import db_manager
from users.auth import authenticate
from centralised_models import Message


class MessageViewSet(viewsets.ViewSet):

    @authenticate
    @action(detail=False, methods=['delete'])
    def update(self, request, pk=None):
        """
        Update an existing message.
        """
        try:
            # Get the database session
            with db_manager.get_db() as db_session:

                # Call the service method to update the message
                message = MessageService.update_message(
                    db_session=db_session,
                    message_id=pk,
                    user_id=request.user.id,
                )

            return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
            # return Response(message, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Failed to update message", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    """
    A simple ViewSet for handling Message CRUD operations.
    """
    @authenticate
    @action(detail=False, methods=['get'])
    def get_messages(self, request):
        """
        Retrieve all messages whose sent_at is less than or equal to the current timestamp.
        """
        try:
            # Get the database session
            with db_manager.get_db() as db_session:
                # Call the service method to retrieve messages that are sent
                messages = MessageService.get_messages(db_session, request.user.id)

            # Return the response with the list of messages
            return Response(MessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Failed to retrieve messages", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def create(self, request):
    #     """
    #     Create a new message.
    #     """
    #     try:
    #         # Extract data from request
    #         campaign_id = request.data.get('campaign_id')
    #         recipient_id = request.data.get('recipient_id')
    #         content = request.data.get('content')
    #         status = request.data.get('status', 'UNREAD')  # Default to "UNREAD"
    #         sent_at = request.data.get('sent_at')
    #
    #         # Get the database session
    #         with db_manager.get_db() as db_session:
    #             # Call the service method to create a message
    #             message = MessageService.create_message(
    #                 db_session,
    #                 campaign_id,
    #                 recipient_id,
    #                 content,
    #                 status,
    #                 sent_at
    #             )
    #
    #         # Return the response with the created message details
    #         return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    #
    #     except ValueError as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     except Exception as e:
    #         return Response({"error": "Failed to create message", "details": str(e)},
    #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #
    # def retrieve(self, request, pk=None):
    #     """
    #     Retrieve a specific message by its ID.
    #     """
    #     try:
    #         # Get the database session
    #         with db_manager.get_db() as db_session:
    #             # Call the service method to retrieve the message
    #             # message = MessageService.update_message(
    #             #     db_session=db_session,
    #             #     message_id=pk,
    #             #     user_id=request.user.id,
    #             # )
    #             message = MessageService.get_message(db_session, pk)
    #
    #         return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
    #
    #     except ValueError as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     except Exception as e:
    #         return Response({"error": "Failed to retrieve message", "details": str(e)},
    #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    # @action(detail=False, methods=['get'])
    # def campaign_messages(self, request, pk=None):
    #     """
    #     Retrieve all messages related to a specific campaign.
    #     """
    #     try:
    #         # Get the database session
    #         with db_manager.get_db() as db_session:
    #             # Call the service method to retrieve messages by campaign_id
    #             messages = MessageService.get_messages_by_campaign(db_session, pk)
    #
    #         return Response(MessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)
    #
    #     except ValueError as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     except Exception as e:
    #         return Response({"error": "Failed to retrieve messages for campaign", "details": str(e)},
    #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
