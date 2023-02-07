from django.urls import path

from .views import RegistrationAPIView


urlpatterns = [
    path('users/', RegistrationAPIView.as_view()),
]