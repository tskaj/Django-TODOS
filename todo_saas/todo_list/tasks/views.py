from todo_list.models import TodoList
from .models import Task, File
from .serializers import TaskSerializer, FileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

class TaskView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    max_task_per_todo_list= 50

    def get(self, request, task_id=None):
        user = request.user

        if task_id:
            # Fetch a specific task if task_id is provided
            task = get_object_or_404(Task, id=task_id, todo_list__user=user)
            serialized_task = self.serializer_class(task).data
            return Response(data=serialized_task, status=200)

        # Fetch all tasks if no task_id is provided
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
        
        if Task.objects.filter(todo_list=todo_list).count() >=self.max_task_per_todo_list:
            return Response(
                  {"error": f"One User Can only have {self.max_task_per_todo_list} tasks per to-do list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data['todo_list'] = todo_list.pk
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
    
class SimilarTaskView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get(self, request):
        user = request.user

        # Fetch all tasks for the user
        todo_list = TodoList.objects.filter(user=user).first()
        if not todo_list:
            return Response({"description": "No todo list exists for the current user"}, status=200)

        tasks = Task.objects.filter(todo_list=todo_list)

        # Dictionary to store tasks and their similar counterparts
        similar_tasks_dict = {}

        # Iterate through each task to compare it with every other task
        for task in tasks:
            task_words = set(task.description.lower().split())

            for other_task in tasks:
                if task.id != other_task.id:
                    other_task_words = set(other_task.description.lower().split())

                    # Check if task A's words are all in task B or vice versa
                    if task_words.issubset(other_task_words) or other_task_words.issubset(task_words):
                        # Add the task to the dictionary with the task ID as key
                        if task.id not in similar_tasks_dict:
                            similar_tasks_dict[task.id] = task

                        # Add the other task if not already added
                        if other_task.id not in similar_tasks_dict:
                            similar_tasks_dict[other_task.id] = other_task

        # Convert the dictionary values to a list to get all similar tasks
        similar_tasks = list(similar_tasks_dict.values())

        # Serialize the similar tasks and return the response
        serialized_tasks = self.serializer_class(similar_tasks, many=True).data
        return Response(data=serialized_tasks, status=200)

    

class FileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def post(self, request, task_id):
        # Ensure the task exists and is associated with the current user
        task = get_object_or_404(Task, id=task_id, todo_list__user=request.user)
        
        # Ensure request is using multipart/form-data
        if not request.FILES:
            return Response({"file": ["No file uploaded."]}, status=status.HTTP_400_BAD_REQUEST)

        # Include the task_id in the request data
        request.data._mutable = True  # Make the request data mutable
        request.data['task'] = task_id
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, todo_list__user=request.user)
        files = File.objects.filter(task=task)
        serialized_files = self.serializer_class(files, many=True).data
        return Response(data=serialized_files, status=status.HTTP_200_OK)
