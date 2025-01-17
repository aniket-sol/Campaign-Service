from django.urls import path
from .views import CampaignViewSet

urlpatterns = [
    path('', CampaignViewSet.as_view({'get': 'list', 'post': 'create'})),  # for listing and creating campaigns
    path('<int:pk>/', CampaignViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'})),  # for detailed views
]
