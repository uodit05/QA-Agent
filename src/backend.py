import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
import uvicorn
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import requests
import json

from src.utils import load_documents, chunk_documents

app = FastAPI(title="Autonomous QA Agent Backend")

# Configuration
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file (explicit path)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
else:
    load_dotenv() # Fallback to default behavior
    print("Loading .env from default location")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

# Configuration
CHROMA_DB_DIR = "chroma_db"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-flash-latest")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

# Initialize Embeddings (using a lightweight HF model)
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Vector DB (Persistent)
def get_vector_db():
    return Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding_function)

class TestGenRequest(BaseModel):
    query: str
    model: Optional[str] = "gemini-flash-latest"

class ScriptGenRequest(BaseModel):
    test_case: str
    html_content: str
    target_url: str = "http://example.com"
    model: Optional[str] = "gemini-flash-latest"

class ChatRequest(BaseModel):
    query: str
    model: Optional[str] = "gemini-flash-latest"

@app.post("/ingest")
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Ingests uploaded documents into the vector database."""
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    saved_paths = []
    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)
        
        # Load and chunk documents
        raw_docs = load_documents(saved_paths)
        if not raw_docs:
            return {"message": "No text could be extracted from the uploaded files."}
            
        chunks = chunk_documents(raw_docs)
        
        # Add to Vector DB
        db = get_vector_db()
        db.add_documents(chunks)
        db.persist()
        
        return {"message": f"Successfully ingested {len(files)} files. Created {len(chunks)} chunks."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.post("/generate-tests")
async def generate_tests(request: TestGenRequest):
    """Generates test cases based on the query and knowledge base."""
    try:
        db = get_vector_db()
        # Retrieve relevant docs
        retriever = db.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(request.query)
        context = "\n\n".join([f"Source: {d.metadata['source']}\nContent: {d.page_content}" for d in docs])
        
        prompt = f"""
        You are an expert QA Automation Engineer. Your task is to generate comprehensive test cases based strictly on the provided context.
        
        Context:
        {context}
        
        User Query: {request.query}
        
        Instructions:
        1. Generate test cases in a structured format (JSON).
        2. Each test case must have: Test_ID, Feature, Test_Scenario, Expected_Result, and Grounded_In (source document).
        3. Do NOT hallucinate features not present in the context.
        4. Output ONLY the JSON array of test cases.
        """
        
        # Call Gemini
        try:
            model = genai.GenerativeModel(request.model)
            response = model.generate_content(prompt)
            result = response.text
            
            # Clean up JSON (extract from markdown code blocks if present)
            import re
            code_block_pattern = r"```(json|JSON)?\n(.*?)```"
            match = re.search(code_block_pattern, result, re.DOTALL)
            if match:
                result = match.group(2).strip()
                
            try:
                parsed_result = json.loads(result)
                if isinstance(parsed_result, dict):
                    # Try to find the list of test cases
                    for key in ["test_cases", "tests", "result", "response"]:
                        if key in parsed_result and isinstance(parsed_result[key], list):
                            parsed_result = parsed_result[key]
                            break
                    # If still a dict, wrap it in a list or handle gracefully
                    if isinstance(parsed_result, dict):
                         parsed_result = [parsed_result]
                
                return {"result": parsed_result, "context": [d.metadata['source'] for d in docs]}
            except json.JSONDecodeError:
                print(f"JSON Decode Error. Raw LLM Response: {result}")
                return {
                    "result": [],
                    "context": [],
                    "warning": "Failed to parse LLM response. Check backend logs for raw output."
                }
        except Exception as e:
            print(f"Gemini API Error: {e}")
            # Fallback for demo/testing if LLM is not running
            print("LLM not reachable, returning mock response.")
            return {
                "result": [
                    {
                        "Test_ID": "TC-MOCK-001",
                        "Feature": "Mock Feature",
                        "Test_Scenario": "Mock Scenario based on " + request.query,
                        "Expected_Result": "Mock Result",
                        "Grounded_In": "mock_doc.md"
                    }
                ],
                "context": ["mock_doc.md"],
                "warning": "LLM was not reachable. This is a mock response."
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script")
async def generate_script(request: ScriptGenRequest):
    """Generates a Selenium script for a specific test case."""
    try:
        db = get_vector_db()
        # Retrieve relevant docs (might be useful for specific rules)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(request.test_case)
        context = "\n\n".join([f"Source: {d.metadata['source']}\nContent: {d.page_content}" for d in docs])
        
        prompt = f"""
        You are an expert Selenium Python Automation Engineer.
        
        Task: Write a Selenium Python script to automate the following test case.
        
        Test Case:
        {request.test_case}
        
        Target URL: {request.target_url}
        
        Target HTML Page Source:
        {request.html_content}
        
        Additional Context (Rules/Data):
        {context}
        
        Instructions:
        1. Use 'webdriver.Chrome()' (assume chromedriver is in PATH).
        2. Start by navigating to the Target URL: driver.get("{request.target_url}")
        3. Use explicit waits (WebDriverWait) for stability.
        4. Use specific selectors based on the provided HTML (ID, Name, CSS).
        5. Include assertions to verify the Expected Result.
        6. Output ONLY the Python code. No markdown formatting.
        """
        
        try:
            model = genai.GenerativeModel(request.model)
            response = model.generate_content(prompt)
            script = response.text
            
            # Clean up script (extract from markdown code blocks if present)
            import re
            code_block_pattern = r"```(python|Python)\n(.*?)```"
            match = re.search(code_block_pattern, script, re.DOTALL)
            if match:
                script = match.group(1).strip()
            else:
                # Fallback: try generic code block
                code_block_pattern_generic = r"```\n(.*?)```"
                match_generic = re.search(code_block_pattern_generic, script, re.DOTALL)
                if match_generic:
                    script = match_generic.group(1).strip()
            
            return {"script": script}
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "script": "# LLM not reachable. Mock script.\nfrom selenium import webdriver\n\nprint('Mock script for: " + request.test_case[:20] + "...')",
                "warning": "LLM was not reachable."
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_docs(request: ChatRequest):
    """Chat with the knowledge base."""
    try:
        db = get_vector_db()
        retriever = db.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(request.query)
        context = "\n\n".join([f"Source: {d.metadata['source']}\nContent: {d.page_content}" for d in docs])
        
        prompt = f"""
        You are a helpful assistant for a QA team. Answer the user's question based strictly on the provided context.
        
        Context:
        {context}
        
        User Question: {request.query}
        
        Instructions:
        1. Answer clearly and concisely.
        2. If the answer is not in the context, say "I don't have enough information in the provided documents."
        """
        
        try:
            model = genai.GenerativeModel(request.model)
            response = model.generate_content(prompt)
            answer = response.text
            return {"answer": answer, "context": [d.metadata['source'] for d in docs]}
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "answer": "Mock Answer: Based on the documents, the answer is...",
                "context": ["mock_doc.md"],
                "warning": "LLM was not reachable."
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
