from django.urls import path
from .views import PracticeViewSet

urlpatterns = [
    path('', PracticeViewSet.as_view({'get': 'list', 'post': 'create'})),  # for listing and creating practices
    path('<int:pk>/', PracticeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # for detailed views
]

