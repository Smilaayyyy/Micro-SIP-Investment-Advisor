import streamlit as st
import requests
import json
import base64
from PIL import Image
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="SIP Investment Advisor",
    page_icon="💰",
    layout="wide"
)

# API endpoint
API_ENDPOINT = "https://micro-sip-investment-advisor.onrender.com"

# App title and description
st.title("Micro-SIP Investment Advisor")
st.markdown("""
This application helps you plan your Systematic Investment Plan (SIP) based on your financial goals and savings capacity.
Simply fill in the form below to get personalized investment recommendations.
""")

# Create a sidebar for user inputs
st.sidebar.header("Your Information")

# Input form in the sidebar
with st.sidebar.form("user_input_form"):
    # Savings capacity
    savings_amount = st.number_input("Savings Amount", min_value=100.0, value=5000.0, step=100.0)
    
    # Frequency
    frequency = st.selectbox("Savings Frequency", ["Daily", "Weekly", "Monthly"], index=2)
    
    # Currency
    currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"], index=0)
    
    # Age
    age = st.slider("Your Age", min_value=18, max_value=80, value=30)
    
    # Investment goals - text area for more detailed input
    goals = st.text_area("Your Investment Goals", 
                        "Retirement planning with moderate growth and some capital preservation.")
    
    # Risk tolerance
    risk_options = [
        "Conservative - I prefer stability with minimal risk",
        "Moderate - I can accept some fluctuations for better returns",
        "Aggressive - I'm comfortable with volatility for maximum returns"
    ]
    risk_tolerance = st.selectbox("Risk Tolerance", risk_options, index=1)
    
    # Extract just the first word of risk_tolerance
    risk_profile = risk_tolerance.split(" ")[0]
    
    # Submit button
    submit_button = st.form_submit_button("Get SIP Recommendations")

# Process form submission
if submit_button:
    # Show a spinner while waiting for the API response
    with st.spinner("Analyzing your financial profile..."):
        try:
            # Prepare the request data
            request_data = {
                "savings_capacity": savings_amount,
                "frequency": frequency.lower(),
                "currency": currency,
                "age": age,
                "goals": goals,
                "risk_tolerance": risk_profile
            }
            
            # Make the API request
            response = requests.post(API_ENDPOINT, json=request_data)
            
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Display the results in the main area
                st.header("Your SIP Recommendation")
                
                # Create three columns for better layout
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader("Investment Strategy")
                    st.markdown(f"""
                    **Monthly SIP Amount:** {currency} {result['adjusted_monthly_amount']:,.2f}
                    
                    **Investment Timeframe:** {result['recommendation']['investment_timeframe_years']} years
                    
                    **Risk Profile:** {result['recommendation']['risk_profile']}
                    
                    **Expected Annual Return:** {result['recommendation']['expected_return_rate']}%
                    """)
                
                with col2:
                    st.subheader("Projected Returns")
                    returns_data = result['projected_returns']
                    st.metric("Invested Amount", f"{currency} {returns_data['invested_amount']:,.2f}")
                    st.metric("Expected Returns", f"{currency} {returns_data['expected_returns']:,.2f}", 
                             f"{returns_data['expected_returns']/returns_data['invested_amount']*100:.1f}%")
                    st.metric("Maturity Value", f"{currency} {returns_data['maturity_value']:,.2f}")
                
                with col3:
                    st.subheader("Investment Growth")
                    # Display the visualization image
                    if result['visualization']:
                        image_bytes = base64.b64decode(result['visualization'])
                        image = Image.open(BytesIO(image_bytes))
                        st.image(image, use_column_width=True)
                
                # Display recommended funds
                st.header("Recommended Funds")
                
                # Create a table of fund data
                fund_data = result['fund_data']
                if fund_data:
                    # Create a DataFrame for better display
                    fund_df = pd.DataFrame(fund_data)
                    
                    # Reorder and select columns of interest
                    columns_to_display = ['name', 'category', 'nav', 'expense_ratio', 'risk_level', 'historical_return', 'min_investment']
                    rename_dict = {
                        'name': 'Fund Name',
                        'category': 'Category',
                        'nav': 'NAV',
                        'expense_ratio': 'Expense Ratio (%)',
                        'risk_level': 'Risk Level',
                        'historical_return': 'Historical Return (%)',
                        'min_investment': f'Min Investment ({currency})'
                    }
                    
                    # Select columns that exist in the data
                    valid_columns = [col for col in columns_to_display if col in fund_df.columns]
                    
                    if valid_columns:
                        st.dataframe(fund_df[valid_columns].rename(columns=rename_dict), use_container_width=True)
                    else:
                        st.warning("Fund data is not in the expected format.")
                else:
                    st.warning("No fund data available.")
                
                # Additional advice section
                st.header("Investment Advice")
                
                # Generate some advice based on the recommendation
                if result['recommendation']['risk_profile'].lower() == "conservative":
                    advice = """
                    Your conservative risk profile suggests you prioritize capital preservation. 
                    The recommended funds focus on stability with a mix of debt instruments.
                    Consider setting up an emergency fund before starting your SIP investments.
                    """
                elif result['recommendation']['risk_profile'].lower() == "moderate":
                    advice = """
                    With a moderate risk profile, your portfolio balances growth and stability.
                    The recommended funds include a mix of equity and debt for balanced returns.
                    Consider diversifying across sectors for better risk management.
                    """
                else:  # Aggressive
                    advice = """
                    Your aggressive risk profile allows for higher equity allocation.
                    The recommended funds focus on growth-oriented equity investments.
                    Remember that market volatility is normal, and stay invested for the long term.
                    """
                
                st.markdown(advice)
                
                # Disclaimer
                st.caption("""
                **Disclaimer:** This recommendation is for informational purposes only and not financial advice. 
                Consult a qualified financial advisor before making investment decisions.
                """)
                
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Make sure the API server is running. You can start it with: `uvicorn app:app --reload`")

# Add some helpful information at the bottom
st.markdown("---")
st.markdown("""
### Understanding SIP Investments

**Systematic Investment Plan (SIP)** is an investment vehicle offered by mutual funds, allowing investors to invest small amounts periodically 
(typically monthly) instead of lump sums. SIPs help in:

1. **Disciplined Investing:** Regular investments create financial discipline
2. **Rupee Cost Averaging:** You buy more units when prices are low and fewer when prices are high
3. **Power of Compounding:** Your returns earn returns over time
4. **Flexibility:** Start, stop, or modify your investment anytime

""")

# Run with: streamlit run streamlit_app.py
