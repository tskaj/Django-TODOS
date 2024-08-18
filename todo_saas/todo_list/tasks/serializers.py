from rest_framework import serializers
from .models import Task, File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'task', 'file_path', 'uploaded_at']

class TaskSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only = True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'creation_date', 'due_date', 'completion_status', 'completion_date', 'todo_list', 'files']

