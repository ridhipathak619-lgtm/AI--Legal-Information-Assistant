import os

from flask import Flask, jsonify, render_template, request
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore

from src import config
from src.helper import get_embeddings
from src.prompt import SYSTEM_PROMPT

app = Flask(__name__)

# Pinecone reads PINECONE_API_KEY and ChatGroq reads GROQ_API_KEY from the environment.
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=config.INDEX_NAME, embedding=get_embeddings()
)
retriever = vectorstore.as_retriever(
    search_type="similarity", search_kwargs={"k": config.TOP_K}
)
llm = ChatGroq(model=config.GROQ_MODEL, temperature=0.2)
prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "{question}")]
)
chain = prompt | llm


def answer_question(question: str):
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)
    reply = chain.invoke({"context": context, "question": question})

    sources, seen = [], set()
    for d in docs:
        name = os.path.basename(d.metadata.get("source", "document"))
        page = d.metadata.get("page")
        label = f"{name}, p. {page + 1}" if isinstance(page, int) else name
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return reply.content, sources


@app.get("/")
def index():
    return render_template("chat.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    if not question:
        return jsonify(error="Type a question first."), 400
    try:
        answer, sources = answer_question(question)
    except Exception as exc:  # surface a readable error to the UI
        app.logger.exception("Chat failed")
        return jsonify(error="Could not get an answer. Check your API keys and index."), 500
    return jsonify(answer=answer, sources=sources)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
