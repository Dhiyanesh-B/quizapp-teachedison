"""Tests for quiz generation and CRUD."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.quizzes.models import Quiz, Question
from apps.ai_integration.providers import MockProvider


class MockProviderTestCase(TestCase):
    """Test the mock AI quiz generator."""

    def test_generates_correct_count(self):
        """Mock provider should return the requested number of questions."""
        provider = MockProvider()
        questions = provider.generate('Python', 'easy', 5)
        self.assertEqual(len(questions), 5)

    def test_generates_valid_structure(self):
        """Each question should have the required keys."""
        provider = MockProvider()
        questions = provider.generate('DSA', 'medium', 3)
        for q in questions:
            self.assertIn('question', q)
            self.assertIn('options', q)
            self.assertIn('correct_answer', q)
            self.assertIn('explanation', q)
            self.assertEqual(len(q['options']), 4)

    def test_topic_appears_in_question(self):
        """The topic should appear in the generated question text."""
        provider = MockProvider()
        questions = provider.generate('JavaScript', 'easy', 1)
        self.assertIn('JavaScript', questions[0]['question'])

    def test_handles_large_count(self):
        """Should handle counts larger than the template pool."""
        provider = MockProvider()
        questions = provider.generate('Math', 'hard', 15)
        self.assertEqual(len(questions), 15)


class QuizGenerateViewTestCase(TestCase):
    """Test the AI quiz generation endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='quizuser', email='quiz@example.com', password='pass1234',
        )
        self.client.force_authenticate(user=self.user)

    def test_generate_quiz_success(self):
        """POST /api/quizzes/generate/ should create a quiz with questions."""
        data = {'topic': 'Python', 'difficulty': 'easy', 'count': 3}
        response = self.client.post('/api/quizzes/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['topic'], 'Python')
        self.assertEqual(response.data['difficulty'], 'easy')
        self.assertEqual(len(response.data['questions']), 3)

    def test_generate_quiz_missing_topic(self):
        """Missing topic should return 400."""
        data = {'difficulty': 'easy', 'count': 5}
        response = self.client.post('/api/quizzes/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_quiz_unauthenticated(self):
        """Unauthenticated user should get 401."""
        self.client.force_authenticate(user=None)
        data = {'topic': 'Math', 'difficulty': 'medium', 'count': 5}
        response = self.client.post('/api/quizzes/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class QuizCRUDTestCase(TestCase):
    """Test quiz list and detail endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com', password='pass1234', role='ADMIN',
        )
        self.user = User.objects.create_user(
            username='user', email='user@example.com', password='pass1234', role='USER',
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz', topic='Python', difficulty='easy', created_by=self.admin,
        )
        Question.objects.create(
            quiz=self.quiz,
            question_text='What is Python?',
            options=['A language', 'A snake', 'A tool', 'A framework'],
            correct_answer='A language',
            explanation='Python is a programming language.',
        )

    def test_list_quizzes(self):
        """Any authenticated user should see quizzes."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quiz_detail(self):
        """Quiz detail should include questions."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 1)

    def test_delete_quiz_admin(self):
        """Admin should be able to delete a quiz."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_quiz_user_forbidden(self):
        """Regular user should not be able to delete a quiz."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
