from django.urls import path, include
from .views import TodoListView

urlpatterns = [
    path('', TodoListView.as_view(), name='todo-list-view'),
    path('tasks/', include('todo_list.tasks.urls')),
]
