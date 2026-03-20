"""
AI quiz generation providers.

Each provider implements:
    generate(topic, difficulty, count) -> list[dict]
"""
import json
import random
import requests
from django.conf import settings


class GeminiProvider:
    """
    Calls the Google Gemini API to generate quiz questions.

    Requires GEMINI_API_KEY or GEMINI_KEY in settings / env.
    """

    def generate(self, topic, difficulty, count):
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            raise ProviderUnavailableError("Gemini API key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = self._build_prompt(topic, difficulty, count)

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "responseMimeType": "application/json"
                }
            },
            timeout=settings.AI_REQUEST_TIMEOUT,
        )

        if response.status_code == 429:
            raise RateLimitError("Gemini rate limit exceeded.")
        response.raise_for_status()

        data = response.json()
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            questions = json.loads(content)
            return questions
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise Exception(f"Failed to parse Gemini output: {exc}")

    @staticmethod
    def _build_prompt(topic, difficulty, count):
        return (
            f"Generate {count} multiple-choice quiz questions about '{topic}' "
            f"at '{difficulty}' difficulty level.\n\n"
            f"Return a JSON array where each element has exactly these keys:\n"
            f'  "question": the question text,\n'
            f'  "options": [4 distinct string options],\n'
            f'  "correct_answer": the correct option text verbatim,\n'
            f'  "explanation": a brief explanation.\n\n'
            f"Return ONLY the JSON array."
        )





class MockProvider:
    """
    Fallback provider that returns deterministic mock quiz questions.

    Used when the real AI API is unavailable or not configured.
    """

    # Question templates per topic category
    TEMPLATES = {
        'default': [
            {
                'question': 'What is the primary purpose of {topic}?',
                'options': [
                    'To solve complex problems efficiently',
                    'To make programs run slower',
                    'To increase memory usage',
                    'To remove functionality',
                ],
                'correct_answer': 'To solve complex problems efficiently',
                'explanation': '{topic} is designed to solve complex problems in an efficient manner.',
            },
            {
                'question': 'Which of the following best describes {topic}?',
                'options': [
                    'A systematic approach to problem solving',
                    'A random process with no structure',
                    'An outdated methodology',
                    'A purely theoretical concept with no applications',
                ],
                'correct_answer': 'A systematic approach to problem solving',
                'explanation': '{topic} follows a systematic, structured approach.',
            },
            {
                'question': 'What is a key advantage of understanding {topic}?',
                'options': [
                    'Better problem-solving skills',
                    'No advantage at all',
                    'It makes things more complicated',
                    'It is only useful in theory',
                ],
                'correct_answer': 'Better problem-solving skills',
                'explanation': 'Understanding {topic} fundamentally improves your problem-solving ability.',
            },
            {
                'question': 'In {topic}, what does efficiency typically refer to?',
                'options': [
                    'Time and space complexity',
                    'The color of the interface',
                    'The number of files in a project',
                    'How many developers are on the team',
                ],
                'correct_answer': 'Time and space complexity',
                'explanation': 'Efficiency in {topic} usually refers to how time and space resources are utilized.',
            },
            {
                'question': 'Which learning approach is most effective for mastering {topic}?',
                'options': [
                    'Practice with real-world examples',
                    'Only reading theory',
                    'Memorizing definitions',
                    'Skipping fundamentals',
                ],
                'correct_answer': 'Practice with real-world examples',
                'explanation': 'Hands-on practice is the most effective way to master {topic}.',
            },
            {
                'question': 'What role does {topic} play in software development?',
                'options': [
                    'It forms a foundational building block',
                    'It is completely irrelevant',
                    'It only applies to web development',
                    'It is used only in testing',
                ],
                'correct_answer': 'It forms a foundational building block',
                'explanation': '{topic} is one of the foundational building blocks in software development.',
            },
            {
                'question': 'How does {topic} relate to performance optimization?',
                'options': [
                    'It directly impacts application performance',
                    'It has no impact on performance',
                    'It only affects the user interface',
                    'It slows down development',
                ],
                'correct_answer': 'It directly impacts application performance',
                'explanation': '{topic} knowledge is crucial for writing performant code.',
            },
            {
                'question': 'What is a common misconception about {topic}?',
                'options': [
                    'That it is only for advanced programmers',
                    'That it is essential for all developers',
                    'That practice helps learning',
                    'That it has real-world applications',
                ],
                'correct_answer': 'That it is only for advanced programmers',
                'explanation': '{topic} is accessible to developers at all skill levels.',
            },
            {
                'question': 'Which tool or technique is commonly associated with {topic}?',
                'options': [
                    'Analytical thinking and structured design',
                    'Random guessing',
                    'Ignoring edge cases',
                    'Avoiding documentation',
                ],
                'correct_answer': 'Analytical thinking and structured design',
                'explanation': 'Analytical thinking is core to working with {topic}.',
            },
            {
                'question': 'Why is {topic} important in technical interviews?',
                'options': [
                    'It tests fundamental problem-solving ability',
                    'It is never asked about',
                    'Interviewers like to waste time',
                    'It only matters for senior roles',
                ],
                'correct_answer': 'It tests fundamental problem-solving ability',
                'explanation': '{topic} questions assess core analytical and problem-solving skills.',
            },
        ],
    }

    def generate(self, topic, difficulty, count):
        templates = self.TEMPLATES['default']
        selected = templates[:count] if count <= len(templates) else (
            templates * (count // len(templates) + 1)
        )[:count]

        questions = []
        for i, template in enumerate(selected):
            q = {
                'question': template['question'].format(topic=topic),
                'options': template['options'],
                'correct_answer': template['correct_answer'],
                'explanation': template['explanation'].format(topic=topic),
            }
            questions.append(q)

        # Shuffle options for variety based on difficulty
        if difficulty in ('medium', 'hard'):
            for q in questions:
                correct = q['correct_answer']
                random.shuffle(q['options'])
                # Ensure correct answer is still in options
                if correct not in q['options']:
                    q['options'][0] = correct

        return questions


# ---- Custom exceptions ----

class ProviderUnavailableError(Exception):
    """Raised when an AI provider is not available."""
    pass


class RateLimitError(Exception):
    """Raised when a rate limit is hit."""
    pass
