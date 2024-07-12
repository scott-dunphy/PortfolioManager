from datetime import datetime
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd
import uuid
from loan import Loan

# Debug: Log start of script
st.write("Starting unsecured loan script...")

# Check if 'portfolio' is in session state
if 'portfolio' not in st.session_state:
    st.error("Portfolio not found in session state.")
    st.stop()

# Debug: Log portfolio existence
st.write("Portfolio found in session state.")

# Assuming you have a list of unsecured loans stored in st.session_state.portfolio.unsecured_loans
unsecured_loans = st.session_state.portfolio.unsecured_loans
loan_names = [loan.loan_id for loan in unsecured_loans]
selected_loan_name = st.selectbox("Select Unsecured Loan", loan_names)

# Debug: Log selected loan name
st.write(f"Selected loan name: {selected_loan_name}")

# Find the selected loan
selected_loan = next((loan for loan in unsecured_loans if loan.loan_id == selected_loan_name), None)

# Debug: Log selected loan details
if selected_loan:
    st.write(f"Selected loan: {selected_loan.loan_id}")
else:
    st.write("No loan selected.")

# Unsecured Loan inputs
loan_id = st.text_input('Loan ID', value=selected_loan.loan_id if selected_loan else str(uuid.uuid4()))

col1, col2 = st.columns(2)

with col1:
    origination_date = st.date_input('Origination Date', value=selected_loan.origination_date if selected_loan else datetime.today())
    maturity_date = st.date_input('Maturity Date', value=selected_loan.maturity_date if selected_loan else datetime.today() + relativedelta(years=10))
    original_balance = st.number_input('Original Balance', value=selected_loan.original_balance if selected_loan else 1.0, min_value=0.01, format='%f')
    fixed_floating = st.selectbox('Fixed/Floating', options=["Fixed", "Floating"], index=["Fixed", "Floating"].index(selected_loan.fixed_floating) if selected_loan else 0)

with col2:
    if fixed_floating == "Fixed":
        note_rate = st.number_input('Note Rate (%)', value=selected_loan.note_rate if selected_loan else 0.0, min_value=0.0, format='%f')
        interest_only_period = st.number_input('Interest Only Period (months)', value=selected_loan.interest_only_period if selected_loan else 0, min_value=0)
        amortization_period = st.number_input('Amortization Period (months)', value=selected_loan.amortization_period if selected_loan else 0, min_value=0)
        spread = 0
    else:
        note_rate = 0
        spread = st.number_input('Floating Rate Spread (%)', value=selected_loan.spread if selected_loan else 0.0, min_value=0.0, format='%f')
        interest_only_period = 0
        amortization_period = 0

    day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(selected_loan.day_count_method) if selected_loan else 0)

# Debug: Log input values
st.write(f"Loan ID: {loan_id}")
st.write(f"Origination Date: {origination_date}")
st.write(f"Maturity Date: {maturity_date}")
st.write(f"Original Balance: {original_balance}")
st.write(f"Fixed/Floating: {fixed_floating}")
st.write(f"Note Rate: {note_rate}")
st.write(f"Spread: {spread}")
st.write(f"Interest Only Period: {interest_only_period}")
st.write(f"Amortization Period: {amortization_period}")
st.write(f"Day Count Method: {day_count_method}")

# Create or update the loan object
loan = Loan(
    origination_date=origination_date,
    maturity_date=maturity_date,
    original_balance=original_balance,
    note_rate=note_rate,
    interest_only_period=interest_only_period,
    amortization_period=amortization_period,
    day_count_method=day_count_method,
    loan_id=loan_id,  # Use the input loan_id
    fixed_floating=fixed_floating,
    spread=spread
)

# Debug: Log loan creation
st.write(f"Loan created: {loan}")

# Display the unsecured loan schedule
st.write("Unsecured Loan Schedule:")
try:
    schedule_df = pd.DataFrame(loan.get_unsecured_schedule())
    st.dataframe(schedule_df)
except Exception as e:
    st.error(f"Error generating schedule: {e}")
    st.stop()

# Add buttons for adding new and updating existing loan
if st.button("Add New Unsecured Loan"):
    try:
        st.session_state.portfolio.add_unsecured_loan(loan)
        st.success("New Unsecured Loan added successfully.")
    except Exception as e:
        st.error(f"Error adding new unsecured loan: {e}")

if st.button("Update Unsecured Loan"):
    try:
        if selected_loan:
            st.session_state.portfolio.remove_unsecured_loan(selected_loan.loan_id)
        st.session_state.portfolio.add_unsecured_loan(loan)
        st.success("Unsecured Loan updated successfully.")
    except Exception as e:
        st.error(f"Error updating unsecured loan: {e}")
