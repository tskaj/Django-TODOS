from django.urls import path, include
from rest_framework.routers import DefaultRouter

#router = DefaultRouter()
#router.register(r'users', UserViewSet, basename= 'users')
#router.register(r'tasks', TaskViewSet, basename='tasks')
#router.register(r'files', FileViewSet, basename= 'files')

urlpatterns = [
    path('tasks/', include('todo_list.tasks.urls')),
    # path('',TaskView.as_view(), name='task-viewset'),
    # path('',FileViewSet.as_view(), name='file-viewSet'),
    
]
