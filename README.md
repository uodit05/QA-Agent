# Autonomous QA Agent 🤖

An intelligent, autonomous QA agent that generates comprehensive test cases and Selenium test scripts from project documentation and HTML structure using Google's Gemini API and RAG (Retrieval-Augmented Generation).

## Features

- 📚 **Knowledge Base Ingestion**: Upload project documents (PDF, Markdown, HTML, JSON, TXT)
- 🧪 **Smart Test Case Generation**: AI-powered test case creation grounded in your documentation
- 🐍 **Selenium Script Generation**: Automatic Python/Selenium script generation from test cases
- 💬 **Chat with Docs**: Interactive Q&A with your knowledge base
- 🎨 **Modern UI**: Beautiful, responsive Streamlit interface
- 🚀 **Cloud-Ready**: Deploy to Render with one click

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Streamlit     │────────>│   FastAPI       │────────>│  Gemini API     │
│   Frontend      │         │   Backend       │         │  (LLM)          │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                    │
                                    v
                            ┌─────────────────┐
                            │   ChromaDB      │
                            │ Vector Store    │
                            └─────────────────┘
```

## Prerequisites

- Python 3.11+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git

## Quick Start (Local)

### 1. Clone the Repository

```bash
git clone https://github.com/uodit05/QA-Agent.git
cd QA-Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Create `src/.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
uvicorn src.backend:app --host 0.0.0.0 --port 10000
```

**Terminal 2 - Frontend:**
```bash
BACKEND_URL=http://localhost:10000 streamlit run src/app.py --server.port 8501
```

### 5. Access the App

Open your browser and navigate to:
```
http://localhost:8501
```

## Usage

### 1. Build Knowledge Base
- Upload your project documents (specs, requirements, API docs, etc.)
- Click "🚀 Build Knowledge Base"
- Wait for ingestion to complete

### 2. Generate Test Cases
- Describe what you want to test (e.g., "Generate test cases for login functionality")
- Click "✨ Generate Tests"
- Review the generated test cases

### 3. Generate Selenium Scripts
- Expand a test case
- Provide the target HTML context
- Click "🔧 Generate Script"
- Download and run the script

### 4. Chat with Docs
- Switch to "💬 Chat Assistant" tab
- Ask questions about your documentation
- Get AI-powered answers grounded in your knowledge base

## Deployment to Render

This application is ready for deployment to Render with automatic configuration.

### Quick Deploy

1. **Push to Git**:
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **"New +"** → **"Blueprint"**
   - Connect your Git repository
   - Render will auto-detect `render.yaml`
   - Set `GEMINI_API_KEY` in backend environment variables
   - Click **"Apply"**

3. **Access Your App**:
   - Frontend URL: `https://qa-agent-frontend.onrender.com`
   - Backend URL: `https://qa-agent-backend.onrender.com`

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Project Structure

```
QA-Agent/
├── src/
│   ├── app.py              # Streamlit frontend
│   ├── backend.py          # FastAPI backend
│   ├── utils.py            # Utility functions
│   └── .env                # Environment variables (not in git)
├── data/                   # Sample documents
│   ├── product_specs.md
│   ├── ui_ux_guide.txt
│   └── api_endpoints.json
├── chroma_db/              # Vector database (auto-created)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **LLM**: Google Gemini API (`gemini-flash-latest`)
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **RAG Framework**: LangChain
- **Document Parsing**: PyMuPDF, BeautifulSoup4

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `BACKEND_URL` | Backend service URL | No | `http://localhost:10000` |
| `PORT` | Service port (Render) | No | `8000` (backend), `8501` (frontend) |

## Troubleshooting

### "LLM was not reachable"
- Verify `GEMINI_API_KEY` is set in `src/.env`
- Check your API key is valid
- Ensure you have internet connectivity

### "Could not connect to backend"
- Verify backend is running on the correct port
- Check `BACKEND_URL` is set correctly
- Look for errors in backend terminal

### ChromaDB Errors
- Delete `chroma_db/` directory and rebuild knowledge base
- Ensure you have write permissions in the project directory