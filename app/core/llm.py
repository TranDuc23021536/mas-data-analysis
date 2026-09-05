import time
import logging
from langchain_groq import ChatGroq
from app.core.config import settings

logger = logging.getLogger("mas.llm")

_MAX_RETRIES = 3
_BACKOFF_SECONDS = 2


def get_llm(temperature: float = 0):
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
    )


_llm_instance = get_llm()


def invoke_with_retry(messages: list) -> str:
    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = _llm_instance.invoke(messages)
            return response.content.strip()
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed (attempt {attempt}/{_MAX_RETRIES}): {e}")
            if attempt < _MAX_RETRIES:
                time.sleep(_BACKOFF_SECONDS * attempt)

    raise RuntimeError(f"LLM call failed after {_MAX_RETRIES} attempts: {last_error}")


def strip_code_fence(text: str, lang_hint: str = "") -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if lang_hint and text.startswith(lang_hint):
            text = text[len(lang_hint):]
        text = text.strip()
    return text