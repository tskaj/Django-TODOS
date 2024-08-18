from django.urls import path, include

from todo_list.tasks.views import SimilarTaskView
from .views import TodoListView

urlpatterns = [
    path('', TodoListView.as_view(), name='todo-list-view'),
    path('<int:todolist_id>/', TodoListView.as_view(), name='todo-list-detail'),
    path('tasks/', include('todo_list.tasks.urls')),  # Include task-related URLs
    path('tasks/similar/', SimilarTaskView.as_view(), name='similar-task-list'),
]
