from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from Users.response_mocks import FacebookMocks, ResetPasswordMocks
from .serializers import UserRegisterationSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import requests
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from drf_spectacular.utils import extend_schema, OpenApiResponse


User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterationSerializer
    @extend_schema(tags=["User APIs"])
    @extend_schema(
        request=UserRegisterationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserRegisterationSerializer,
                description="User successfully registered"
            ),
            400: OpenApiResponse(
                description="Invalid input"
            ),
        },
        summary="Register a new user"
    )
    def post(self, request):
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(tags=["User APIs"])
    @extend_schema(
        request=ResetPasswordMocks.resetpassword_request_mock,
        responses={
            200: OpenApiResponse(
                description="Password reset link sent"
            ),
            400: OpenApiResponse(
                description="User with this email does not exist"
            ),
        },
        summary="Send password reset link"
    )
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f"http://localhost:8000/password/reset/confirm/?uid={uidb64}&token={token}"

            send_mail(
                'Password Reset Request',
                f'Please use the following link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
        
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not (uidb64 and token and new_password):
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()

        if user is not None and token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()

            # Generate a new JWT token after successful password reset
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token or user ID"}, status=status.HTTP_400_BAD_REQUEST)


class ObtainTokenView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(tags=["User APIs"])
    @extend_schema(
        request= FacebookMocks.facebook_request_mock,
        responses={
            200: FacebookMocks.facebook_response_mock,
            400: OpenApiResponse(
                description="Invalid facebook token"
            ),
        },
        summary="Confirm password reset"
    )

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    @extend_schema(tags=["User APIs"])
    @extend_schema(
        responses={
            200: UserSerializer,
        },
        summary="Get user details"
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
    
    
class FacebookLoginView(APIView):
    @extend_schema(tags=["User APIs"])
    @extend_schema(
        request= FacebookMocks.facebook_request_mock,
        responses={
            200: FacebookMocks.facebook_response_mock,
            400: OpenApiResponse(
                description="Invalid facebook token"
            ),
        },
        summary="Confirm password reset"
    )
    def post(self, request):
        access_token = request.data.get("access_token")

        if not access_token:
            return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the access token with Facebook
        fb_response = requests.get(
            f"https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email"
        )
        fb_data = fb_response.json()

        if "error" in fb_data:
            return Response({"error": "Invalid Facebook token"}, status=status.HTTP_400_BAD_REQUEST)

        email = fb_data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email, defaults={"username": fb_data.get("name")})

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
