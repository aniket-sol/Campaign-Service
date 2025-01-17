from django.urls import path
from . import views

urlpatterns = [
    path('campaign/', views.campaign_list, name='campaign-list'),  # GET, POST
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='campaign-detail'),  # GET, PUT, DELETE
]