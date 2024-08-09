from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class UserViewSet(APIView):
    users = User.objects.all()
    serializer_class = UserSerializer
    permission_classes =() #[permissions.IsAuthenticated]
    def get(self,request):
        users= User.objects.filter()
        serialized_users = self.serializer_class(users, many=True).data
        return Response(data=serialized_users, status=200)