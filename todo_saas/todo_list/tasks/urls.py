from django.urls import path
from .views import TaskView

urlpatterns = [
    path('', TaskView.as_view(), name='task-list'),  # For GET and POST requests
    path('<int:task_id>/', TaskView.as_view(), name='task-detail'),  # For PATCH and DELETE requests
]
