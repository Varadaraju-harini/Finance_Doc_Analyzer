from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import financial_analyst, verifier
from task import (
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
    verification
)

# Load environment variables from .env file
load_dotenv()

# Ensure GEMINI_API_KEY is set
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")

app = FastAPI(title="Financial Document Analyzer API")

# Thread pool to run blocking CrewAI tasks asynchronously
executor = ThreadPoolExecutor(max_workers=1)

# Default configurations
DEFAULT_QUERY = "Analyze this financial document for investment insights"
DEFAULT_FILE_PATH = "data/TSLA-Q2-2025-Update.pdf"


# --- Generic Crew Runner ---
def run_crew_generic(query: str, path: str, agent, task):
    """
    Run a CrewAI workflow synchronously with a specific agent and task.
    """
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
    )
    return crew.kickoff(inputs={"query": query, "path": path})


async def run_crew_generic_async(query: str, path: str, agent, task):
    """
    Run CrewAI workflow asynchronously using a thread pool.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, run_crew_generic, query, path, agent, task)


# --- Shared File Handling ---
async def handle_file_upload(file: Optional[UploadFile]):
    """
    Handle uploaded file or fallback to default file.
    Returns the file path, size, and a boolean indicating if the uploaded file is used.
    """
    file_path = DEFAULT_FILE_PATH
    use_uploaded_file = False

    if file:
        # Save uploaded file with unique filename
        file_id = str(uuid.uuid4())
        file_path = f"data/financial_document_{file_id}.pdf"
        use_uploaded_file = True
        try:
            os.makedirs("data", exist_ok=True)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail="Failed to save uploaded file")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")
    else:
        # Ensure default file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Default file not found at {file_path}")

    return file_path, os.path.getsize(file_path), use_uploaded_file


# --- Root Health Check ---
@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


# --- Endpoint Factory ---
def create_endpoint(agent, task, default_query_field):
    """
    Factory to generate endpoints for different CrewAI tasks.
    """

    async def endpoint(query: str = Form(default=default_query_field), file: Optional[UploadFile] = File(None)):
        file_path, file_size, use_uploaded_file = await handle_file_upload(file)
        try:
            response = await run_crew_generic_async(query, file_path, agent, task)
            return {
                "status": "success",
                "query": query,
                "file_path": file_path,
                "file_size_bytes": file_size,
                "result": str(response),
                "using_default_file": not use_uploaded_file,
                "uploaded_filename": file.filename if use_uploaded_file else None
            }
        finally:
            # Clean up temporary uploaded files
            if use_uploaded_file and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # silently ignore cleanup errors

    return endpoint


# --- Register Endpoints ---
app.post("/analyze")(create_endpoint(financial_analyst, analyze_financial_document, DEFAULT_QUERY))
app.post("/investment")(create_endpoint(financial_analyst, investment_analysis, "Provide detailed investment insights"))
app.post("/risk")(create_endpoint(financial_analyst, risk_assessment, "Perform a detailed risk assessment"))
app.post("/verify")(create_endpoint(verifier, verification, "Verify document completeness and relevance"))
