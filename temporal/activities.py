import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError

from app.llm.langchain_agent import (
    is_temporal_question,
    answer_temporal_question
)

logger = activity.logger


@activity.defn(name="classify_question")
async def classify_question(question: str) -> bool:
    """
    Return True/False for "is this a Temporal question?"
    Network/transport failures are raised as *retryable* so the workflow can backoff/retry.
    """
    try:
        return await is_temporal_question(question)
    except (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.RemoteProtocolError,
    ) as e:
        # Retryable so the workflow's retry policy kicks in.
        raise ApplicationError(
            "Classifier backend unreachable",
            non_retryable=False,
        ) from e
    except Exception as e:
        # Logic/other errors: non-retryable to avoid spinning.
        logger.exception("Classification activity failed")
        raise ApplicationError(str(e), non_retryable=True) from e


@activity.defn(name="run_doc_qa")
async def run_doc_qa(question: str) -> str:
    """
    Answer a Temporal question by querying Temporal docs.
    Transport errors are retryable; other exceptions are non-retryable.
    """
    try:
        return await answer_temporal_question(question)
    except (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.RemoteProtocolError,
    ) as e:
        raise ApplicationError(
            "QA backend unreachable",
            non_retryable=False,
        ) from e
    except Exception as e:
        logger.exception("Doc QA activity failed")
        raise ApplicationError(str(e), non_retryable=True) from e