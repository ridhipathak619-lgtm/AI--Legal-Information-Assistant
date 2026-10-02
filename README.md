# AI Legal Information Assistant

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

A Retrieval-Augmented Generation (RAG) web application that answers legal questions in plain language, using only the legal documents you provide. It combines **Hugging Face embeddings**, **Pinecone vector search**, **Groq LLM inference**, **LangChain** and **Flask** to give concise, context-aware answers through a simple web interface. Every answer shows the document and page it came from.

> **Disclaimer:** This project provides general legal information, not legal advice. Laws change and the model can make mistakes. Consult a qualified lawyer for your situation.

---

## Features

- Answers grounded in your own legal PDFs (acts, statutes, government guides, FAQs)
- Concise responses written in plain language
- Source citations (file name and page) shown beside each answer
- Says so when the answer is not in the documents, instead of guessing
- Fast inference through Groq
- Clean, responsive chat interface with light and dark mode

## How it works

```
PDFs in data/ ──► split into chunks ──► Hugging Face embeddings ──► Pinecone index
                                                                        │
Question (Flask UI) ──► embed ──► top-k similar chunks ◄────────────────┘
                                       │
                          LangChain prompt + context ──► Groq LLM ──► answer + sources
```

1. **Indexing (once):** `store_index.py` reads the PDFs, splits them into overlapping chunks, converts them to vectors and uploads them to Pinecone.
2. **Retrieval:** when a user asks a question, it is embedded and the most similar chunks are fetched from Pinecone.
3. **Generation:** the chunks and the question go into a LangChain prompt, and the Groq-hosted LLM writes a short answer based only on that context.

## Tech stack

| Layer | Tool |
|---|---|
| Embeddings | Hugging Face `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) |
| Vector database | Pinecone (serverless, cosine similarity) |
| LLM inference | Groq (`llama-3.3-70b-versatile` by default) |
| Orchestration | LangChain |
| Backend | Flask |
| Frontend | HTML, CSS, vanilla JavaScript |

## Project structure

```
ai-legal-information-assistant/
├── app.py              # Flask app and /chat endpoint
├── store_index.py      # Builds the Pinecone index from data/
├── src/
│   ├── config.py       # Settings and environment variables
│   ├── helper.py       # PDF loading, chunking, embeddings
│   └── prompt.py       # System prompt
├── templates/
│   └── chat.html       # Chat page
├── static/
│   ├── style.css
│   └── script.js
├── data/               # Put your legal PDFs here
├── requirements.txt
├── .env.example
└── LICENSE
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- A [Pinecone](https://www.pinecone.io/) account and API key
- A [Groq](https://console.groq.com/) account and API key

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/ai-legal-information-assistant.git
cd ai-legal-information-assistant

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your API keys

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

```env
PINECONE_API_KEY=your-pinecone-key
GROQ_API_KEY=your-groq-key
PINECONE_INDEX_NAME=legal-assistant
GROQ_MODEL=llama-3.3-70b-versatile
```

Never commit `.env`. It is already listed in `.gitignore`.

### 3. Add your documents

Place legal PDFs in the `data/` folder. Only use documents you are permitted to use.

### 4. Build the index

```bash
python store_index.py
```

Run this once, and again whenever you add or change documents.

### 5. Run the app

```bash
python app.py
```

Open **http://localhost:8080** in your browser.

## Example questions

- What are the rights of a person who has been arrested?
- What is the time limit for filing a consumer complaint?
- What does the law say about a tenant's security deposit?

The answers depend entirely on the documents you indexed.

## Configuration

Settings live in `src/config.py` and `.env`:

| Setting | Default | Purpose |
|---|---|---|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model used for answers |
| `PINECONE_INDEX_NAME` | `legal-assistant` | Name of the Pinecone index |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 800 / 120 | How documents are split |
| `TOP_K` | 4 | Chunks retrieved per question |

If you change the embedding model, update `EMBEDDING_DIM` to match and rebuild the index with a new index name or after deleting the old one.

## API

`POST /chat`

```json
{ "message": "What are the rights of an arrested person?" }
```

Response:

```json
{
  "answer": "…",
  "sources": ["constitution.pdf, p. 12"]
}
```

`GET /health` returns `{"status": "ok"}`.

## Deployment

```bash
gunicorn -w 1 -b 0.0.0.0:8080 app:app
```

Set the same environment variables on your host (Render, Railway, AWS, etc.). The first start downloads the embedding model, so allow a little extra time.

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `No PDFs found in data/` | Add `.pdf` files to `data/` before running `store_index.py`. |
| Dimension mismatch error from Pinecone | The index was created with a different embedding size. Delete it or use a new `PINECONE_INDEX_NAME`. |
| "Could not get an answer" in the UI | Check both API keys in `.env` and that the index exists and has data. |
| Model not found error from Groq | The model name may be retired. Set a current one in `GROQ_MODEL`. |
| Empty or irrelevant answers | Scanned PDFs without text need OCR first. Try a larger `TOP_K`. |

## Limitations

- Answers are only as good and as current as the indexed documents.
- No conversation memory yet: each question is answered independently.
- Not a substitute for professional legal advice.

## Roadmap

- Chat history and follow-up questions
- Document upload from the web interface
- Evaluation set to measure answer quality
- Multi-language support

## Contributing

Issues and pull requests are welcome. Fork the repo, create a feature branch, and open a pull request describing your change.

## License

Released under the [MIT License](LICENSE).
