import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import bigquery
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# --- Configuration ---
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
TABLE_ID = "startup_data.peer_metrics"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="Detailed Benchmarking Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    startup_name: str

class PeerComparison(BaseModel):
    startup_name: str
    annual_revenue: int | None
    valuation_usd: int | None
    hiring_velocity: int | None
    revenue_multiple: float | None

class BenchmarkResponse(BaseModel):
    peer_details: list[PeerComparison]
    final_conclusion: str

# --- BigQuery & Gemini Clients ---
client = bigquery.Client()
model = genai.GenerativeModel('gemini-2.0-flash-exp')

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

        # --- FIX: Handle potential None values before formatting the prompt ---
        revenue_str = f"${request.annual_revenue:,}" if request.annual_revenue is not None else "N/A"
        hiring_str = f"{request.hiring_velocity} new hires in 6 months" if request.hiring_velocity is not None else "N/A"

        prompt = f"""
        You are a venture capital analyst. Here is the data for a startup named '{request.startup_name}':
        - Annual Revenue: {revenue_str}
        - Hiring Velocity: {hiring_str}

        Here is the data for its peer companies:
        {', '.join([p.model_dump_json() for p in peer_details])}

        Based on this data, write a 2-3 sentence conclusion comparing '{request.startup_name}' to its peers.
        Is it ahead or behind? Focus on revenue multiples and hiring velocity.
        """
        
        response = model.generate_content(prompt)
        
        return BenchmarkResponse(
            peer_details=peer_details,
            final_conclusion=response.text.strip()
        )

    except Exception as e:
        print(f"An error occurred: {e}") # Added print for better debugging
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")