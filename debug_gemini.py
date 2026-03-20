import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai_integration.providers import GeminiProvider
import requests

p = GeminiProvider()
try:
    print(p.generate('Math', 'easy', 1))
except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)
    print("Response Body:", e.response.text)
except Exception as e:
    print("Error:", e)
