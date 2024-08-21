from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import TodoList
from .serializers import TodoListSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

class TodoListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TodoListSerializer
    @extend_schema(tags=["TodoList APIs"])
    @extend_schema(
        summary='Retrieve a specific TodoList or the first one for the user',
        description='Fetches a TodoList by its ID if provided, or the first TodoList for the user if no ID is given. Returns a detailed description if no list exists.',
        responses={
            200: TodoListSerializer,
            404: 'TodoList not found for the user'
        },
        parameters=[
            OpenApiParameter(name='todolist_id', description='ID of the TodoList to retrieve', required=False, type=int)
        ]
    )
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
    @extend_schema(tags=["TodoList APIs"])
    @extend_schema(
        summary='Create a new TodoList',
        description='Creates a new TodoList for the user. If an ID is provided, it prevents the creation of a TodoList with an existing ID.',
        request=TodoListSerializer,
        responses={
            201: TodoListSerializer,
            400: 'Bad Request - Invalid data'
        },
        parameters=[
            OpenApiParameter(name='todolist_id', description='ID to prevent duplicate TodoList creation', required=False, type=int)
        ]
    )
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
    @extend_schema(tags=["TodoList APIs"])
    @extend_schema(
        summary='Update a specific TodoList',
        description='Updates a TodoList with the given ID. Only the fields provided in the request will be updated.',
        request=TodoListSerializer,
        responses={
            200: TodoListSerializer,
            400: 'Bad Request - Invalid data',
            404: 'TodoList not found for the user'
        },
        parameters=[
            OpenApiParameter(name='todolist_id', description='ID of the TodoList to update', required=True, type=int)
        ]
    )
    def patch(self, request, todolist_id):
        user = request.user
        todo_list = get_object_or_404(TodoList, id=todolist_id, user=user)

        serializer = TodoListSerializer(todo_list, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(tags=["TodoList APIs"])
    @extend_schema(
        summary='Delete a specific TodoList',
        description='Deletes a TodoList with the given ID. This action is irreversible.',
        responses={
            204: 'No Content - Successfully deleted',
            404: 'TodoList not found for the user'
        },
        parameters=[
            OpenApiParameter(name='todolist_id', description='ID of the TodoList to delete', required=True, type=int)
        ]
    )
    def delete(self, request, todolist_id):
        user = request.user
        todo_list = get_object_or_404(TodoList, id=todolist_id, user=user)
        todo_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
