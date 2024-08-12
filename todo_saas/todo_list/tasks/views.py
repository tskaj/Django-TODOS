from todo_list.models import TodoList
from .models import Task, File
from .serializers import TaskSerializer, FileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class TaskView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get(self, request):
        user = request.user
        todo_list = TodoList.objects.filter(user=user).first()
        if not todo_list:
            return Response({"description": "No todo list exists for the current user"}, status=200)

        tasks = Task.objects.filter(todo_list=todo_list)
        serialized_tasks = self.serializer_class(tasks, many=True).data
        return Response(data=serialized_tasks, status=200)

    def post(self, request):
        user = request.user
        todo_list = TodoList.objects.filter(user=user).first()

        if not todo_list:
            return Response({"error": "Todo list not found"}, status=status.HTTP_404_NOT_FOUND)

        request.data['todo_list'] = todo_list.pk  # Fix field name to match your serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(todo_list=todo_list)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, task_id):
        user = request.user
        task = get_object_or_404(Task, id=task_id, todo_list__user=user)

        serializer = self.serializer_class(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        user = request.user
        task = get_object_or_404(Task, id=task_id, todo_list__user=user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    

class FileView(APIView):
    #queryset = User.objects.all()
    serializer_class = FileSerializer
    permission_classes =[AllowAny] # [permissions.IsAuthenticated]
    def get(self,request):
        files = File.objects.filter()
        serialized_files = self.serializer_class(files, many = True).data
        return Response(data=serialized_files, status=200)
    
    def get_queryset(self):
        return self.queryset.filter(task__user=self.request.user)

    def perform_create(self, serializer):
        task_id = self.request.data.get('task')
        if Task.objects.filter(id=task_id, user=self.request.user).exists():
            serializer.save()
        else:
            raise serializer.ValidationError("You do not have permission to add files to this task.")