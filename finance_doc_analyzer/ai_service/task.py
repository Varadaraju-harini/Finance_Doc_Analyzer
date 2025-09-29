from crewai import Task
from agents import financial_analyst, investment_advisor, risk_assessor, verifier
from tools import FinancialDocumentTool, InvestmentTool, RiskTool, DocumentVerifierTool

# ------------------------
# 1. Financial Document Analysis
# ------------------------
analyze_financial_document = Task(
    description="""
    You are a senior financial analyst. Analyze the financial document at: {path}

    User Query: {query}

    Goal: Deliver a comprehensive, structured, and actionable financial analysis.

    Steps:
    1. Extract key financial statements, metrics, and data points using FinancialDocumentTool.
    2. Analyze revenue, profit, margins, growth rates, and other KPIs.
    3. Identify trends, anomalies, and notable patterns.
    4. Provide insights supported by the document.
    5. Contextualize metrics against industry benchmarks and market standards.
    6. Include actionable investment guidance and high-level risk considerations.
    7. Structure the report professionally with headings, bullet points, and bold keywords.

    Requirements:
    - Quote exact figures where possible.
    - Clearly note missing or inconsistent data.
    - Maintain a professional, investor-ready tone.
    - Include an executive summary (3-4 lines).
    """,
    expected_output="""
    Financial Analysis Report

    1. Executive Summary           # Brief 3-4 line overview of the document and main findings.
    2. Document Overview           # Key sections, structure, and main figures of the document.
    3. Query Response: {query}     # Direct answer to the user’s specific question.
    4. Key Metrics                 # Important KPIs like revenue, profit, margins, growth rates.
    5. Investment Insights         # Actionable recommendations or insights based on analysis.
    6. Risk Overview               # High-level risks or concerns observed in the document.
    7. Market Context              # Benchmarks, industry comparisons, macroeconomic considerations.
    8. Conclusion                  # Final summary with actionable next steps or recommendations.
    """,
    agent=financial_analyst,
    tools=[FinancialDocumentTool()],
    async_execution=False,
)

# ------------------------
# 2. Investment Analysis
# ------------------------
investment_analysis = Task(
    description="""
    Prepare a professional Investment Analysis Report for the document at: {path}

    User Query: {query}

    Steps:
    1. Extract relevant financial data.
    2. Calculate key KPIs: revenue growth, profitability, ROE, debt ratios.
    3. Conduct SWOT analysis (strengths, weaknesses, opportunities, threats).
    4. Compare performance with peers or industry benchmarks.
    5. Assess valuation: under/over/fairly valued.
    6. Provide actionable Buy/Hold/Sell recommendations with rationale.
    7. Present the report clearly for investor review.

    Requirements:
    - Include precise figures.
    - Highlight gaps or anomalies.
    - Maintain professional tone.
    """,
    expected_output="""
    Investment Analysis Report

    - Investment Thesis         # Overall recommendation (Buy/Hold/Sell) with reasoning.
    - Key Metrics               # Core financial indicators supporting the recommendation.
    - Strengths                 # Positive aspects of the company or financials (3-5 bullet points).
    - Weaknesses                # Areas of concern or potential issues (3-5 bullet points).
    - Valuation                 # Assessment of company’s value compared to peers or intrinsic value.
    - Market Position           # Competitive advantages, threats, or market opportunities.
    - Recommendation: Buy/Hold/Sell # Clear investment action with rationale and targets.
    - Risk Considerations       # Risks tied to the investment decision and possible mitigations.
    """,
    agent=investment_advisor,
    tools=[InvestmentTool()],
    async_execution=False,
)

# ------------------------
# 3. Risk Assessment
# ------------------------
risk_assessment = Task(
    description="""
    Conduct a detailed risk review of the financial document at: {path}

    User Query: {query}

    Steps:
    1. Extract document content and relevant financial data.
    2. Identify risks: financial, operational, market, regulatory.
    3. Classify each risk by severity (High / Medium / Low).
    4. Assess potential impact and suggest mitigation strategies.
    5. Present findings clearly with headings, bullet points, and tables if needed.

    Requirements:
    - Quote exact figures where applicable.
    - Highlight missing or unusual data.
    - Provide actionable, investor-ready recommendations.
    """,
    expected_output="""
    Risk Assessment Report

    - Overall Risk Rating: High / Medium / Low  # Summary risk score for the document/company.
    - Financial Risks                          # Risks related to liquidity, leverage, or credit exposure.
    - Market Risks                             # Risks from industry cycles, macroeconomic factors, or competition.
    - Operational Risks                        # Internal process, supply chain, or management-related risks.
    - Regulatory/Legal Risks                   # Compliance, legal, or audit-related risks.
    - Mitigation Strategies                     # Suggested ways to monitor, reduce, or manage risks.
    - Watchlist Metrics                         # Key KPIs to track for ongoing risk monitoring.
    """,
    agent=risk_assessor,
    tools=[RiskTool()],
    async_execution=False,
)

# ------------------------
# 4. Document Verification
# ------------------------
verification = Task(
    description="""
    Verify the financial document at: {path} for completeness, relevance, and accuracy.

    Verification Focus: {query}

    Steps:
    1. Parse the document content thoroughly.
    2. Identify document type (Balance Sheet, Income Statement, 10-K, Investor Deck, etc.).
    3. Check for completeness: Are key sections present?
    4. Validate critical data points: totals, dates, fiscal periods, currency units.
    5. Assess relevance to the user query.
    6. Flag inconsistencies, missing data, or unusual numbers.
    7. Present results in a clear, professional format.

    Requirements:
    - Provide exact classification and observations.
    - Recommend next steps if needed.
    - Maintain professional, investor-ready tone.
    """,
    expected_output="""
    Document Verification Report

    - Document Type        # Classification of the document (Balance Sheet, 10-K, Investor Deck, etc.).
    - Completeness         # Whether all key sections are present and complete.
    - Data Quality         # Accuracy and consistency of figures and data points.
    - Relevance            # Degree to which the document answers the user query.
    - Key Sections Found   # List of the main financial sections and figures identified.
    - Observations         # Notes on anomalies, missing info, or unusual patterns.
    - Recommendations      # Next steps (e.g., request updated report, proceed with analysis).
    """,
    agent=verifier,
    tools=[DocumentVerifierTool()],
    async_execution=False,
)
