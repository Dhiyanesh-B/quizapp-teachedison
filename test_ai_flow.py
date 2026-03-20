import os
import django
from pprint import pprint

# Setup Django environment BEFORE other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User
from apps.quizzes.models import Quiz

def run_test_flow():
    client = APIClient()
    
    print("\n--- 1. Registering Test User ---")
    user_data = {
        'username': 'tester_bot',
        'email': 'bot@example.com',
        'password': 'password123'
    }
    # Clean up old user if exists
    User.objects.filter(username='tester_bot').delete()
    
    resp = client.post('/api/auth/register/', user_data, format='json')
    print("Registration Status:", resp.status_code)
    
    print("\n--- 2. Logging In ---")
    login_resp = client.post('/api/auth/login/', {
        'username': 'tester_bot',
        'password': 'password123'
    }, format='json')
    token = login_resp.data['tokens']['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    print("Login Status:", login_resp.status_code)
    
    print("\n--- 3. Hitting AI Quiz Generation Endpoint ---")
    print("(This will use the Mock Fallback since no OpenAI Key is provided in .env)")
    gen_data = {
        'topic': 'Python Django',
        'difficulty': 'medium',
        'count': 3
    }
    gen_resp = client.post('/api/quizzes/generate/', gen_data, format='json')
    print("Generate Status:", gen_resp.status_code)
    
    print("\n--- Generated AI Quiz Result ---")
    quiz_data = gen_resp.data
    print(f"Title: {quiz_data.get('title')}")
    print(f"Topic: {quiz_data.get('topic')}")
    print("Questions:")
    for i, q in enumerate(quiz_data.get('questions', []), 1):
        print(f"  Q{i}: {q['question_text']}")
        print(f"      Options: {q['options']}")
        print(f"      Correct: {q['correct_answer']}")
        print(f"      Explanation: {q['explanation']}\n")

if __name__ == "__main__":
    run_test_flow()
