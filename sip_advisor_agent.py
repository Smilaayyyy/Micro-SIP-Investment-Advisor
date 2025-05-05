from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import RunnableSequence
from langchain_community.llms import Ollama  # Changed to use Ollama
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import json
from sip_utils import (
    calculate_sip_returns, get_fund_data, recommend_funds, 
    generate_sip_visualization, calculate_daily_to_monthly,
    calculate_weekly_to_monthly
)

# Define the output structure
class SIPRecommendation(BaseModel):
    monthly_sip_amount: float = Field(..., description="Recommended monthly SIP amount in the user's currency")
    investment_timeframe_years: int = Field(..., description="Recommended investment timeframe in years")
    risk_profile: str = Field(..., description="User's risk profile (conservative, moderate, or aggressive)")
    recommended_funds: List[str] = Field(..., description="List of recommended fund symbols")
    expected_return_rate: float = Field(..., description="Expected annual return rate as a percentage")

class MockLLMResponse:
    """Simple class to mimic LLM response format for the fallback mode"""
    def __init__(self, content):
        self.content = content

class SIPAdvisorAgent:
    def __init__(self, use_fallback=True):
        """Initialize the SIP Advisor Agent."""
        self.use_fallback = use_fallback
        
        if not self.use_fallback:
            try:
                # Try to initialize Ollama with the Llama2 model
                # You need to have Ollama running locally with the Llama2 model
                self.llm = Ollama(model="llama2")
                self.output_parser = PydanticOutputParser(pydantic_object=SIPRecommendation)
                
                # Create the prompt template
                template = """
                You are a financial advisor specializing in Systematic Investment Plans (SIPs).
                
                Based on the following user information, recommend an appropriate SIP strategy:
                
                - User's savings capacity: {savings_capacity} {frequency} in {currency}
                - Age: {age}
                - Investment goals: {goals}
                - Risk tolerance (if specified): {risk_tolerance}
                
                {format_instructions}
                
                Provide a recommendation that includes:
                1. A suitable monthly SIP amount based on their savings capacity
                2. An appropriate investment timeframe
                3. An assessment of their risk profile
                4. Recommended mutual funds or ETFs
                5. Expected annual return rate
                
                For recommended funds, please use only the following fund symbols: HDFC_EQUITY, ICICI_BLUECHIP, SBI_SMALLCAP, AXIS_MIDCAP, KOTAK_STANDARD, FRANKLIN_TAXSHIELD, ICICI_BALANCED, HDFC_HYBRID, SBI_DEBT, ADITYA_CORPORATE_BOND.
                
                Your response should be in the exact JSON format specified above.
                """
                
                self.prompt = ChatPromptTemplate.from_template(
                    template=template,
                    partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
                )
                
                self.chain = RunnableSequence(
                    self.prompt | self.llm | self.output_parser
                )
            except Exception as e:
                print(f"Failed to initialize Ollama: {str(e)}. Falling back to rule-based mode.")
                self.use_fallback = True
    
    def process_user_input(self, savings_capacity, frequency, currency, age, goals, risk_tolerance=None):
        """Process user input and generate SIP recommendations."""
        
        # If using fallback or Ollama initialization failed, use rule-based approach
        if self.use_fallback:
            recommendation = self._generate_rule_based_recommendation(
                savings_capacity, frequency, currency, age, goals, risk_tolerance
            )
        else:
            try:
                # Try using the LLM
                recommendation = self.chain.invoke({
                    "savings_capacity": savings_capacity,
                    "frequency": frequency,
                    "currency": currency,
                    "age": age,
                    "goals": goals,
                    "risk_tolerance": risk_tolerance or "Not specified"
                })
            except Exception as e:
                print(f"LLM inference failed: {str(e)}. Using rule-based approach.")
                recommendation = self._generate_rule_based_recommendation(
                    savings_capacity, frequency, currency, age, goals, risk_tolerance
                )
        
        # Convert to appropriate monthly amount if needed
        monthly_amount = recommendation.monthly_sip_amount
        if frequency.lower() == "daily":
            monthly_amount = calculate_daily_to_monthly(savings_capacity)
        elif frequency.lower() == "weekly":
            monthly_amount = calculate_weekly_to_monthly(savings_capacity)
        
        # Get fund data for recommended funds
        fund_data = []
        for fund_symbol in recommendation.recommended_funds:
            fund_data.append(get_fund_data(fund_symbol))
        
        # Calculate SIP returns
        returns = calculate_sip_returns(
            monthly_investment=monthly_amount,
            years=recommendation.investment_timeframe_years,
            expected_return_rate=recommendation.expected_return_rate
        )
        
        # Generate visualization
        visualization = generate_sip_visualization(
            monthly_investment=monthly_amount,
            years=recommendation.investment_timeframe_years,
            expected_return=recommendation.expected_return_rate
        )
        
        # Convert Pydantic model to dictionary
        recommendation_dict = recommendation.dict()
        
        return {
            "recommendation": recommendation_dict,
            "adjusted_monthly_amount": round(monthly_amount, 2),
            "fund_data": fund_data,
            "projected_returns": returns,
            "visualization": visualization
        }
    
    def _generate_rule_based_recommendation(self, savings_capacity, frequency, currency, age, goals, risk_tolerance=None):
        """Generate a rule-based recommendation without using an LLM."""
        
        # Convert to monthly amount
        if frequency.lower() == "daily":
            monthly_amount = calculate_daily_to_monthly(savings_capacity)
        elif frequency.lower() == "weekly":
            monthly_amount = calculate_weekly_to_monthly(savings_capacity)
        else:  # Monthly
            monthly_amount = savings_capacity
        
        # Determine risk profile based on age and risk_tolerance
        if risk_tolerance:
            risk_profile = risk_tolerance.lower()
        else:
            if age < 30:
                risk_profile = "aggressive"
            elif age < 50:
                risk_profile = "moderate"
            else:
                risk_profile = "conservative"
        
        # Normalize risk profile to one of the three categories
        if "conserv" in risk_profile:
            risk_profile = "conservative"
        elif "aggress" in risk_profile or "high" in risk_profile:
            risk_profile = "aggressive"
        else:
            risk_profile = "moderate"
        
        # Determine investment timeframe based on age
        if age < 30:
            investment_timeframe = 30
        elif age < 40:
            investment_timeframe = 20
        elif age < 50:
            investment_timeframe = 15
        else:
            investment_timeframe = 10
        
        # Determine expected return rate based on risk profile
        if risk_profile == "conservative":
            expected_return_rate = 8.0
        elif risk_profile == "moderate":
            expected_return_rate = 12.0
        else:  # aggressive
            expected_return_rate = 15.0
        
        # Get recommended funds based on risk profile
        recommended_funds = recommend_funds(risk_profile, goals)
        
        # Create a SIPRecommendation object
        recommendation = SIPRecommendation(
            monthly_sip_amount=monthly_amount,
            investment_timeframe_years=investment_timeframe,
            risk_profile=risk_profile,
            recommended_funds=recommended_funds,
            expected_return_rate=expected_return_rate
        )
        
        return recommendation