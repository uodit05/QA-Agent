# Autonomous QA Agent

An intelligent agent that constructs a "testing brain" from project documentation to generate test cases and Selenium scripts automatically.

## Features
- **Knowledge Base Ingestion**: Uploads and parses PDF, Markdown, TXT, JSON, and HTML files.
- **RAG Pipeline**: Uses ChromaDB and HuggingFace embeddings to retrieve relevant context.
- **Test Case Generation**: Generates structured test plans based strictly on provided documentation (no hallucinations).
- **Selenium Script Generation**: Creates executable Python Selenium scripts grounded in the target HTML structure.
- **Modern UI**: Built with Streamlit for easy interaction.

## Project Structure
```
.
├── checkout.html           # Target web project for testing
├── data/                   # Support documents (specs, guides, API)
│   ├── product_specs.md
│   ├── ui_ux_guide.txt
│   └── api_endpoints.json
├── src/
│   ├── app.py              # Streamlit Frontend
│   ├── backend.py          # FastAPI Backend
│   └── utils.py            # Document parsing & chunking utilities
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (for local LLM)

### Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd QA-Agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Ollama (in a separate terminal):
   ```bash
   ollama run llama3
   ```

## How to Run

1. **Start the Backend Server**:
   ```bash
   uvicorn src.backend:app --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend UI** (in a new terminal):
   ```bash
   streamlit run src/app.py
   ```

3. Open your browser at `http://localhost:8501`.

## Usage Guide

### Phase 1: Build Knowledge Base
1. Go to the **Knowledge Base** tab.
2. Upload `checkout.html` and all files from the `data/` directory.
3. Click **Build Knowledge Base**. Wait for the success message.

### Phase 2: Generate Test Cases
1. Go to the **Test Case Agent** tab.
2. Enter a query (e.g., "Generate test cases for the discount code feature").
3. Click **Generate Test Cases**. The agent will display structured test scenarios grounded in the uploaded docs.

### Phase 3: Generate Selenium Script
1. Go to the **Script Generator** tab.
2. Select a generated test case from the dropdown.
3. Click **Generate Script**.
4. Copy the generated Python code and run it to verify the test.

## Support Documents Explained
- **checkout.html**: The target e-commerce page we are testing.
- **product_specs.md**: Defines business rules (e.g., "SAVE15 gives 15% off").
- **ui_ux_guide.txt**: Defines visual requirements (e.g., "Error messages must be red").
- **api_endpoints.json**: Defines the expected backend API behavior.