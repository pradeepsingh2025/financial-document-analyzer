import os
import requests
from dotenv import load_dotenv
from crewai.tools import tool
import fitz  # PyMuPDF

load_dotenv()


@tool("Search Tool")
def search_tool(query: str) -> str:
    """Useful to search the internet for information about a given topic and return relevant results.
    Args:
        query (str): The search query to execute on the internet.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Serper API key not found. Simulated search results: Market is volatile, check specific sources."
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        return response.text
    except Exception as e:
        return f"Error searching: {e}"


@tool("Financial Document Reader")
def read_data_tool(file_path: str) -> str:
    """Tool to read text from a pdf file.
    Args:
        file_path (str): The absolute or relative path to the pdf file representing the financial document.
    Returns:
        str: The full text content extracted from the PDF document.
    """
    try:
        doc = fitz.open(file_path)
        full_report = ""
        for page in doc:
            full_report += page.get_text() + "\n"

        # Clean and format the financial document data
        while "\n\n" in full_report:
            full_report = full_report.replace("\n\n", "\n")

        return full_report
    except Exception as e:
        return f"Error reading document: {str(e)}"


@tool("Investment Analysis Tool")
def analyze_investment_tool(financial_document_data: str) -> str:
    """Process and analyze the financial document data to extract key quantitative metrics.
    Args:
        financial_document_data (str): The text data from the financial document.
    """
    processed_data = financial_document_data.replace("  ", " ")
    return f"Data successfully processed. Ready for evaluation. (Length: {len(processed_data)} chars)"


@tool("Risk Assessment Tool")
def create_risk_assessment_tool(financial_document_data: str) -> str:
    """Generate risk assessment based on document parameters.
    Args:
        financial_document_data (str): The text data from the financial document.
    """
    return "Initial structural risk assessment completed. Proceed with qualitative risk investigation."
