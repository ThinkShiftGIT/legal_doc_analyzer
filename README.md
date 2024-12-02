# Legal Document Analyzer

An enterprise-scale multi-modal legal document analysis system that leverages AI to process, analyze, and extract insights from legal documents in various formats.

## 🚀 Features

- **Multi-Modal Document Processing**
  - PDF documents with text extraction and chunking
  - Audio files (MP3, WAV) with speech-to-text using Whisper
  - Video files (MP4, AVI) with audio extraction and transcription

- **Advanced Analysis**
  - Semantic search across all documents
  - AI-powered document analysis using Mistral AI
  - Context-aware question answering
  - Document summarization

- **Modern Architecture**
  - FastAPI-based REST API
  - Vector store (ChromaDB) for efficient similarity search
  - Modular design for easy extension
  - Asynchronous processing

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **AI/ML**: Mistral AI, Whisper, Sentence Transformers
- **Storage**: ChromaDB (Vector Store)
- **Document Processing**: PyPDF, MoviePy
- **Package Management**: Poetry

## 📋 Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- Mistral AI API key
- FFmpeg for audio/video processing

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/ThinkShiftGIT/legal_doc_analyzer.git
cd legal_doc_analyzer
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
   - Create a .env file in the project root
   - Add your Mistral AI API key:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

## 🚦 Usage

Start the server:
```bash
poetry run uvicorn legal_doc_analyzer.api.main:app --reload
```

Access the API:
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative documentation: http://127.0.0.1:8000/redoc

### Available Endpoints:

#### Document Upload
```http
POST /api/v1/upload
```
- Supports PDF, audio (MP3, WAV), and video (MP4, AVI) files
- Automatically processes and stores document content
- Returns processing status and metadata

#### Document Search
```http
POST /api/v1/search
```
- Semantic search across all processed documents
- Query using natural language
- Returns relevant document chunks with metadata

#### Document Analysis
```http
POST /api/v1/analyze
```
- AI-powered document analysis
- Ask questions about document content
- Get context-aware responses with source citations

## 🧪 Development

Adding Dependencies:
```bash
poetry add package_name
```

Running Tests:
```bash
# Create test data
poetry run python tests/create_test_data.py

# Run tests
poetry run pytest
```

## 📁 Project Structure
```
legal_doc_analyzer/
├── src/
│   └── legal_doc_analyzer/
│       ├── api/               # FastAPI routes and app setup
│       ├── processors/        # Document processing modules
│       └── storage/          # Vector store implementation
├── tests/                    # Test files and data
├── pyproject.toml           # Poetry dependencies
└── README.md               # This file
```

## 🔒 Security Notes

- Store sensitive credentials in .env file (never commit to repository)
- Implement proper authentication in production
- Restrict CORS settings for production use
- Validate and sanitize all file uploads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

ThinkShiftGIT - Initial work and maintenance