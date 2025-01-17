from django.urls import path
from .views import UserViewSet

# practice_create = PracticeViewSet.as_view({'post': 'create'})  # Map the `create` action to POST

urlpatterns = [
    path('signup/', UserViewSet.as_view({'post': 'create'})),
    path('login/', UserViewSet.as_view({'post': 'login'})),
    path('logout/', UserViewSet.as_view({'post': 'logout'})),
]