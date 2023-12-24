from django.urls import path
from .views import LoginAPIView, RegistrationAPIView, LogoutAPIView, RefershAPIView, GetAllUsersAPIView, UserAPIView
urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('user/', UserAPIView.as_view(), name='user'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('getAllUsers/', GetAllUsersAPIView.as_view(), name='getAllUsers'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('refresh/', RefershAPIView.as_view(), name='refresh'),
]