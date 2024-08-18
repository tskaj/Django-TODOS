from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import TodoList
from .serializers import TodoListSerializer
from django.shortcuts import get_object_or_404

class TodoListView(APIView):
    permission_classes = [IsAuthenticated]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TodoList
from .serializers import TodoListSerializer

class TodoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, todolist_id=None):
        user = request.user
        if todolist_id:
            todo_list = get_object_or_404(TodoList, id=todolist_id, user=user)
        else:
            todo_list = TodoList.objects.filter(user=user).first()
        
        if not todo_list:
            return Response({"description": "No todo list exists for the current user"}, status=200)

        serializer = TodoListSerializer(todo_list)
        return Response(serializer.data, status=200)
    
    def post(self, request, todolist_id=None):
        user = request.user
        if todolist_id:
            # Prevent creating a new todo list with an existing ID
            return Response({"error": "Cannot create a todo list with an existing ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        data['user'] = user.id
        serializer = TodoListSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, todolist_id):
        user = request.user
        todo_list = get_object_or_404(TodoList, id=todolist_id, user=user)

        serializer = TodoListSerializer(todo_list, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, todolist_id):
        user = request.user
        todo_list = get_object_or_404(TodoList, id=todolist_id, user=user)
        todo_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)