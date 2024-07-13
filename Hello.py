import streamlit as st
from datetime import date
import pandas as pd
from portfolio import Portfolio
from config import adjusted_column_config
from portfolioviz import Portfolioviz

st.set_page_config(
    page_title="CRE Portfolio Manager",
    page_icon="👋",
)

st.title("CRE Portfolio Manager 🏗️")

# Get the current date
now = date.today()
start_date = date(now.year, now.month, 1)
end_date = date(start_date.year + 3, start_date.month, 1)

# User input for analysis start and end dates
analysis_start_date = st.date_input('Analysis Start Date', value=start_date)
analysis_end_date = st.date_input('Analysis End Date', value=end_date)

# Function to update the portfolio dates and recalculate cash flows
def update_portfolio_dates_and_calculate():
    if 'portfolio' in st.session_state:
        st.session_state.portfolio.analysis_start_date = analysis_start_date
        st.session_state.portfolio.analysis_end_date = analysis_end_date
        return st.session_state.portfolio.aggregate_hold_period_cash_flows(analysis_start_date, analysis_end_date)
    return None

# Initialize properties in session state if not already present
if 'properties' in st.session_state:
    properties = st.session_state.properties
    # Initialize portfolio in session state if not already present
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio(
            name='Dunphy Property Fund',
            start_date=analysis_start_date,
            end_date=analysis_end_date,
            properties=properties,
            unsecured_loans=[]  # Add your unsecured loans here if any
        )
    
    # Aggregate hold period cash flows
    if st.button("Calculate"):
        cash_flows = update_portfolio_dates_and_calculate()
        st.title(st.session_state.portfolio.name)
        st.dataframe(cash_flows.T, column_config=adjusted_column_config, use_container_width=True)
        st.dataframe(cash_flows.T.sum().T)
        

        st.write("Market Value by Property Type")
        viz = Portfolioviz(st.session_state.portfolio)
        viz.plot_property_type_distribution()

        st.write("Unsecured Loan Balance")
        viz.plot_loan_balance_over_time()
