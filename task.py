from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import (
    search_tool,
    read_data_tool,
    analyze_investment_tool,
    create_risk_assessment_tool,
)

verification = Task(
    description=(
        "Verify the financial document located at {file_path}. "
        "Examine the document to ensure it is authentic, complete, and contains valid financial data. "
        "Identify the primary type of the document (e.g., 10-K, earnings report, etc.)."
    ),
    expected_output=(
        "A formal verification report confirming the authenticity of the document, "
        "its document type, and a summary of its structural completeness."
    ),
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False,
)

analyze_financial_document = Task(
    description=(
        "Analyze the verified financial document at {file_path} to answer the user's query: '{query}'. "
        "Extract key financial metrics, evaluate the company's financial health, and identify significant trends. "
        "If the user query requires industry context, you may search for recent market news."
    ),
    expected_output=(
        "A detailed financial analysis report answering the user's query, "
        "including organized sections for key metrics, financial health indicators, and market context."
    ),
    agent=financial_analyst,
    tools=[read_data_tool, search_tool] if search_tool else [read_data_tool],
    async_execution=False,
    context=[verification],
)

risk_assessment = Task(
    description=(
        "Review the financial analysis and assess the potential risks associated with the company and its market environment. "
        "Identify specific operational, financial, and market risks based on the text at {file_path} and the prior analysis."
    ),
    expected_output=(
        "A comprehensive risk assessment report detailing identified risks, their potential impact, "
        "and suggested mitigation strategies."
    ),
    agent=risk_assessor,
    tools=[create_risk_assessment_tool, read_data_tool],
    async_execution=False,
    context=[analyze_financial_document],
)

investment_analysis = Task(
    description=(
        "Based on the financial analysis and the risk assessment, provide strategic investment recommendations. "
        "Address the user's initial query: '{query}'. "
        "Provide a clear, risk-adjusted investment thesis."
    ),
    expected_output=(
        "A formal investment advisory report containing a clear investment thesis, "
        "recommended actions (e.g., buy/hold/sell), and justification based on analysis and risk."
    ),
    agent=investment_advisor,
    tools=[analyze_investment_tool, read_data_tool],
    async_execution=False,
    context=[analyze_financial_document, risk_assessment],
)
