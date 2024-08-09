from rest_framework import viewsets, permissions
from .models import Task, File
from .serializers import TaskSerializer, FileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class TaskView(APIView):
    #queryset = User.objects.all()
    serializer_class = TaskSerializer
    permission_classes =() #[permissions.IsAuthenticated]
    def get(self, request):
        tasks = Task.objects.filter()
        serialized_tasks = self.serializer_class(tasks, many=True).data
        return Response(data=serialized_tasks, status=200)
    
def get_querset(self):
    return self.queryset.filter(user= self.request.user)

def perform_create(self, serializer):
    serializer.save(user = self.request.user)
    
class FileViewSet(APIView):
    #queryset = User.objects.all()
    serializer_class = FileSerializer
    permission_classes =() # [permissions.IsAuthenticated]
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