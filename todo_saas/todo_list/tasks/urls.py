from django.urls import path
from .views import TaskView, FileView, SimilarTaskView

urlpatterns = [
    path('', TaskView.as_view(), name='task-list'),  # GET all tasks, POST create task
    path('<int:task_id>/', TaskView.as_view(), name='task-detail'),  # PATCH update, DELETE task
    path('<int:task_id>/files/', FileView.as_view(), name='file-list'),  # GET files
    path('<int:task_id>/files/upload/', FileView.as_view(), name='file-upload'),  # POST upload file
]
