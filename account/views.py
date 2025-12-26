from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from account.models import CustomUser
from account.permissions import IsAdminOrManager
from account.enums import RoleChoices
from account.serializers import UserSerializer, AdminSerializer
from account.utils import get_token_for_user
from drf_spectacular.utils import extend_schema

class AdminSignupView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(role=RoleChoices.ADMIN)
        token = get_token_for_user(user)
        headers = self.get_success_headers(serializer.data)
        return Response({**serializer.data, **token}, status=status.HTTP_201_CREATED, headers=headers)

class UserSignupView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_token_for_user(user)
        headers = self.get_success_headers(serializer.data)
        return Response({**serializer.data, **token}, status=status.HTTP_201_CREATED, headers=headers)

class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    @extend_schema(request=UserSerializer(many=True))
    def get_queryset(self):
        user = self.request.user
        if user.role == RoleChoices.MANAGER:
            return CustomUser.objects.filter(role=RoleChoices.DEVELOPER)
        return CustomUser.objects.all()
    
class UserProfileUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def get_object(self):
        return self.request.user
    
class UserRoleUpdateView(UpdateAPIView):
    serializer_class = AdminSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrManager]