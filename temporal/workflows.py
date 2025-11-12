from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# from temporal.activities import run_doc_qa

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
