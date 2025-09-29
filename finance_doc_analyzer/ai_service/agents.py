import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import FinancialDocumentTool, InvestmentTool, RiskTool, DocumentVerifierTool

# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_DIR = os.path.dirname(BASE_DIR)                # fastapi-react-mongodb-docker/

load_dotenv(dotenv_path=os.path.join(PROJECT_DIR, ".env"))

# Ensure GEMINI_API_KEY is set
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")

# ------------------------
# Initialize LLM using Gemini
# ------------------------
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    max_tokens=8000,
    api_key=os.getenv("GEMINI_API_KEY")
)

# ------------------------
# Agent: Senior Financial Analyst
# ------------------------
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze the financial document at {path} and answer the user's query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a highly skilled financial analyst with deep expertise in corporate finance, "
        "equity research, and market trends. You meticulously examine financial statements, "
        "highlight critical performance metrics, and provide actionable, data-backed insights. "
        "Your reports are structured, professional, and tailored to help users make informed decisions."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=3,
    max_rpm=5,
    allow_delegation=True
)

# ------------------------
# Agent: Document Verifier
# ------------------------
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify the financial document at {path} and confirm its relevance and accuracy for the query: {query}",
    verbose=True,
    backstory=(
        "You are a meticulous compliance officer specializing in financial documentation. "
        "Your role is to ensure documents are accurate, complete, and reliable. "
        "You identify inconsistencies, flag missing or unusual data, and validate the document's suitability "
        "for detailed financial analysis."
    ),
    tools=[DocumentVerifierTool()],
    llm=llm,
    max_iter=3,
    max_rpm=5,
    allow_delegation=True
)

# ------------------------
# Agent: Investment Advisor
# ------------------------
investment_advisor = Agent(
    role="Investment Advisor",
    goal="Analyze the financial document at {path} and provide actionable, risk-adjusted investment advice for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified investment professional with extensive experience in portfolio management, "
        "asset allocation, and market strategy. You evaluate financial reports to generate practical, "
        "risk-adjusted recommendations. Your guidance helps users optimize investments while considering "
        "their objectives, risk tolerance, and current market conditions."
    ),
    tools=[InvestmentTool()],
    llm=llm,
    max_iter=3,
    max_rpm=5,
    allow_delegation=False
)

# ------------------------
# Agent: Risk Assessor
# ------------------------
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Assess potential risks in the financial document at {path} related to the user query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a professional risk manager with expertise in market, credit, operational, and regulatory risks. "
        "You scrutinize financial documents to identify potential threats and vulnerabilities. "
        "Your recommendations are clear, practical, and focused on mitigating risks while ensuring compliance and sustainability."
    ),
    tools=[RiskTool()],
    llm=llm,
    max_iter=3,
    max_rpm=5,
    allow_delegation=False
)
