from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import APIView
from .models import User
from .serializers import  UserLoginSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework.authentication import get_authorization_header
import jwt, datetime
from django.conf import settings
from decouple import config
from rest_framework.permissions import IsAuthenticated

def create_access_token(user):
  return jwt.encode({
    'id': user.id,
    'jti': user.id,
    'token_type': 'access',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
    'iat': datetime.datetime.utcnow(),
    'is_staff': user.is_staff,
  } , config('DJANGO_SECRET_KEY', cast=str), algorithm='HS256')
  
def create_refresh_token(user):
  return jwt.encode({
    'id': user.id,
    'jti': user.id,
    'token_type': 'refresh',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
    'iat': datetime.datetime.utcnow(),
    'is_staff': user.is_staff,
  } , config('DJANGO_SECRET_KEY', cast=str), algorithm='HS256')
  
def authenticate_credentials(token):
  try:
    payload = jwt.decode(token, config('DJANGO_SECRET_KEY', cast=str), algorithms='HS256')
    user = User.objects.get(id=payload['id'])
  except Exception as e:
    raise exceptions.AuthenticationFailed(e)
  return user,payload

class UserAPIView(APIView):
  
  def get(self, request):
    try:
      token = get_authorization_header(request).split()[1]
    except Exception as e:
      raise exceptions.AuthenticationFailed(e)
    user, payload = authenticate_credentials(token)
    try:
      user = User.objects.get(id=payload['id'])
      user_serialized = UserProfileSerializer(user).data
    except Exception as e:
      raise exceptions.AuthenticationFailed(e)
    return Response(user_serialized, status=status.HTTP_200_OK)    

class RegistrationAPIView(APIView):
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh_token = create_refresh_token(user)
    access_token = create_access_token(user)
    response = Response()
    response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)
    response.data = {
      'token':access_token,
    }
    # # Creating Log
    # if user.is_staff is False:
    #   log = UserLogs(userName=user.name, data="Created Account")
    #   log.save()
    return response
    
class LoginAPIView(APIView):
  
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      refresh_token = create_refresh_token(user)
      access_token = create_access_token(user)
      response = Response()
      response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)
      response.data = {
        'token':access_token,
        'user_details': UserProfileSerializer(user).data
      }
      return response
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
  
# Route to get all the users
class GetAllUsersAPIView(APIView):
    def get(self, request, format=None):
        all_users = User.objects.all()
        user_serialized = UserProfileSerializer(all_users, many=True).data
        return Response(user_serialized, status=status.HTTP_200_OK)     
      
class RefershAPIView(APIView):
  def post(self, request):
    
    refresh_token = request.COOKIES.get('refreshToken')
    
    user, _ = authenticate_credentials(refresh_token)
    access_token = create_access_token(user)
    return Response({'token':access_token}, status=status.HTTP_200_OK) 
  
class LogoutAPIView(APIView):
  def post(self, request):
    response = Response()
    response.delete_cookie('refreshToken')
    response.data = {
      'msg':'Logout Successful'
    }
    return response