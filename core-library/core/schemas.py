from pydantic import BaseModel, Field
from typing import List, Optional

class TeamMember(BaseModel):
    name: str = Field(description="Full name of the team member.")
    role: str = Field(description="Role or title of the team member (e.g., CEO, CTO).")
    bio: Optional[str] = Field(description="A brief summary of their background and experience.", default=None)

class Financials(BaseModel):
    mrr: Optional[float] = Field(description="Monthly Recurring Revenue in USD.", default=None)
    arr: Optional[float] = Field(description="Annual Recurring Revenue in USD.", default=None)
    funding_ask_usd: Optional[float] = Field(description="The amount of funding the startup is asking for in USD.", default=None)

class DealData(BaseModel):
    startup_name: str = Field(description="The official name of the startup.")
    summary: str = Field(description="A one-sentence summary of what the startup does.")
    team: List[TeamMember] = Field(description="A list of founders and key hires.")
    problem: str = Field(description="The problem the startup is trying to solve.")
    solution: str = Field(description="The startup's proposed solution.")
    market_size_tam: Optional[float] = Field(description="Total Addressable Market in USD.", default=None)
    financials: Financials

