"""Tests for quiz attempts and scoring."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.quizzes.models import Quiz, Question
from apps.attempts.models import Attempt, Answer
from apps.attempts.services import start_attempt, record_answer, submit_attempt


class AttemptServiceTestCase(TestCase):
    """Test attempt business logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='pass1234',
        )
        self.quiz = Quiz.objects.create(
            title='Scoring Test', topic='Math', difficulty='easy', created_by=self.user,
        )
        self.q1 = Question.objects.create(
            quiz=self.quiz, question_text='1+1=?',
            options=['1', '2', '3', '4'], correct_answer='2', explanation='Basic addition.',
        )
        self.q2 = Question.objects.create(
            quiz=self.quiz, question_text='2*3=?',
            options=['4', '5', '6', '7'], correct_answer='6', explanation='Basic multiplication.',
        )
        self.q3 = Question.objects.create(
            quiz=self.quiz, question_text='10/2=?',
            options=['3', '4', '5', '6'], correct_answer='5', explanation='Basic division.',
        )

    def test_start_attempt(self):
        """Starting an attempt should create an in-progress attempt."""
        attempt = start_attempt(self.user, self.quiz.id)
        self.assertEqual(attempt.status, 'in_progress')
        self.assertEqual(attempt.user, self.user)
        self.assertEqual(attempt.quiz, self.quiz)

    def test_no_duplicate_in_progress(self):
        """Cannot start a second in-progress attempt for the same quiz."""
        start_attempt(self.user, self.quiz.id)
        with self.assertRaises(ValueError):
            start_attempt(self.user, self.quiz.id)

    def test_record_correct_answer(self):
        """Recording a correct answer should mark is_correct=True."""
        attempt = start_attempt(self.user, self.quiz.id)
        answer = record_answer(attempt, self.q1.id, '2')
        self.assertTrue(answer.is_correct)

    def test_record_wrong_answer(self):
        """Recording a wrong answer should mark is_correct=False."""
        attempt = start_attempt(self.user, self.quiz.id)
        answer = record_answer(attempt, self.q1.id, '3')
        self.assertFalse(answer.is_correct)

    def test_no_duplicate_answer(self):
        """Cannot answer the same question twice in one attempt."""
        attempt = start_attempt(self.user, self.quiz.id)
        record_answer(attempt, self.q1.id, '2')
        with self.assertRaises(ValueError):
            record_answer(attempt, self.q1.id, '3')

    def test_scoring(self):
        """Submit should calculate the correct score."""
        attempt = start_attempt(self.user, self.quiz.id)
        record_answer(attempt, self.q1.id, '2')   # correct
        record_answer(attempt, self.q2.id, '6')   # correct
        record_answer(attempt, self.q3.id, '3')   # wrong

        attempt = submit_attempt(attempt)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.status, 'completed')
        self.assertIsNotNone(attempt.completed_at)

    def test_cannot_submit_twice(self):
        """Cannot submit an already-completed attempt."""
        attempt = start_attempt(self.user, self.quiz.id)
        submit_attempt(attempt)
        with self.assertRaises(ValueError):
            submit_attempt(attempt)


class AttemptAPITestCase(TestCase):
    """Test attempt API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apistudent', email='api@example.com', password='pass1234',
        )
        self.quiz = Quiz.objects.create(
            title='API Test Quiz', topic='Science', difficulty='medium', created_by=self.user,
        )
        self.question = Question.objects.create(
            quiz=self.quiz, question_text='What is H2O?',
            options=['Water', 'Oxygen', 'Hydrogen', 'Helium'],
            correct_answer='Water', explanation='H2O is the chemical formula for water.',
        )
        self.client.force_authenticate(user=self.user)

    def test_start_attempt_api(self):
        """POST /api/attempts/start/ should create an attempt."""
        response = self.client.post(
            '/api/attempts/start/',
            {'quiz_id': self.quiz.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'in_progress')

    def test_answer_question_api(self):
        """POST /api/attempts/{id}/answer/ should record an answer."""
        # Start attempt
        resp = self.client.post(
            '/api/attempts/start/',
            {'quiz_id': self.quiz.id},
            format='json',
        )
        attempt_id = resp.data['id']

        # Answer question
        response = self.client.post(
            f'/api/attempts/{attempt_id}/answer/',
            {'question_id': self.question.id, 'selected_answer': 'Water'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])

    def test_submit_attempt_api(self):
        """POST /api/attempts/{id}/submit/ should finalize and score."""
        resp = self.client.post(
            '/api/attempts/start/',
            {'quiz_id': self.quiz.id},
            format='json',
        )
        attempt_id = resp.data['id']
        self.client.post(
            f'/api/attempts/{attempt_id}/answer/',
            {'question_id': self.question.id, 'selected_answer': 'Water'},
            format='json',
        )

        response = self.client.post(f'/api/attempts/{attempt_id}/submit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 1)
        self.assertEqual(response.data['status'], 'completed')

    def test_attempt_history_api(self):
        """GET /api/attempts/history/ should return the user's attempts."""
        response = self.client.get('/api/attempts/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attempt_unauthenticated(self):
        """Unauthenticated user should get 401."""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/api/attempts/start/',
            {'quiz_id': self.quiz.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
