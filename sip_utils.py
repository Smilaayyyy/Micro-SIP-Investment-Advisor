import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from typing import Dict, List, Any

# Sample fund data - in a real application, you'd fetch this from an API
FUND_DATABASE = {
    "HDFC_EQUITY": {
        "name": "HDFC Equity Fund",
        "category": "Equity - Large Cap",
        "nav": 845.67,
        "expense_ratio": 1.65,
        "risk_level": "Moderate to High",
        "historical_return": 14.8,
        "min_investment": 5000,
        "fund_manager": "Prashant Jain"
    },
    "ICICI_BLUECHIP": {
        "name": "ICICI Prudential Bluechip Fund",
        "category": "Equity - Large Cap",
        "nav": 58.23,
        "expense_ratio": 1.78,
        "risk_level": "Moderate to High",
        "historical_return": 13.5,
        "min_investment": 1000,
        "fund_manager": "Anish Tawakley"
    },
    "SBI_SMALLCAP": {
        "name": "SBI Small Cap Fund",
        "category": "Equity - Small Cap",
        "nav": 98.45,
        "expense_ratio": 1.92,
        "risk_level": "High",
        "historical_return": 17.2,
        "min_investment": 5000,
        "fund_manager": "R. Srinivasan"
    },
    "AXIS_MIDCAP": {
        "name": "Axis Midcap Fund",
        "category": "Equity - Mid Cap",
        "nav": 65.34,
        "expense_ratio": 1.82,
        "risk_level": "High",
        "historical_return": 16.8,
        "min_investment": 1000,
        "fund_manager": "Shreyash Devalkar"
    },
    "KOTAK_STANDARD": {
        "name": "Kotak Standard Multicap Fund",
        "category": "Equity - Multi Cap",
        "nav": 43.21,
        "expense_ratio": 1.68,
        "risk_level": "Moderate to High",
        "historical_return": 15.4,
        "min_investment": 5000,
        "fund_manager": "Harsha Upadhyaya"
    },
    "FRANKLIN_TAXSHIELD": {
        "name": "Franklin India Taxshield Fund",
        "category": "Equity - ELSS",
        "nav": 76.89,
        "expense_ratio": 1.95,
        "risk_level": "Moderate to High",
        "historical_return": 13.9,
        "min_investment": 500,
        "fund_manager": "R. Janakiraman"
    },
    "ICICI_BALANCED": {
        "name": "ICICI Prudential Balanced Advantage Fund",
        "category": "Hybrid - Dynamic Asset Allocation",
        "nav": 45.67,
        "expense_ratio": 1.72,
        "risk_level": "Moderate",
        "historical_return": 11.8,
        "min_investment": 1000,
        "fund_manager": "Sankaran Naren"
    },
    "HDFC_HYBRID": {
        "name": "HDFC Hybrid Equity Fund",
        "category": "Hybrid - Aggressive",
        "nav": 67.23,
        "expense_ratio": 1.85,
        "risk_level": "Moderate",
        "historical_return": 12.5,
        "min_investment": 5000,
        "fund_manager": "Chirag Setalvad"
    },
    "SBI_DEBT": {
        "name": "SBI Magnum Income Fund",
        "category": "Debt - Medium to Long Duration",
        "nav": 52.19,
        "expense_ratio": 1.52,
        "risk_level": "Low to Moderate",
        "historical_return": 8.2,
        "min_investment": 5000,
        "fund_manager": "Dinesh Ahuja"
    },
    "ADITYA_CORPORATE_BOND": {
        "name": "Aditya Birla Sun Life Corporate Bond Fund",
        "category": "Debt - Corporate Bond",
        "nav": 87.65,
        "expense_ratio": 1.38,
        "risk_level": "Low",
        "historical_return": 7.8,
        "min_investment": 1000,
        "fund_manager": "Sunaina da Cunha"
    }
}

