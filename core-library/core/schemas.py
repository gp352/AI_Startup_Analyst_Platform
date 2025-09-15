# File: core-library/core/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any

class RiskItem(BaseModel):
    risk: str = Field(..., description="A concise description of a single potential risk, red flag, or concern.")
    explanation: str = Field(..., description="A brief explanation of why this is a risk and what its implications are.")
    severity: str = Field(..., description="The estimated severity of the risk (e.g., 'Low', 'Medium', 'High').")

class TeamMember(BaseModel):
    name: str = Field(description="Full name of the team member.")
    role: str = Field(description="Role or title of the team member (e.g., CEO, CTO).")
    bio: Optional[str] = Field(
        description="A brief summary of their background and experience.", 
        default=None
    )

class DealData(BaseModel):
    startup_name: str = Field(description="The official name of the startup.")
    summary: str = Field(description="A one-sentence summary of what the startup does.")
    
    # --- NEW FIELDS ---
    industry_vertical: Optional[str] = Field(
        default=None,
        description="The specific industry the startup operates in (e.g., HealthTech, FinTech, EdTech)."
    )
    sector: Optional[str] = Field(
        default=None,
        description="The business model sector (e.g., B2B, B2C, B2B2C)."
    )
    # --- END NEW FIELDS ---
    
    team: List[TeamMember] = Field(
        description="A list of JSON objects, where each object represents a team member with keys 'name', 'role', and 'bio'.", # Be more descriptive here
        default_factory=list
    )
    problem: str = Field(description="The problem the startup is trying to solve.")
    solution: str = Field(description="The startup's proposed solution.")
    market_size_tam: Optional[float] = Field(
        description="Total Addressable Market in USD.", 
        default=None
    )
    risk_analysis: List[RiskItem] = Field(
        description="A list of potential risks, red flags, or inconsistencies identified in the provided documents."
    )
    financials: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary of all financial metrics found. The key is the metric name (e.g., 'Revenue 2024', 'MRR', 'Funding Ask') and the value is the number or text."
    )