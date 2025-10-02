from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from celery.result import AsyncResult
import os
import uuid
from typing import Optional
from dotenv import load_dotenv
from celery_app import celery_app
import celery_tasks

# Load environment variables
load_dotenv()

# Ensure GEMINI_API_KEY is set
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")

app = FastAPI(title="Financial Document Analyzer")

# Defaults
DEFAULT_QUERY = "Analyze this financial document for investment insights"
DEFAULT_FILE_PATH = "data/TSLA-Q2-2025-Update.pdf"


# --- File Handling ---
async def handle_file_upload(file: Optional[UploadFile]):
    """
    Save uploaded file (if provided) or fallback to default file.
    Returns (filename, file_bytes, use_uploaded_file).
    """
    use_uploaded_file = False
    filename = os.path.basename(DEFAULT_FILE_PATH)
    file_bytes = None

    if file:
        file_id = str(uuid.uuid4())
        filename = f"financial_document_{file_id}.pdf"
        use_uploaded_file = True
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty")
            file_bytes = content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading uploaded file: {str(e)}")
    else:
        # fallback to default
        if not os.path.exists(DEFAULT_FILE_PATH):
            raise HTTPException(status_code=404, detail=f"Default file not found at {DEFAULT_FILE_PATH}")
        with open(DEFAULT_FILE_PATH, "rb") as f:
            file_bytes = f.read()

    return filename, file_bytes, use_uploaded_file


# --- Health Check ---
@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running with Celery + Redis"}


# --- Celery Endpoint Factory ---
def create_celery_endpoint(task_fn, default_query: str):
    """
    Factory for endpoints that enqueue Celery tasks.
    """
    async def endpoint(
        query: str = Form(default=default_query),
        file: Optional[UploadFile] = File(None)
    ):
        filename, file_bytes, use_uploaded_file = await handle_file_upload(file)

        # Enqueue Celery task
        task = task_fn.apply_async(args=[query, filename, file_bytes])

        return {
            "status": "submitted",
            "task_id": task.id,
            "query": query,
            "using_default_file": not use_uploaded_file,
            "uploaded_filename": file.filename if use_uploaded_file else None
        }

    return endpoint


# --- Register Celery-backed Endpoints ---
app.post("/analyze")(create_celery_endpoint(celery_tasks.analyze_financial_document_task, DEFAULT_QUERY))
app.post("/investment")(create_celery_endpoint(celery_tasks.investment_analysis_task, "Provide detailed investment insights"))
app.post("/risk")(create_celery_endpoint(celery_tasks.risk_assessment_task, "Perform a detailed risk assessment"))
app.post("/verify")(create_celery_endpoint(celery_tasks.verification_task, "Verify document completeness and relevance"))


# --- Task Result Endpoint ---
@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif result.state == "STARTED":
        return {"task_id": task_id, "status": "running"}
    elif result.state == "SUCCESS":
        return {"task_id": task_id, "status": "success", "result": result.result}
    elif result.state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    else:
        return {"task_id": task_id, "status": result.state}
