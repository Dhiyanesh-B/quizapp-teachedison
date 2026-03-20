"""Quiz utility functions."""


def format_quiz_title(topic, difficulty):
    """Generate a readable quiz title."""
    return f"{topic.title()} Quiz — {difficulty.capitalize()}"
