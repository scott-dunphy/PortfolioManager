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

st.title("CRE Portfolio Manager 🏗️")



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
    
    

if 'properties' in st.session_state:
    properties = st.session_state.properties
    
    portfolio = Portfolio(
        name = 'Dunphy Property Fund',
        start_date = datetime(2023,1,1),
        end_date = datetime(2025,1,1),
        properties = properties
    )
    
    cash_flows = portfolio.aggregate_hold_period_cash_flows()

    
    column_config = {
        'Adjusted Purchase Price': st.column_config.NumberColumn("Adjusted Purchase Price", format='$ %i'),
        'Adjusted Loan Proceeds': st.column_config.NumberColumn("Adjusted Loan Proceeds", format='$%d'),
        'Adjusted Net Operating Income': st.column_config.NumberColumn("Adjusted Net Operating Income", format='$%d'),
        'Adjusted Capital Expenditures': st.column_config.NumberColumn("Adjusted Capital Expenditures", format='$%d'),
        'Adjusted Interest Expense': st.column_config.NumberColumn("Adjusted Interest Expense", format='$%d'),
        'Adjusted Principal Payments': st.column_config.NumberColumn("Adjusted Principal Payments", format='$%d'),
        'Adjusted Debt Scheduled Repayment': st.column_config.NumberColumn("Adjusted Debt Scheduled Repayment", format='$%d'),
        'Adjusted Debt Early Prepayment': st.column_config.NumberColumn("Adjusted Debt Early Prepayment", format='$%d'),
        'Adjusted Sale Proceeds': st.column_config.NumberColumn("Adjusted Sale Proceeds", format='$%d'),
        'Adjusted Partner Buyout': st.column_config.NumberColumn("Adjusted Partner Buyout", format='$%d'),
        'Total Cash Flow': st.column_config.NumberColumn("Total Cash Flow", format='$%d')
    }
    
    # Display the DataFrame with custom formatting
    st.dataframe(cash_flows, column_config=column_config, use_container_width=True)

