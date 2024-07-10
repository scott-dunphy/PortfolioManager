import streamlit as st
from datetime import date, timedelta
import pandas as pd
from portfolio import Portfolio
from property import Property
from loan import Loan
from config import adjusted_column_config

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
st.write(analysis_start_date)
analysis_end_date = st.date_input('Analysis End Date', value=end_date)

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
    cash_flows = st.session_state.portfolio.aggregate_hold_period_cash_flows()
    # Display the DataFrame with custom formatting
    st.dataframe(cash_flows, column_config=adjusted_column_config, use_container_width=True)
else:
    st.write("Looks like you haven't uploaded any properties yet.\n Go to the Upload page to upload a portfolio or the Properties page to add individual properties.")
