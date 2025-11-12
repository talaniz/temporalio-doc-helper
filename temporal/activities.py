from temporalio import activity
from app.llm.langchain_agent import answer_temporal_question


@activity.defn(name="run_doc_qa")
async def run_doc_qa(question: str) -> str:
    """Activity that runs the LangChain doc QA."""
    try:
        answer = await answer_temporal_question(question)
        return answer
    except Exception as e:
        activity.logger.exception("Doc QA failed")
        return f"Sorry, something went wrong while looking up the docs: {e!s}"
