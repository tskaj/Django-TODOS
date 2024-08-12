from django.urls import path
from .views import RegisterView, ObtainTokenView, UserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # for user registration
    path('token/', ObtainTokenView.as_view(), name='token_obtain'),  # for obtaining JWT token
    path('me/', UserView.as_view(), name='user-view'),  # for getting the user details
]
