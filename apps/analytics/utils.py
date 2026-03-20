"""Analytics utility functions."""
from utils.helpers import calculate_percentage


def build_topic_stats(topic, correct, total, attempts_count, avg_score):
    """Build a stats dict for a single topic."""
    return {
        'topic': topic,
        'attempts': attempts_count,
        'total_questions_answered': total,
        'correct_answers': correct,
        'accuracy': calculate_percentage(correct, total),
        'average_score': round(avg_score, 2) if avg_score else 0.0,
    }
