# File: core-library/core/prompts.py

from core.schemas import DealData

def get_extraction_prompt():
    """
    Generates a stricter prompt for extracting structured data from a document.
    """
    return f"""
    You are an expert investment analyst and a master of structured data formats. 
    Your task is to process the provided document and extract key information.

    Analyze the document thoroughly and generate a single, valid JSON object as your response.
    
    **CRITICAL INSTRUCTIONS:**
    1.  Your entire output MUST be a single JSON object.
    2.  Do NOT use single quotes. All keys and string values MUST be enclosed in double quotes (").
    3.  Do not include any text, commentary, or markdown formatting (like ```json) outside of the JSON object.
    4.  Your response must start with `{{` and end with `}}`.
    5.  If a specific piece of information is not found, use a null value or an empty list where appropriate.
    6.  **If the 'industry_vertical' is not explicitly mentioned in the text, you MUST infer the most appropriate one by analyzing the startup's problem and solution. Assign a value from this list: ["FoodTech", "FinTech", "HealthTech", "EdTech", "Q-Commerce", "e-Commerce", "SaaS", "DeepTech"].**
    7.  **Within the 'financials' object, prioritize extracting metrics with these exact keys if the information is available: "Annual Revenue", "Valuation USD", "Hiring Velocity".**
    8.  **Act as a skeptical analyst for the 'risk_analysis' section. Identify potential red flags, inconsistencies between documents, or concerns. Examples include: inflated market size, high burn rate with low revenue, key metrics missing, or inconsistencies in user numbers. For each risk, provide a 'risk', 'explanation', and 'severity'.**
    
    Adhere strictly to this JSON Schema:
    {DealData.model_json_schema()}
    """