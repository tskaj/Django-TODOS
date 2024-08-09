from django.urls import path
from .views import TaskView, FileView


urlpatterns = [
    path('', TaskView.as_view(), name="task-view"),
    path('', FileView.as_view(), name="file-view")
    
]