import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Initialize Vertex AI
aiplatform.init(
    project=PROJECT_ID,
    location=LOCATION,
)

app = FastAPI(
    title="Synthesis & Recommendation Service",
    description="Generates scores and investment recommendations based on startup data and user weights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Weightages(BaseModel):
    team: float = Field(..., ge=0, le=1, description="Weight for the Team (0.0 to 1.0)")
    product: float = Field(..., ge=0, le=1, description="Weight for the Product/Solution (0.0 to 1.0)")
    market: float = Field(..., ge=0, le=1, description="Weight for the Market (0.0 to 1.0)")
    financials: float = Field(..., ge=0, le=1, description="Weight for Financials/Traction (0.0 to 1.0)")

class RecommendationRequest(BaseModel):
    startup_data: dict
    weights: Weightages

class PillarScore(BaseModel):
    pillar: str
    score: int = Field(..., ge=1, le=10)
    reasoning: str

class RecommendationResponse(BaseModel):
    final_verdict: str
    final_score: float
    recommendation_summary: str
    pillar_scores: list[PillarScore]

# --- Vertex AI Model ---
model = GenerativeModel("gemini-2.5-pro")  # or gemini-1.5-pro

# --- Helper Functions ---
def get_verdict(score: float) -> str:
    if score >= 8.0:
        return "Fund"
    elif score >= 6.0:
        return "Review"
    else:
        return "Pass"

# --- API Endpoints ---
@app.post("/generate-recommendation", response_model=RecommendationResponse)
async def generate_recommendation(request: RecommendationRequest):
    # Step 1: Score each pillar individually using Vertex AI
    scoring_prompt = f"""
    You are an expert VC analyst. Based on the following startup data, score each of the four pillars (Team, Product, Market, Financials) on a scale of 1 to 10.
    Provide a brief, one-sentence reasoning for each score.

    Startup Data: {request.startup_data}

    **CRITICAL INSTRUCTIONS:**
    1.  Your entire output MUST be a single, valid JSON object.
    2.  The JSON object must have a single key "pillar_scores", which is a list of four objects.
    3.  Each object in the list must have three keys: "pillar" (string), "score" (integer 1-10), and "reasoning" (string).
    4.  Do not include any text or markdown outside of the JSON object.

    Example Response:
    {{
        "pillar_scores": [
            {{"pillar": "Team", "score": 8, "reasoning": "The team has deep domain expertise and a track record of success."}},
            {{"pillar": "Product", "score": 7, "reasoning": "The solution is innovative but faces significant technical hurdles."}},
            {{"pillar": "Market", "score": 9, "reasoning": "The TAM is large and growing, with a clear need for this solution."}},
            {{"pillar": "Financials", "score": 5, "reasoning": "Early traction is promising, but the burn rate is high relative to revenue."}}
        ]
    }}
    """

    try:
        scoring_response = model.generate_content(scoring_prompt)
        cleaned_json = scoring_response.text.strip().removeprefix("```json").removesuffix("```").strip()
        scores_dict = json.loads(cleaned_json)
        pillar_scores = [PillarScore(**item) for item in scores_dict.get("pillar_scores", [])]
    except Exception as e:
        print(f"Error during pillar scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate pillar scores: {str(e)}")

    # Step 2: Calculate the weighted final score
    score_map = {ps.pillar.lower(): ps.score for ps in pillar_scores}
    weights = request.weights
    final_score = (
        score_map.get("team", 0) * weights.team +
        score_map.get("product", 0) * weights.product +
        score_map.get("market", 0) * weights.market +
        score_map.get("financials", 0) * weights.financials
    )
    final_score = round(final_score, 2)
    final_verdict = get_verdict(final_score)

    # Step 3: Generate the final recommendation summary
    synthesis_prompt = f"""
    You are a principal at a VC firm writing a final investment recommendation.
    - Startup: {request.startup_data.get('startup_name')}
    - Final Verdict: {final_verdict}
    - Final Score: {final_score}/10.0
    - Pillar Scores & Reasoning: {[ps.model_dump() for ps in pillar_scores]}
    - Your Investment Thesis (Weights): {weights.model_dump()}

    Write a 2-3 sentence investment summary that synthesizes these points into a concise, actionable recommendation for the investment committee.
    Start with the final verdict.
    """
    try:
        summary_response = model.generate_content(synthesis_prompt)
        recommendation_summary = summary_response.text.strip()
    except Exception as e:
        print(f"Error during summary generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation summary: {str(e)}")

    return RecommendationResponse(
        final_verdict=final_verdict,
        final_score=final_score,
        recommendation_summary=recommendation_summary,
        pillar_scores=pillar_scores
    )
