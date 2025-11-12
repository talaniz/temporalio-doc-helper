from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

from app.llm.langchain_agent import BatchedOllamaEmbeddings

DOC_URLS = [
    "https://learn.temporal.io/getting_started/python/dev_environment/",
    "https://learn.temporal.io/getting_started/python/first_program_in_python/",
    "https://learn.temporal.io/getting_started/python/hello_world_in_python/",
    "https://docs.temporal.io/best-practices/managing-namespace",
    "https://docs.temporal.io/glossary"

    # keep this to 3–5 pages so it’s fast
]


def main():
    loader = WebBaseLoader(DOC_URLS)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = splitter.split_documents(docs)

    embeddings = BatchedOllamaEmbeddings()
    vectordb = Chroma.from_documents(
        split_docs,
        embedding=embeddings,
        persist_directory="chroma_temporal_docs",
    )
    print("Index built in ./chroma_temporal_docs")


if __name__ == "__main__":
    main()
