from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sip_advisor_agent import SIPAdvisorAgent
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Micro-SIP Investment Advisor",
    version="1.0",
    description="A service that recommends SIP investments based on user's savings capacity"
)

# Input model
class SIPAdvisorInput(BaseModel):
    savings_capacity: float = Field(..., description="User's savings capacity amount")
    frequency: str = Field(..., description="Frequency of savings (daily, weekly, monthly)")
    currency: str = Field("INR", description="Currency of savings")
    age: int = Field(..., description="User's age")
    goals: str = Field(..., description="User's investment goals")
    risk_tolerance: Optional[str] = Field(None, description="User's risk tolerance (optional)")

# Output model
class SIPAdvisorOutput(BaseModel):
    recommendation: Dict[str, Any] = Field(..., description="SIP recommendations")
    adjusted_monthly_amount: float = Field(..., description="Adjusted monthly SIP amount")
    fund_data: List[Dict[str, Any]] = Field(..., description="Data for recommended funds")
    projected_returns: Dict[str, float] = Field(..., description="Projected SIP returns")
    visualization: str = Field(..., description="Base64 encoded visualization of SIP growth")

# Initialize the SIP Advisor Agent with fallback mode (no API key needed)
sip_advisor = SIPAdvisorAgent(use_fallback=True)

@app.post("/api/sip_advisor", response_model=SIPAdvisorOutput)
async def sip_advisor_endpoint(input_data: SIPAdvisorInput):
    """Endpoint for getting SIP investment recommendations."""
    try:
        result = sip_advisor.process_user_input(
            savings_capacity=input_data.savings_capacity,
            frequency=input_data.frequency,
            currency=input_data.currency,
            age=input_data.age,
            goals=input_data.goals,
            risk_tolerance=input_data.risk_tolerance
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Micro-SIP Investment Advisor API",
        "docs": "/docs",
        "api_endpoint": "/api/sip_advisor"
    }

# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)