# temporal/test_temporal.py
import asyncio
import inspect
import uuid

import pytest

from temporalio.testing import WorkflowEnvironment
from temporalio.client import Client
from temporalio.worker import Worker

from temporal import activities as activities_mod
from temporal import workflows as workflows_mod


# ----------------------------
# Helpers / Fixtures
# ----------------------------

@pytest.fixture(scope="session")
def any_event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def fake_answer_monkeypatch(monkeypatch):
    """
    Patch the LLM/agent call that activities use so tests don't hit externals.
    Make it ASYNC because the activity awaits it.
    """
    async def _fake_agent_call(question: str) -> str:
        return f"[FAKE_ANSWER] {question}"

    # If activities.py imported the symbol directly, patch the module attr.
    monkeypatch.setattr(
        activities_mod, "answer_temporal_question", _fake_agent_call, raising=False
    )
    return _fake_agent_call


# ----------------------------
# Activity unit test
# ----------------------------

@pytest.mark.asyncio
async def test_run_doc_qa_activity_happy_path(fake_answer_monkeypatch):
    assert hasattr(activities_mod, "run_doc_qa"), "run_doc_qa activity not found"

    run_doc_qa = activities_mod.run_doc_qa
    question = "What are some best practices with Temporal?"

    if inspect.iscoroutinefunction(run_doc_qa):
        result = await run_doc_qa(question)  # type: ignore[arg-type]
    else:
        result = run_doc_qa(question)  # type: ignore[misc]

    assert isinstance(result, str)
    assert result.startswith("[FAKE_ANSWER]")
    assert question in result


# ----------------------------
# Workflow end-to-end test
# ----------------------------

@pytest.mark.asyncio
async def test_workflow_executes_activity_end_to_end(fake_answer_monkeypatch):
    assert hasattr(workflows_mod, "AnswerTemporalQuestionWorkflow")

    task_queue = "test-tq-" + uuid.uuid4().hex[:8]
    workflow_id = "wf-" + uuid.uuid4().hex[:8]
    question = "Name 2 failure-retry tips in Temporal."

    # NOTE: await the coroutine returned by start_time_skipping()
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client

        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[workflows_mod.AnswerTemporalQuestionWorkflow],
            activities=[activities_mod.run_doc_qa],
        )

        async with worker:
            result = await client.execute_workflow(
                workflows_mod.AnswerTemporalQuestionWorkflow.run,  # type: ignore[attr-defined]
                question,
                id=workflow_id,
                task_queue=task_queue,
            )

    assert isinstance(result, str)
    assert result.startswith("[FAKE_ANSWER]")
    assert question in result


# ----------------------------
# Worker wiring smoke test
# ----------------------------

@pytest.mark.asyncio
async def test_worker_can_register_defs_without_running():
    from temporal import worker as worker_mod  # local import on purpose

    if hasattr(worker_mod, "TASK_QUEUE"):
        assert isinstance(worker_mod.TASK_QUEUE, str)

    # NOTE: await the coroutine here too
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client

        tq = "smoke-tq-" + uuid.uuid4().hex[:8]
        wf_defs = [workflows_mod.AnswerTemporalQuestionWorkflow]
        act_defs = [activities_mod.run_doc_qa]

        worker = Worker(client, task_queue=tq, workflows=wf_defs, activities=act_defs)
        assert worker is not None


# ----------------------------
# Small guards
# ----------------------------

def test_activity_is_pure_python_callable():
    assert callable(getattr(activities_mod, "run_doc_qa", None))


def test_workflow_class_has_run_method():
    wf_cls = getattr(workflows_mod, "AnswerTemporalQuestionWorkflow", None)
    assert wf_cls is not None
    run_attr = getattr(wf_cls, "run", None)
    assert run_attr is not None, "Workflow must expose a .run method"
    assert inspect.iscoroutinefunction(run_attr), "Workflow .run should be async"
