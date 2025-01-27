from django.urls import path
from .views import MessageViewSet

urlpatterns = [
    path('', MessageViewSet.as_view({'get': 'get_messages'})),  # for listing and creating campaigns
    path('<int:pk>/', MessageViewSet.as_view({'delete': 'update'})),
    # path('sequence', CampaignSequenceViewSet.as_view({'get': 'list', 'post': 'create'})),  # for listing and creating campaigns
    # path('sequence/<int:pk>/', CampaignSequenceViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'})),

]
