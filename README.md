# Pet-Web — AI-Powered Document Analyser

A full-stack web application for **AI/ML-powered document analysis**.
Upload a PDF, DOCX, or plain-text document and instantly receive:

| Feature | Detail |
|---|---|
| **Statistics** | Word / sentence / paragraph / character count, reading time |
| **Keyword extraction** | TF-IDF based (scikit-learn), single- and bi-gram |
| **Extractive summarisation** | Top sentences ranked by informational density |
| **Sentiment analysis** | Polarity score + label via TextBlob |
| **Named-entity recognition** | PERSON, ORG, GPE, … via NLTK chunker |
| **Language detection** | Automatic via langdetect |

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Uvicorn, PyPDF2, python-docx, NLTK, scikit-learn, TextBlob, langdetect |
| **Frontend** | React 18, Vite |
| **Testing** | pytest, pytest-asyncio, httpx |

## Project Structure

```
Pet-Web/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── models/document.py   # Pydantic response models
│   │   ├── routes/documents.py  # /api/documents/* endpoints
│   │   └── services/
│   │       ├── document_parser.py   # Text extraction (PDF/DOCX/TXT)
│   │       └── ml_analyzer.py       # AI/ML analysis pipeline
│   ├── tests/
│   │   ├── test_api.py              # Integration tests
│   │   ├── test_document_parser.py  # Unit tests – parser
│   │   └── test_ml_analyzer.py      # Unit tests – ML services
│   ├── requirements.txt
│   └── pytest.ini
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── DocumentUpload.jsx    # Drag-and-drop upload UI
    │   │   └── AnalysisResults.jsx  # Results display
    │   └── services/api.js          # API client
    ├── .env.example
    └── package.json
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Swagger UI  at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
cp .env.example .env   # set VITE_API_URL if needed
npm install
npm run dev
# App available at http://localhost:5173
```

### Running Tests

```bash
cd backend
pytest -v
```

## API Reference

### `POST /api/documents/analyze`

Upload a document for analysis.

**Request**: `multipart/form-data` with field `file` (PDF, DOCX, or TXT, max 10 MB).

**Response** (`200 OK`):

```json
{
  "filename": "report.pdf",
  "file_type": "PDF",
  "language": "en",
  "stats": {
    "word_count": 1234,
    "sentence_count": 87,
    "paragraph_count": 22,
    "character_count": 7890,
    "reading_time_minutes": 6.17
  },
  "keywords": [{"keyword": "machine learning", "score": 0.0842}],
  "summary": "...",
  "sentiment": "positive",
  "sentiment_score": 0.213,
  "entities": [{"text": "Google", "label": "ORGANIZATION"}],
  "full_text": "..."
}
```

### `GET /api/documents/health`

Returns `{"status": "ok"}`.
