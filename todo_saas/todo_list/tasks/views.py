from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from todo_list.models import TodoList
from .models import Task, File
from .serializers import TaskSerializer, FileSerializer

class TaskView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    max_task_per_todo_list = 50
    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Retrieve tasks or a specific task',
        description='Fetches a specific task by ID if provided or all tasks associated with the user’s todo list if no ID is provided.',
        responses={
            200: TaskSerializer(many=True),
            404: OpenApiResponse(description='Task or TodoList not found'),
        },
        parameters=[
            OpenApiParameter(name='task_id', description='ID of the Task to retrieve', required=False, type=int)
        ]
    )
    def get(self, request, task_id=None):
        user = request.user
        if task_id:
            task = get_object_or_404(Task, id=task_id, todo_list__user=user)
            serialized_task = self.serializer_class(task).data
            return Response(data=serialized_task, status=200)

        todo_list = TodoList.objects.filter(user=user).first()
        if not todo_list:
            return Response({"description": "No todo list exists for the current user"}, status=200)

        tasks = Task.objects.filter(todo_list=todo_list)
        serialized_tasks = self.serializer_class(tasks, many=True).data
        return Response(data=serialized_tasks, status=200)
    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Create a new task',
        description='Creates a new task for the user’s todo list. Limits the number of tasks to `max_task_per_todo_list`.',
        request=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: OpenApiResponse(description='Bad Request - Invalid data or task limit exceeded')
        }
    )
    def post(self, request):
        user = request.user
        todo_list = TodoList.objects.filter(user=user).first()

        if not todo_list:
            return Response({"error": "Todo list not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if Task.objects.filter(todo_list=todo_list).count() >= self.max_task_per_todo_list:
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
    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Update an existing task',
        description='Updates the task specified by `task_id` with the provided data. Only fields provided will be updated.',
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description='Bad Request - Invalid data'),
            404: OpenApiResponse(description='Task not found')
        },
        parameters=[
            OpenApiParameter(name='task_id', description='ID of the Task to update', required=True, type=int)
        ]
    )
    def patch(self, request, task_id):
        user = request.user
        task = get_object_or_404(Task, id=task_id, todo_list__user=user)

        serializer = self.serializer_class(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Delete a task',
        description='Deletes the task specified by `task_id`. This action is irreversible.',
        responses={
            204: OpenApiResponse(description='No Content - Successfully deleted'),
            404: OpenApiResponse(description='Task not found')
        },
        parameters=[
            OpenApiParameter(name='task_id', description='ID of the Task to delete', required=True, type=int)
        ]
    )
    def delete(self, request, task_id):
        user = request.user
        task = get_object_or_404(Task, id=task_id, todo_list__user=user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SimilarTaskView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Retrieve similar tasks',
        description='Finds and groups tasks that have similar descriptions within the user’s todo list. A task is considered similar if its description is a substring of another task’s description.',
        responses={
            200: TaskSerializer(many=True)
        }
    )
    def get(self, request):
        user = request.user
        todo_list = TodoList.objects.filter(user=user).first()
        if not todo_list:
            return Response({"description": "No todo list exists for the current user"}, status=200)

        tasks = Task.objects.filter(todo_list=todo_list)
        task_list = list(tasks)  # Convert queryset to list for easier manipulation
        
        # Initialize groups and visited set
        similar_task_groups = []
        visited_tasks = set()

        for task in task_list:
            if task.id not in visited_tasks:
                current_group = [task]
                visited_tasks.add(task.id)

                for other_task in task_list:
                    if other_task.id != task.id and other_task.id not in visited_tasks:
                        if self.is_substring(task.description, other_task.description):
                            current_group.append(other_task)
                            visited_tasks.add(other_task.id)

                if len(current_group) > 1:
                    similar_task_groups.append(current_group)

        # Serialize the groups of similar tasks
        serialized_groups = [
            self.serializer_class(group, many=True).data for group in similar_task_groups
        ]
        return Response(data=serialized_groups, status=200)

    def is_substring(self, description_a, description_b):
        """
        Determine if one description is a substring of the other.
        """
        return description_a in description_b or description_b in description_a

class FileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    @extend_schema(tags=["Task APIs"])
    @extend_schema(
        summary='Upload a file for a task',
        description='Uploads a file for the task specified by `task_id`. The request must include a file.',
        request=FileSerializer,
        responses={
            201: FileSerializer,
            400: OpenApiResponse(description='Bad Request - No file uploaded or invalid data'),
            404: OpenApiResponse(description='Task not found')
        },
        parameters=[
            OpenApiParameter(name='task_id', description='ID of the Task to which the file is uploaded', required=True, type=int)
        ]
    )
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, todo_list__user=request.user)
        
        if 'file_path' not in request.FILES:
            return Response({"file_path": ["No file uploaded."]}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file_path']

        data = {
            'file_path': file,
            'task': task_id
        }
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

