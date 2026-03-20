"""Analytics service functions."""
from django.db.models import Count, Sum, Avg, Q, F
from apps.attempts.models import Attempt, Answer
from utils.helpers import calculate_percentage


def get_user_overview(user):
    """
    Return an overview of the user's quiz performance.

    Returns dict with:
      - total_quizzes_attempted
      - total_completed
      - overall_accuracy (%)
      - average_score
      - total_correct / total_answered
    """
    completed = Attempt.objects.filter(user=user, status='completed')

    total_attempted = Attempt.objects.filter(user=user).count()
    total_completed = completed.count()

    # Aggregate answers across all completed attempts
    answer_stats = (
        Answer.objects
        .filter(attempt__user=user, attempt__status='completed')
        .aggregate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True)),
        )
    )
    total_answered = answer_stats['total'] or 0
    total_correct = answer_stats['correct'] or 0

    avg_score = completed.aggregate(avg=Avg('score'))['avg'] or 0.0

    return {
        'total_quizzes_attempted': total_attempted,
        'total_completed': total_completed,
        'total_questions_answered': total_answered,
        'total_correct_answers': total_correct,
        'overall_accuracy': calculate_percentage(total_correct, total_answered),
        'average_score': round(avg_score, 2),
    }


def get_topic_performance(user):
    """
    Return per-topic performance breakdown for the user.

    Returns a list of dicts, each containing topic stats.
    """
    topics = (
        Attempt.objects
        .filter(user=user, status='completed')
        .values('quiz__topic')
        .annotate(
            attempts_count=Count('id'),
            avg_score=Avg('score'),
        )
        .order_by('quiz__topic')
    )

    result = []
    for entry in topics:
        topic = entry['quiz__topic']

        # Get answer-level stats for this topic
        answer_stats = (
            Answer.objects
            .filter(
                attempt__user=user,
                attempt__status='completed',
                attempt__quiz__topic=topic,
            )
            .aggregate(
                total=Count('id'),
                correct=Count('id', filter=Q(is_correct=True)),
            )
        )

        result.append({
            'topic': topic,
            'attempts': entry['attempts_count'],
            'average_score': round(entry['avg_score'], 2) if entry['avg_score'] else 0.0,
            'total_questions_answered': answer_stats['total'] or 0,
            'correct_answers': answer_stats['correct'] or 0,
            'accuracy': calculate_percentage(
                answer_stats['correct'] or 0,
                answer_stats['total'] or 0,
            ),
        })

    return result
