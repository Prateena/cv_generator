from django.urls import path
from rest_framework.authtoken import views as drf_views

from . import views

urlpatterns = [
    path('token/', drf_views.obtain_auth_token),
    path('cv/', views.CVListAPIView.as_view()),
]
