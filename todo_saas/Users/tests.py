from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()

class UserTests(APITestCase):
    
    def setUp(self):
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain')
        self.user_view_url = reverse('user-view')
        self.reset_password_url = reverse('reset-password')
        self.confirm_reset_password_url = reverse('confirm-reset-password')

        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')

    def tearDown(self):
        # Cleanup any objects or data that may persist between tests
        User.objects.all().delete()
        mail.outbox = []  # Clear any emails that were sent

    def test_user_registration(self):
        user_data = {
            'email': 'testuser1@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.register_url, user_data )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(email=user_data['email']).exists())


    def test_user_login(self):
        response = self.client.post(self.token_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_user_details_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_user_details_unauthenticated(self):
        response = self.client.get(self.user_view_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset(self):
        response = self.client.post(self.reset_password_url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)  # Ensure an email was sent

    def test_password_reset_invalid_email(self):
        response = self.client.post(self.reset_password_url, {'email': 'invalid@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User with this email does not exist')

    def test_confirm_password_reset(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(self.confirm_reset_password_url, {
            'uid': uidb64,
            'token': token,
            'new_password': 'newpassword123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_confirm_password_reset_invalid_token(self):
        response = self.client.post(self.confirm_reset_password_url, {
            'uid': 'invalid_uid',
            'token': 'invalid_token',
            'new_password': 'newpassword123'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid token or user ID')