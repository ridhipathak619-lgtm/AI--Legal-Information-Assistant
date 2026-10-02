# AI Legal Information Assistant

A Retrieval-Augmented Generation (RAG) web app that answers legal questions in plain language, using only the legal documents you give it. Every answer lists the document and page it came from.

> **Disclaimer:** This project provides general legal information, not legal advice. Consult a qualified lawyer for your situation.

## How it works

```
 PDFs in data/ ──► split into chunks ──► Hugging Face embeddings ──► Pinecone index
                                                                         │
 Question (Flask UI) ──► embed ──► top-k similar chunks ◄────────────────┘
                                        │
                           LangChain prompt + context ──► Groq LLM ──► concise answer + sources
```

| Layer | Tool |
|---|---|
| Embeddings | Hugging Face `sentence-transformers/all-MiniLM-L6-v2` (384 dims) |
| Vector search | Pinecone (serverless, cosine) |
| LLM inference | Groq (`llama-3.3-70b-versatile` by default) |
| Orchestration | LangChain |
| Web app | Flask + vanilla HTML/CSS/JS |

## Project structure

```
ai-legal-information-assistant/
├── app.py              # Flask app and /chat endpoint
├── store_index.py      # Builds the Pinecone index from data/
├── src/
│   ├── config.py       # Settings and environment variables
│   ├── helper.py       # PDF loading, chunking, embeddings
│   └── prompt.py       # System prompt
├── templates/chat.html
├── static/             # style.css, script.js
├── data/               # Put your legal PDFs here
├── requirements.txt
└── .env.example
```

## Setup

1. **Clone and install**
   ```bash
   git clone https://github.com/<your-username>/ai-legal-information-assistant.git
   cd ai-legal-information-assistant
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Add API keys.** Copy `.env.example` to `.env` and fill in your [Pinecone](https://www.pinecone.io/) and [Groq](https://console.groq.com/) keys.
3. **Add documents.** Put legal PDFs in `data/`.
4. **Build the index** (run once, and again when documents change):
   ```bash
   python store_index.py
   ```
5. **Run the app**
   ```bash
   python app.py
   ```
   Open http://localhost:8080.

## Configuration

Edit `src/config.py` or `.env`: `GROQ_MODEL`, `PINECONE_INDEX_NAME`, chunk size/overlap, and `TOP_K` (chunks retrieved per question).
If you change the embedding model, update `EMBEDDING_DIM` and rebuild the index.

## Deployment

```bash
gunicorn -w 1 -b 0.0.0.0:8080 app:app
```
Set the same environment variables on your host (Render, Railway, AWS, etc.). Never commit `.env`.

## Limitations

- Answers are only as good as the documents indexed. Laws change, so keep sources current.
- The model can still make mistakes; check the cited sources.
- No conversation memory yet: each question is answered independently.

## Roadmap ideas

- Chat history and follow-up questions
- Document upload from the UI
- Evaluation set for answer quality

## License

MIT
