"""
AI quiz generation service.

Orchestrates provider calls with retry logic and fallback.
"""
import logging
import time
from django.conf import settings
from .providers import GeminiProvider, MockProvider, ProviderUnavailableError, RateLimitError

logger = logging.getLogger(__name__)


def generate_quiz_questions(topic, difficulty, count):
    """
    Generate quiz questions using AI with retry + fallback.

    Flow:
      1. Try Gemini Provider if configured.
      2. On rate-limit (429), wait with exponential backoff then retry.
      3. On any other failure (or if unconfigured), fall back to the mock provider.

    Returns a list of question dicts.
    """
    max_retries = getattr(settings, 'AI_MAX_RETRIES', 3)

    # Determine which provider to attempt
    if getattr(settings, 'GEMINI_API_KEY', ''):
        provider = GeminiProvider()
        provider_name = "Gemini"
    else:
        provider = MockProvider()
        provider_name = "Mock"

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "%s generation attempt %d/%d for topic='%s', difficulty='%s', count=%d",
                provider_name, attempt, max_retries, topic, difficulty, count,
            )
            questions = provider.generate(topic, difficulty, count)
            logger.info("%s generation succeeded on attempt %d", provider_name, attempt)
            return questions

        except RateLimitError:
            wait_time = 2 ** attempt  # exponential backoff: 2, 4, 8 …
            logger.warning("Rate limit hit. Waiting %ds before retry…", wait_time)
            time.sleep(wait_time)

        except ProviderUnavailableError:
            logger.warning("AI provider unavailable. Falling back to mock.")
            break

        except Exception as exc:
            logger.error("AI generation error on attempt %d: %s", attempt, exc)
            if attempt == max_retries:
                break

    # Fallback to mock provider
    logger.info("Using mock provider for topic='%s'", topic)
    mock = MockProvider()
    return mock.generate(topic, difficulty, count)
