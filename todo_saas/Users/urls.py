from django.urls import path
from .views import RegisterView, ObtainTokenView, UserView, FacebookLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # User registration
    path('token/', ObtainTokenView.as_view(), name='token_obtain'),  # JWT token obtain
    path('me/', UserView.as_view(), name='user-view'),  # Get user details
    path('auth/facebook/', FacebookLoginView.as_view(), name='facebook_login'),  # Facebook login
]