def calculate_daily_to_monthly(daily_amount: float) -> float:
    """Convert daily savings capacity to monthly equivalent."""
    return daily_amount * 30

def calculate_weekly_to_monthly(weekly_amount: float) -> float:
    """Convert weekly savings capacity to monthly equivalent."""
    return weekly_amount * 4.33  # Average number of weeks in a month

def get_fund_data(fund_symbol: str) -> Dict[str, Any]:
    """Get fund data for a given fund symbol."""
    # Normalize the fund symbol
    fund_symbol = fund_symbol.upper().replace(" ", "_")
    
    # Return fund data if available, otherwise return a default placeholder
    if fund_symbol in FUND_DATABASE:
        return FUND_DATABASE[fund_symbol]
    else:
        # Return a placeholder for unknown funds
        return {
            "name": fund_symbol.replace("_", " "),
            "category": "Unknown",
            "nav": 0.0,
            "expense_ratio": 0.0,
            "risk_level": "Unknown",
            "historical_return": 0.0,
            "min_investment": 0.0,
            "fund_manager": "Unknown"
        }

def recommend_funds(risk_profile: str, investment_goals: str) -> List[str]:
    """Recommend funds based on risk profile and investment goals."""
    # This is a simplified recommendation logic
    # In a real application, this would be more sophisticated
    
    if risk_profile.lower() == "conservative":
        return ["ADITYA_CORPORATE_BOND", "SBI_DEBT", "HDFC_HYBRID"]
    elif risk_profile.lower() == "moderate":
        return ["ICICI_BALANCED", "HDFC_HYBRID", "KOTAK_STANDARD"]
    elif risk_profile.lower() == "aggressive":
        return ["SBI_SMALLCAP", "AXIS_MIDCAP", "HDFC_EQUITY"]
    else:
        # Default to a balanced portfolio
        return ["ICICI_BLUECHIP", "HDFC_HYBRID", "ADITYA_CORPORATE_BOND"]

def calculate_sip_returns(monthly_investment: float, years: int, expected_return_rate: float) -> Dict[str, float]:
    """Calculate SIP returns over a given time period."""
    monthly_rate = expected_return_rate / 12 / 100
    months = years * 12
    
    # Calculate invested amount
    invested_amount = monthly_investment * months
    
    # Calculate maturity value using SIP formula
    maturity_value = monthly_investment * ((pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate)
    
    # Calculate wealth gained
    wealth_gained = maturity_value - invested_amount
    
    return {
        "invested_amount": round(invested_amount, 2),
        "expected_returns": round(wealth_gained, 2),
        "maturity_value": round(maturity_value, 2)
    }

def generate_sip_visualization(monthly_investment: float, years: int, expected_return: float) -> str:
    """Generate a visualization of SIP growth and return a base64 encoded image."""
    # Create data for visualization
    months = years * 12
    monthly_rate = expected_return / 12 / 100
    
    # Calculate invested amount over time
    invested_amounts = [monthly_investment * (m + 1) for m in range(months)]
    
    # Calculate SIP value over time
    sip_values = []
    for m in range(months):
        sip_value = monthly_investment * ((pow(1 + monthly_rate, m + 1) - 1) / monthly_rate) * (1 + monthly_rate)
        sip_values.append(sip_value)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Create x-axis in years
    x = np.array(range(months)) / 12
    
    # Plot the data
    plt.plot(x, invested_amounts, label='Invested Amount', color='blue')
    plt.plot(x, sip_values, label='SIP Value', color='green')
    plt.fill_between(x, invested_amounts, sip_values, color='lightgreen', alpha=0.5)
    
    # Customize the plot
    plt.title('SIP Growth Projection')
    plt.xlabel('Years')
    plt.ylabel('Amount')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format y-axis with tick marks in thousands or lakhs based on the scale
    plt.ticklabel_format(axis='y', style='plain')
    
    # Convert plot to base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64