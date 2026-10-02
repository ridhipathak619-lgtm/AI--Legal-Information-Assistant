"""One-off script: read PDFs in data/, embed them, and upload to Pinecone."""
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from src import config
from src.helper import get_embeddings, load_pdfs, split_documents


def main():
    pc = Pinecone(api_key=config.PINECONE_API_KEY)

    if not pc.has_index(config.INDEX_NAME):
        pc.create_index(
            name=config.INDEX_NAME,
            dimension=config.EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    docs = load_pdfs()
    if not docs:
        raise SystemExit("No PDFs found in data/. Add some and run again.")
    chunks = split_documents(docs)
    print(f"Loaded {len(docs)} pages -> {len(chunks)} chunks")

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        index_name=config.INDEX_NAME,
    )
    print("Index ready.")


if __name__ == "__main__":
    main()
