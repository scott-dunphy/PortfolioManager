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
        st.session_state.cash_flows = cash_flows.T  # Store transposed cash_flows in session state

# Check if 'cash_flows' is in session state and set it if not
if 'cash_flows' in st.session_state:
    cash_flows = st.session_state.cash_flows
    cash_flows = st.data_editor(cash_flows, column_config=adjusted_column_config, use_container_width=True)
    st.session_state.cash_flows = cash_flows  # Update session state with any changes made in the editor

    # Sum the transposed DataFrame
    transposed_df = cash_flows.sum().to_frame().T
    transposed_df.index = ['Total Adjusted Cash Flows']

    # Display in Streamlit without the index
    st.dataframe(transposed_df)

    with st.form("capital_call_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_input = st.date_input("Date")
        with col2:
            capital_call = st.number_input("Capital Call", min_value=0.0, step=0.01)
        with col3:
            redemption = st.number_input("Redemption Payment", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Submit")
        
    # Handle form submission
    if submit:
        # Create a new DataFrame for the new flow
        new_flow = pd.DataFrame([{
            'Date': date_input,
            'Capital Call': capital_call,
            'Redemption Payment': redemption
        }]).set_index('Date')

        # Add the new flow to the portfolio
        st.session_state.portfolio.add_capital_flows(new_flow)
        st.success("Data submitted successfully!")
        st.experimental_rerun()

    if not st.session_state.portfolio.capital_flows.empty:
        st.write("Capital Flows:")
        st.write(st.session_state.portfolio.capital_flows)
        
    st.write("Market Value by Property Type")
    viz = Portfolioviz(st.session_state.portfolio)
    viz.plot_property_type_distribution()

    st.write("Unsecured Loan Balance")
    viz.plot_loan_balance_over_time()
