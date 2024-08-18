from django.db import models
from todo_list.models import TodoList


# Task model
class Task(models.Model):
    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name='task', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completion_status = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

# File model
class File(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file_path = models.FileField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_path
    
