"""Tests for user authentication."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


class RegisterTestCase(TestCase):
    """Test user registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/register/'

    def test_register_success(self):
        """A valid registration should return 201 and user data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['role'], 'USER')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_duplicate_username(self):
        """Duplicate username should return 400."""
        User.objects.create_user(username='taken', email='a@b.com', password='pass1234')
        data = {
            'username': 'taken',
            'email': 'new@example.com',
            'password': 'securepass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Missing required fields should return 400."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(TestCase):
    """Test user login endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/login/'
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='securepass123',
        )

    def test_login_success(self):
        """Valid credentials should return tokens."""
        data = {'username': 'loginuser', 'password': 'securepass123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_invalid_credentials(self):
        """Wrong password should return 400."""
        data = {'username': 'loginuser', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Non-existent user should return 400."""
        data = {'username': 'nouser', 'password': 'somepass'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshTestCase(TestCase):
    """Test token refresh endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='refreshuser',
            email='refresh@example.com',
            password='securepass123',
        )
        # Login to get tokens
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'refreshuser', 'password': 'securepass123'},
            format='json',
        )
        self.refresh_token = response.data['tokens']['refresh']

    def test_refresh_token_success(self):
        """Valid refresh token should return a new access token."""
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': self.refresh_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        """Invalid refresh token should return 401."""
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': 'invalid-token'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
