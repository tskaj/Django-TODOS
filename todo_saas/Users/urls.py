from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView

#router = DefaultRouter()
#router.register(r'users', UserViewSet, basename= 'users')
#router.register(r'tasks', TaskViewSet, basename='tasks')
#router.register(r'files', FileViewSet, basename= 'files')

urlpatterns = [
    #path('', include(router.urls)),
    path('', UserView.as_view(), name='user-viewSet'),
    
    ]