from django.urls import path
from .views import UserViewSet, UserRequestViewSet

# practice_create = PracticeViewSet.as_view({'post': 'create'})  # Map the `create` action to POST

urlpatterns = [
    path('signup/', UserViewSet.as_view({'post': 'create'})),
    path('login/', UserViewSet.as_view({'post': 'login'})),
    path('logout/', UserViewSet.as_view({'post': 'logout'})),
    path('change-password/', UserViewSet.as_view({'post': 'change_password'})),
    path('request/', UserRequestViewSet.as_view({'get': 'list_active_entries', 'post': 'create'})),
    path('request/<int:pk>/', UserRequestViewSet.as_view({'get': 'list_active_entries_practice_wise', 'patch': 'partial_update'})),
]