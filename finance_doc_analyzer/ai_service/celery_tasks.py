from celery_app import celery_app
from task import analyze_financial_document, investment_analysis, risk_assessment, verification
from crewai import Crew, Process
from agents import financial_analyst, investment_advisor, risk_assessor, verifier
import logging

logger = logging.getLogger(__name__)

def run_crew_bytes(query, filename, file_bytes, agent, task):
    """
    Kick off a Crew task and return JSON-serializable result using file bytes.
    """
    try:
        # Save to temp file for LLM processing
        temp_path = f"data/{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential
        )
        result = crew.kickoff(inputs={"query": query, "path": temp_path})

        serialized = serialize_crew_output(result)
        if not serialized.get("text"):
            logger.warning("LLM returned empty response")
            return {"text": None, "metadata": None, "error": "LLM returned empty response"}
        
        return serialized
    except Exception as e:
        logger.exception("Crew task failed")
        return {"text": None, "metadata": None, "error": str(e)}

def serialize_crew_output(output):
    if hasattr(output, "text") or hasattr(output, "metadata"):
        return {
            "text": getattr(output, "text", str(output)),
            "metadata": getattr(output, "metadata", None),
        }
    return {"text": str(output), "metadata": None}

# Celery tasks
@celery_app.task(bind=True)
def analyze_financial_document_task(self, query, filename, file_bytes):
    return run_crew_bytes(query, filename, file_bytes, financial_analyst, analyze_financial_document)

@celery_app.task(bind=True)
def investment_analysis_task(self, query, filename, file_bytes):
    return run_crew_bytes(query, filename, file_bytes, investment_advisor, investment_analysis)

@celery_app.task(bind=True)
def risk_assessment_task(self, query, filename, file_bytes):
    return run_crew_bytes(query, filename, file_bytes, risk_assessor, risk_assessment)

@celery_app.task(bind=True)
def verification_task(self, query, filename, file_bytes):
    return run_crew_bytes(query, filename, file_bytes, verifier, verification)
