from rest_framework import serializers
from .models import Task, File
        
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields =['id', 'user', 'description', 'creation_date', 'due_date', 'completion_status', 'completion_date']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'task', 'file_path', 'uploaded_at']
        
