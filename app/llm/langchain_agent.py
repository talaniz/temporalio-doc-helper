import asyncio

from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnablePassthrough
from langchain_ollama import OllamaLLM, OllamaEmbeddings

# Build using scripts/build_temporal_index.py
CHROMA_DIR = "chroma_temporal_docs"

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
    """Create the chain to classify Slack questions."""
    llm = OllamaLLM(model="llama3")
    return RunnableSequence(
        _classifier_prompt,
        llm,
        StrOutputParser(),
    )


async def is_temporal_question(question: str, chain=None) -> bool:
    """
    Use a LangChain chain to determine if the question should be answered.
    """
    if chain is None:
        chain = build_classifier_chain()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, 
                                        chain.invoke, {"question": question})
    return result.strip().upper().startswith("YES")


def load_temporal_vectorstore():
    """Load the persisted Chroma index for Temporal docs."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


_qa_prompt = PromptTemplate.from_template(
    """
    You are a helpful assistant answering questions about Temporal Technologies.

    Use ONLY the information from the context to answer.
    If the answer is not in the context, say you don't know.

    Question:
    {question}

    Context:
    {context}

    Answer in a concise, developer-friendly way.
    """
)


def build_doc_qa_chain():
    """
    Build a RAG chain for Temporal docs.
    """
    vectordb = load_temporal_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    llm = OllamaLLM(model="llama3")

    return (
        RunnableParallel(
            context=retriever,
            question=RunnablePassthrough(),
        )
        | _qa_prompt
        | llm
        | StrOutputParser()
    )


async def answer_temporal_question(question: str, chain=None) -> str:
    """
    Use the Temporal docs QA chain to answer a question.
    chain is injectable for tests.
    """
    if chain is None:
        chain = build_doc_qa_chain()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, chain.invoke, question)
    return result.strip()


class BatchedOllamaEmbeddings:
    """
    Thin wrapper around LangChain's OllamaEmbeddings so that:
      - Chroma can call embed_documents(List[str])
      - We can control model/base_url cleanly
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://127.0.0.1:11434",
        **kwargs,
    ):
        # Single, well-behaved inner instance
        self._inner = OllamaEmbeddings(
            model=model,
            base_url=base_url,
            **kwargs,
        )

    def embed_query(self, text: str):
        """Delegate directly to the real OllamaEmbeddings implementation."""
        return self._inner.embed_query(text)

    def embed_documents(self, texts):
        """
        Chroma calls this with List[str]. We just map each text through
        embed_query on the inner embeddings instance.
        """
        return [self._inner.embed_query(t) for t in texts]
