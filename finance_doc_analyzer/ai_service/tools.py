import os
import re
import pdfplumber
from dotenv import load_dotenv
from crewai.tools import BaseTool

# Load environment variables from .env file
load_dotenv()


# ------------------------
# Helper function to extract text from a PDF
# ------------------------
def extract_pdf_text(path: str) -> str:
    """
    Extract full text from a PDF file. Returns error messages if file is missing or unreadable.
    """
    if not os.path.exists(path):
        return f"Error: File not found at path: {path}"

    full_text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                content = page.extract_text() or ""
                # Replace consecutive newlines with single newline
                content = content.replace("\n\n", "\n")
                full_text += f"--- Page {page_num + 1} ---\n{content}\n"

        if not full_text.strip():
            return "Error: No text content could be extracted from the PDF"

        return full_text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# ------------------------
# Financial Document Tool
# ------------------------
class FinancialDocumentTool(BaseTool):
    name: str = "read_financial_document"
    description: str = "Reads PDF financial documents and returns the full text."

    def _run(self, path: str) -> str:
        return extract_pdf_text(path)

    async def _arun(self, path: str) -> str:
        return self._run(path)

    def run(self, path: str) -> str:
        """Convenience wrapper for synchronous usage"""
        return self._run(path)


# ------------------------
# Investment Analysis Tool
# ------------------------
class InvestmentTool(BaseTool):
    name: str = "analyze_investment"
    description: str = "Analyzes financial document data for investment insights."

    def _run(self, document_text: str, query: str = "") -> str:
        """
        Simple keyword-based investment analysis.
        """
        processed_data = document_text.replace("  ", " ")
        analysis = f"Investment Analysis for query: '{query}'\n\n"

        key_terms = ['revenue', 'profit', 'loss', 'cash flow', 'assets', 'liabilities', 'equity']
        found_terms = [term for term in key_terms if term.lower() in processed_data.lower()]

        if found_terms:
            analysis += f"Key financial indicators found: {', '.join(found_terms)}\n"
        else:
            analysis += "Limited financial data identified in document.\n"

        analysis += "Investment analysis functionality partially implemented based on document content."
        return analysis

    def run(self, path: str, query: str = "") -> str:
        document_text = extract_pdf_text(path)
        return self._run(document_text, query)

    async def _arun(self, path: str, query: str = "") -> str:
        return self.run(path, query)


# ------------------------
# Risk Assessment Tool
# ------------------------
class RiskTool(BaseTool):
    name: str = "risk_assessment"
    description: str = "Evaluates financial risk from a document using keyword and numeric analysis."

    def _run(self, document_text: str, query: str = "") -> str:
        """
        Performs a simple risk assessment using keyword scanning and numeric heuristics.
        """
        document_lower = document_text.lower()
        numbers = [float(x.replace(',', '')) for x in
                   re.findall(r"\$?([\d,]+\.?\d*)", document_text)] if document_text else []

        risk_score = 0
        risk_factors = []

        # Keywords scanning
        risk_keywords = [
            'risk', 'market risk', 'credit risk', 'operational risk',
            'financial risk', 'uncertainty', 'volatility', 'exposure'
        ]
        found_keywords = [k for k in risk_keywords if k in document_lower]
        if found_keywords:
            risk_score += min(len(found_keywords) * 10, 50)
            risk_factors.append(f"Found risk indicators: {', '.join(found_keywords)}")

        # Numeric heuristics
        if numbers and numbers[0] > 1_000_000:
            risk_score += 20
            risk_factors.append("High debt levels detected")

        # Negative words
        negative_words = ['loss', 'deficit', 'decline', 'decrease']
        if any(word in document_lower for word in negative_words):
            risk_score += 20
            risk_factors.append("Negative financial indicators detected")

        # Categorize risk
        if risk_score >= 70:
            category = "High Risk"
        elif risk_score >= 30:
            category = "Medium Risk"
        else:
            category = "Low Risk"

        result = f"Risk Assessment for query: '{query}'\n"
        result += f"Risk Score: {risk_score}/100\nCategory: {category}\n"
        if risk_factors:
            result += f"Risk Factors: {'; '.join(risk_factors)}"

        return result


# ------------------------
# Document Verification Tool
# ------------------------
class DocumentVerifierTool(BaseTool):
    name: str = "verify_financial_document"
    description: str = "Verifies financial document content for completeness and relevance."

    def _run(self, document_text: str, query: str = "") -> str:
        processed_data = document_text.replace("  ", " ").lower()
        issues_found = []

        # Check document length
        if len(processed_data.strip()) < 500:
            issues_found.append("Document seems too short, may be incomplete.")

        # Check for financial sections
        sections = [
            'balance sheet', 'income statement', 'cash flow', 'profit & loss',
            'financial summary', 'statement of operations'
        ]
        found_sections = [s for s in sections if s in processed_data]
        if not found_sections:
            issues_found.append(
                "No standard financial sections detected (balance sheet, income statement, cash flow, etc.)")

        # Check for years and currency
        if not re.search(r'\b20\d{2}\b', processed_data):
            issues_found.append("No year detected.")
        if not re.search(r'\$\d+', processed_data):
            issues_found.append("No currency amounts detected.")

        verification_result = f"Document Verification for query: '{query}'\n"
        if issues_found:
            verification_result += "Potential Issues:\n- " + "\n- ".join(issues_found) + "\n"
        else:
            verification_result += "Document appears complete and relevant for analysis.\n"

        verification_result += f"Found Sections: {', '.join(found_sections) if found_sections else 'None'}"
        return verification_result