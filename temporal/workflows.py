from __future__ import annotations
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError


@workflow.defn
class AnswerTemporalQuestionWorkflow:
    @workflow.run
    async def run(self, question: str) -> str:
        # Call the activity by its registered name; avoids importing the
        # heavy LangChain / Chroma dependencies in the workflow sandbox.
        result = await workflow.execute_activity(
            "run_doc_qa",
            question,
            schedule_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
        )
        return result


@workflow.defn(name="ClassifyQuestionWorkflow")
class ClassifyQuestionWorkflow:
    @workflow.run
    async def run(self, question: str) -> dict:
        try:
            is_temporal = await workflow.execute_activity(
                "classify_question",
                question,
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    backoff_coefficient=2.0,
                    maximum_attempts=5,
                ),
            )
            return {"ok": True, "is_temporal": bool(is_temporal)}
        except ActivityError:
            # Don’t crash the workflow; report back that the classifier is unavailable
            workflow.logger.exception("Classification failed")
            return {"ok": False, "reason": "classifier_unavailable"}
