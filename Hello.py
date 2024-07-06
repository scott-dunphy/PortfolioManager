import streamlit as st
from datetime import date, datetime
from portfolio import Portfolio
import pandas as pd
from property import Property
from loan import Loan

st.set_page_config(
    page_title="CRE Portfolio Manager",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")



# Initialize session state for properties
if 'properties' not in st.session_state:
    st.write("Looks like you don't have any properties loaded! \n Load your own or use the example portfolio.")
    if st.button("Load Example Properties"):
        st.session_state.properties = [
            Property(
                property_id="CRE001",
                name="Downtown Office Building",
                address="123 Main St, Anytown, USA",
                property_type="Office",
                square_footage=50000.0,
                year_built=1995,
                purchase_price=25000000.00,
                purchase_date=date(2023, 1, 1),
                analysis_start_date=date(2023, 1, 1),
                analysis_end_date=date(2025, 12, 1),
                current_value=25000000.00,
                ownership_share=0.8
            ),
            Property(
                property_id="CRE002",
                name="Suburban Retail Center",
                address="456 Elm St, Anytown, USA",
                property_type="Retail",
                square_footage=75000.0,
                year_built=2005,
                purchase_price=35000000.00,
                purchase_date=date(2023, 1, 1),
                analysis_start_date=date(2023, 1, 1),
                analysis_end_date=date(2025, 12, 1),
                current_value=35000000.00,
                ownership_share=1.0
            )
        ]
    
    

if st.session_state.properties:
    properties = st.session_state.properties
    
    portfolio = Portfolio(
        name = 'Dunphy Property Fund',
        start_date = datetime(2023,1,1),
        end_date = datetime(2025,1,1),
        properties = properties
    )
    
    cash_flows = portfolio.aggregate_hold_period_cash_flows()
    
    st.table(cash_flows)


