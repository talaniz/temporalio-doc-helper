import asyncio
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

_classifier_prompt = PromptTemplate.from_template(
    """
    You are a classifier for a Slack bot that answers developer questions.

    Question: "{question}"

    Decide whether this question is about the Temporal Technologies
    platform or documentation. Answer with exactly one word:

    YES — if it is clearly about Temporal or something that the docs could answer
    NO — if it is general, off-topic, or cannot be answered from the Temporal docs.
    """
)

def build_classifier_chain():
    llm = Ollama(model="llama3")
    return RunnableSequence(
        _classifier_prompt,
        llm,
        StrOutputParser(),
    )

async def is_temporal_question(question: str, chain=None) -> bool:
    """
    Uses a LangChain 'chain' to decide if this is a Temporal question.
    `chain` is injectable so we can swap in a fake for tests.
    """
    if chain is None:
        chain = build_classifier_chain()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, chain.invoke, {"question": question})
    return result.strip().upper().startswith("YES")
