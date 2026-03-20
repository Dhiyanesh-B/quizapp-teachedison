"""Quiz service functions."""
from .models import Quiz, Question
from apps.ai_integration.services import generate_quiz_questions


def create_quiz_from_ai(topic, difficulty, count, user):
    """
    Generate quiz questions via AI and save them as a new Quiz.

    Returns the created Quiz instance with questions.
    """
    # Generate questions using AI (with retry + fallback)
    questions_data = generate_quiz_questions(
        topic=topic,
        difficulty=difficulty,
        count=count,
    )

    # Create the quiz
    quiz = Quiz.objects.create(
        title=f"{topic} Quiz ({difficulty.capitalize()})",
        topic=topic,
        difficulty=difficulty,
        created_by=user,
    )

    # Bulk-create questions
    question_objects = [
        Question(
            quiz=quiz,
            question_text=q['question'],
            options=q['options'],
            correct_answer=q['correct_answer'],
            explanation=q.get('explanation', ''),
        )
        for q in questions_data
    ]
    Question.objects.bulk_create(question_objects)

    return quiz
