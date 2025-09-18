import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery, aiplatform
from fastapi.middleware.cors import CORSMiddleware
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-analyst-85388")
TABLE_ID = "startup_data.peer_metrics"

# Init Vertex AI (ADC handles authentication)
aiplatform.init(
    project=PROJECT_ID,
    location=os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
)

# Use Vertex AI Gemini
model = GenerativeModel("gemini-2.5-pro")  # or gemini-1.5-pro

# BigQuery client
client = bigquery.Client()

# --- FastAPI App Setup ---
app = FastAPI(title="Detailed Benchmarking Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class BenchmarkRequest(BaseModel):
    industry_vertical: str
    sector: str
    annual_revenue: int | None = None
    hiring_velocity: int | None = None
    valuation_usd: int | None = None
    startup_name: str

class PeerComparison(BaseModel):
    startup_name: str
    annual_revenue: int | None
    valuation_usd: int | None
    hiring_velocity: int | None
    revenue_multiple: float | None

class RiskItem(BaseModel):
    risk: str
    explanation: str
    severity: str

class RiskAnalysisRequest(BaseModel):
    startup_data: dict

class RiskAnalysisResponse(BaseModel):
    risk_analysis: list[RiskItem]

class BenchmarkResponse(BaseModel):
    peer_details: list[PeerComparison]
    final_conclusion: str


# --- API Endpoints ---
@app.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_metrics(request: BenchmarkRequest):
    query = f"""
        SELECT
            startup_name, annual_revenue, valuation_usd, hiring_velocity,
            SAFE_DIVIDE(valuation_usd, annual_revenue) as revenue_multiple
        FROM `{TABLE_ID}`
        WHERE sector = @sector AND industry_vertical = @vertical
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sector", "STRING", request.sector),
            bigquery.ScalarQueryParameter("vertical", "STRING", request.industry_vertical),
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        peer_details = [PeerComparison(**dict(row)) for row in results]

        if not peer_details:
            return BenchmarkResponse(peer_details=[], final_conclusion="No comparable peers found in the dataset.")

        # Handle None values safely
        revenue_str = f"${request.annual_revenue:,}" if request.annual_revenue else "N/A"
        hiring_str = f"{request.hiring_velocity} new hires in 6 months" if request.hiring_velocity else "N/A"
        valuation_str = f"${request.valuation_usd:,}" if request.valuation_usd else "N/A"

        prompt = f"""
        You are a venture capital analyst. Here is the data for a startup named '{request.startup_name}':
        - Annual Revenue: {revenue_str}
        - Valuation: {valuation_str}
        - Hiring Velocity: {hiring_str}

        Here is the data for its peer companies:
        {', '.join([p.model_dump_json() for p in peer_details])}

        Based on this data, write a 2-3 sentence conclusion comparing '{request.startup_name}' to its peers.
        Is it ahead or behind? Focus on valuation, revenue multiples, and hiring velocity.
        """

        response = model.generate_content(prompt)

        return BenchmarkResponse(
            peer_details=peer_details,
            final_conclusion=response.text.strip()
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/analyze-risks", response_model=RiskAnalysisResponse)
async def analyze_risks(request: RiskAnalysisRequest):
    """
    Analyzes startup data to identify potential risks.
    """
    prompt = f"""
    You are a skeptical venture capital analyst. Your task is to identify potential risks, red flags, or concerns based on the provided startup data.

    **CRITICAL INSTRUCTIONS:**
    1.  Analyze the following data: {request.startup_data}
    2.  Identify 3-5 potential risks. Examples include: inflated market size, high burn rate with low revenue, key metrics missing, extreme valuation compared to revenue, or competitive landscape concerns.
    3.  For each risk, provide a 'risk' (short title), 'explanation' (why it's a concern), and 'severity' ('Low', 'Medium', or 'High').
    4.  Your entire output MUST be a single, valid JSON object with a single key "risk_analysis" which is a list of risk items.
    5.  Do not include any text, commentary, or markdown formatting (like ```json) outside of the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        cleaned_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        return RiskAnalysisResponse.model_validate_json(cleaned_json)
    except Exception as e:
        print(f"An error occurred during risk analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze risks: {e}")
