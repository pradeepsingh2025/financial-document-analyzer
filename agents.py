import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import (
    search_tool,
    read_data_tool,
    analyze_investment_tool,
    create_risk_assessment_tool,
)

load_dotenv()


# Attempt to configure the LLM dynamically based on environment keys, allowing fallback to CrewAI's defaults
llm = None
os.getenv("GEMINI_API_KEY")
llm = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Provide incredibly accurate, insightful, and actionable financial analysis based on provided documents and queries: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned financial analyst with decades of experience in investment banking "
        "and quantitative analysis. You are known for your meticulous attention to detail, "
        "your ability to uncover hidden trends in financial reports, and your deep understanding "
        "of macroeconomic factors. Your advice is relied upon by top institutional investors."
    ),
    tools=[read_data_tool, search_tool] if search_tool else [read_data_tool],
    allow_delegation=True,
    llm=llm,
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Compliance Verifier",
    goal="Rigorously inspect and verify the authenticity, completeness, and financial nature of the provided documents.",
    verbose=True,
    memory=True,
    backstory=(
        "You are an expert in financial compliance and document verification. "
        "Your sharp eye catches any irregularities or missing information in financial reporting. "
        "You ensure that all subsequent analysis is based on verified, legitimate financial data."
    ),
    tools=[read_data_tool],
    allow_delegation=True,
    llm=llm,
)

investment_advisor = Agent(
    role="Strategic Investment Advisor",
    goal="Formulate tailored, risk-adjusted investment strategies based on comprehensive financial analysis.",
    verbose=True,
    backstory=(
        "You are a fiduciary investment advisor known for constructing robust, "
        "long-term portfolios. You synthesize complex financial data into "
        "clear, actionable strategies, always prioritizing the client's "
        "risk tolerance and financial objectives over short-term trends."
    ),
    tools=[analyze_investment_tool],
    allow_delegation=False,
    llm=llm,
)


risk_assessor = Agent(
    role="Chief Risk Officer",
    goal="Identify, quantify, and mitigate potential risks associated with financial data and investment strategies.",
    verbose=True,
    backstory=(
        "You are a leading expert in risk management with a background in quantitative finance. "
        "You excel at stress-testing investment scenarios, identifying hidden vulnerabilities "
        "in financial statements, and ensuring robust downside protection for portfolios."
    ),
    tools=[create_risk_assessment_tool],
    allow_delegation=False,
    llm=llm,
)
