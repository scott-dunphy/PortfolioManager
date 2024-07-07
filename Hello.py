import streamlit as st
from datetime import date, datetime
from portfolio import Portfolio
import pandas as pd
from property import Property
from loan import Loan
from config import adjusted_column_config
from datetime import datetime, timedelta

st.set_page_config(
    page_title="CRE Portfolio Manager",
    page_icon="👋",
)

st.title("CRE Portfolio Manager 🏗️")
# Get the current date and time
now = datetime.now()
start_date = datetime(now.year, now.month, 1)
end_date = datetime(start_date.year + 3, start_date.month, 1)

analysis_start_date = pd.to_datetime(st.date_input('Analysis Start Date', value=start_date))
analysis_end_date = pd.to_datetime(st.date_input('Analysis End Date', value=end_date))



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

if 'portfolio' in st.session_state:
    st.session_state.portfolio.properties = properties 
    st.write(st.session_state.portfolio.unsecured_loans)
else:
    st.session_state.portfolio = Portfolio(
        name = 'Dunphy Property Fund',
        start_date = analysis_start_date,
        end_date = analysis_end_date,
        properties = properties
    )


cash_flows = st.session_state.portfolio.aggregate_hold_period_cash_flows()

# Display the DataFrame with custom formatting
st.dataframe(cash_flows, column_config=adjusted_column_config, use_container_width=True)

