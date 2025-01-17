from http import HTTPStatus
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from users.models import UserRoleType
from users.auth import AuthService
from .models import UserCampaign, CampaignStatus
from utils import db_manager

@require_http_methods(["GET", "POST"])
def campaign_list(request):
    session_token = request.data.get("session_token")
    user_id = request.data.get("user_id")
    """
    GET: List all campaigns
    POST: Create a new campaign
    """
    if not AuthService.validate_session(session_token):
        return JsonResponse(
            {"error": "Authentication required"},
            status=HTTPStatus.UNAUTHORIZED
        )

    # Using db_manager to get a session from the context manager
    with db_manager.get_db() as db_session:
        if request.method == "GET":
            if not AuthService.is_authorized(user_id, [UserRoleType.super_admin, UserRoleType.admin]):
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=HTTPStatus.FORBIDDEN
                )

            try:
                campaigns = db_session.query(UserCampaign).all()
                campaigns_data = [{
                    'id': campaign.id,
                    'title': campaign.title,
                    'description': campaign.description,
                    'status': campaign.status,
                    'created_at': campaign.created_at.isoformat(),
                    'created_by': campaign.created_by,
                    'targets': [{
                        'practice_id': target.practice_id,
                        'role': target.role.value
                    } for target in campaign.targets]
                } for campaign in campaigns]

                return JsonResponse({'campaigns': campaigns_data})

            except Exception as e:
                return JsonResponse(
                    {'error': str(e)},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

        elif request.method == "POST":
            if not AuthService.is_authorized(user_id, [UserRoleType.super_admin]):
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=HTTPStatus.FORBIDDEN
                )

            try:
                data = request.json()

                campaign = UserCampaign(
                    title=data['title'],
                    description=data.get('description'),
                    status=CampaignStatus.DRAFT.value,
                    created_by=user_id  # You can use the user_id from request here
                )

                db_session.add(campaign)
                db_session.commit()

                return JsonResponse({
                    'message': 'Campaign created successfully',
                    'campaign_id': campaign.id
                }, status=HTTPStatus.CREATED)

            except IntegrityError:
                db_session.rollback()
                return JsonResponse(
                    {'error': 'Campaign with this title already exists'},
                    status=HTTPStatus.BAD_REQUEST
                )
            except KeyError as e:
                return JsonResponse(
                    {'error': f'Missing required field: {str(e)}'},
                    status=HTTPStatus.BAD_REQUEST
                )
            except Exception as e:
                db_session.rollback()
                return JsonResponse(
                    {'error': str(e)},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )


@require_http_methods(["GET", "PUT", "DELETE"])
def campaign_detail(request, campaign_id: int):
    """
    GET: Retrieve a specific campaign
    PUT: Update a specific campaign
    DELETE: Delete a specific campaign
    """
    if not AuthService.validate_session(request.data.get("session_token")):
        return JsonResponse(
            {"error": "Authentication required"},
            status=HTTPStatus.UNAUTHORIZED
        )

    # Using db_manager to get a session from the context manager
    with db_manager.get_db() as db_session:
        # Check if campaign exists
        campaign = db_session.query(UserCampaign).filter(
            UserCampaign.id == campaign_id
        ).first()

        if not campaign:
            return JsonResponse(
                {'error': 'Campaign not found'},
                status=HTTPStatus.NOT_FOUND
            )

        if request.method == "GET":
            if not AuthService.is_authorized(request.data.get("user_id"), [UserRoleType.super_admin, UserRoleType.admin]):
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=HTTPStatus.FORBIDDEN
                )

            try:
                campaign_data = {
                    'id': campaign.id,
                    'title': campaign.title,
                    'description': campaign.description,
                    'status': campaign.status,
                    'created_at': campaign.created_at.isoformat(),
                    'created_by': campaign.created_by,
                    'targets': [{
                        'practice_id': target.practice_id,
                        'role': target.role.value
                    } for target in campaign.targets]
                }

                return JsonResponse({'campaign': campaign_data})

            except Exception as e:
                return JsonResponse(
                    {'error': str(e)},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

        elif request.method == "PUT":
            if not AuthService.is_authorized(request.data.get("user_id"), [UserRoleType.super_admin]):
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=HTTPStatus.FORBIDDEN
                )

            try:
                data = request.json()

                # Update fields if provided
                if 'title' in data:
                    campaign.title = data['title']
                if 'description' in data:
                    campaign.description = data['description']
                if 'status' in data:
                    campaign.status = data['status']

                campaign.updated_at = datetime.now()
                db_session.commit()

                return JsonResponse({'message': 'Campaign updated successfully'})

            except IntegrityError:
                db_session.rollback()
                return JsonResponse(
                    {'error': 'Campaign with this title already exists'},
                    status=HTTPStatus.BAD_REQUEST
                )
            except Exception as e:
                db_session.rollback()
                return JsonResponse(
                    {'error': str(e)},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

        elif request.method == "DELETE":
            if not AuthService.is_authorized(request.data.get("user_id"), [UserRoleType.super_admin]):
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=HTTPStatus.FORBIDDEN
                )

            try:
                db_session.delete(campaign)
                db_session.commit()

                return JsonResponse({'message': 'Campaign deleted successfully'})

            except Exception as e:
                db_session.rollback()
                return JsonResponse(
                    {'error': str(e)},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )
