from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

#router = DefaultRouter()
#router.register(r'users', UserViewSet, basename= 'users')
#router.register(r'tasks', TaskViewSet, basename='tasks')
#router.register(r'files', FileViewSet, basename= 'files')

urlpatterns = [
    #path('', include(router.urls)),
    path('', UserViewSet.as_view(), name='user-viewSet'),
    
    ]