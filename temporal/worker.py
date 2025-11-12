import asyncio
import sys
from pathlib import Path

from temporalio.client import Client
from temporalio.worker import Worker

from temporal.activities import classify_question, run_doc_qa
from temporal.workflows import (
    AnswerTemporalQuestionWorkflow,
    ClassifyQuestionWorkflow,
)

TASK_QUEUE = "qa-task-queue"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def main() -> None:
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AnswerTemporalQuestionWorkflow, ClassifyQuestionWorkflow],
        activities=[run_doc_qa, classify_question],
    )

    print(f"Worker starting on task queue: {TASK_QUEUE}")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
