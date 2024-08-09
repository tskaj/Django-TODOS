from django.db import models
from Users.models import User

    

# Task model
class TodoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_list')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.title

