from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class FacebookMocks:
    facebook_response_mock = inline_serializer(
        name = "FacebookResponseSerializer",
        fields = {
            "token": serializers.CharField(),
            "refresh": serializers.CharField()
        }
        
    )
    
    facebook_request_mock = inline_serializer(
        name = "FacebookRequestSerializer",
        fields = {
            "access_token": serializers.CharField(),
        }
        
    )
    
    
class ResetPasswordMocks:
    resetpassword_request_mock = inline_serializer(
        name = "ObtainTokenSerializer",
        fields = {
            "email" : serializers.CharField()
        }
    )
    
    