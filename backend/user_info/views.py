# user_info/views.py
import time

# Importing necessary modules and classes
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser

# Importing the User model and the UserSerializer
from .models import User, UserProfile
from .serializers import UserSerializer


# Creating a viewset that inherits from ModelViewSet
class UserInfoViewSet(viewsets.ModelViewSet):
    # Specifying the queryset for the viewset (all User objects)
    queryset = User.objects.all().order_by('-date_joined')
    # Specifying the serializer class to be used
    serializer_class = UserSerializer

    # Add IsAuthenticated permission to all actions
    permission_classes = [IsAuthenticated]

    # Creating a custom action for user registration
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])  # 允许非身份验证访问
    def register(self, request):
        # Retrieving username and password from the request data
        # 获取基本用户信息
        username = request.data.get('username')
        password = request.data.get('password')
        # 获取额外的profile信息
        avatar = request.data.get('avatar')
        gender = request.data.get('gender')
        occupation = request.data.get('occupation')

        # Checking for missing username or password
        if not username or not password:
            return Response({'msg': 'Invalid input. Please provide both username and password.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Checking if a user with the given username already exists
        if User.objects.filter(username=username).exists():
            return Response({'msg': 'Registration failed. User with this username already exists.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 创建User和UserProfile实例
        user = User.objects.create_user(username=username, password=password)
        if avatar and gender and occupation:
            UserProfile.objects.create(user=user, avatar=avatar, gender=gender, occupation=occupation)

        # Returning a success message
        return Response({'msg': 'Registration successful.'})

    # Creating a custom action for user login
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])  # 允许非身份验证访问
    def login(self, request):
        # Retrieving username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticating the user using Django's authenticate method
        user = authenticate(request, username=username, password=password)

        # Checking if authentication was successful
        if user is not None:
            login(request, user)

            # Generating a RefreshToken
            refresh = RefreshToken.for_user(user)

            # Creating a dictionary with the access and refresh tokens
            token_dict = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }

            # Returning a success message and the token dictionary
            return Response({'msg': 'Login successful.', 'token': token_dict.get('access_token')},
                            status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Login failed. Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
