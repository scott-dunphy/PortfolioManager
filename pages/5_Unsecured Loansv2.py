from datetime import datetime
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd
import uuid
from loan import Loan

# Assuming you have a list of unsecured loans stored in st.session_state.unsecured_loans
unsecured_loans = st.session_state.portfolio.unsecured_loans if 'portfolio' in st.session_state else []

loan_names = [loan.loan_id for loan in unsecured_loans]
selected_loan_name = st.selectbox("Select Unsecured Loan", loan_names)

selected_loan = next((loan for loan in unsecured_loans if loan.loan_id == selected_loan_name), None)

# Unsecured Loan inputs
loan_id = st.text_input('Loan ID', value=selected_loan.loan_id if selected_loan else str(uuid.uuid4()))

col1, col2 = st.columns(2)

with col1:
    origination_date = st.date_input('Origination Date', value=selected_loan.origination_date if selected_loan else datetime.today())
    maturity_date = st.date_input('Maturity Date', value=selected_loan.maturity_date if selected_loan else datetime.today() + relativedelta(years=10))
    original_balance = st.number_input('Original Balance', value=selected_loan.original_balance if selected_loan else 0.0, format='%f')
    fixed_floating = st.selectbox('Fixed/Floating', options=["Fixed", "Floating"], index=["Fixed", "Floating"].index(selected_loan.fixed_floating) if selected_loan else 0)
    

with col2:
    if fixed_floating == "Fixed":
        note_rate = st.number_input('Note Rate (%)', value=selected_loan.note_rate if selected_loan else 0.0, min_value=0.0, format='%f')
    if fixed_floating == "Floating":
        spread = st.number_input('Floating Rate Spread (%)', value=selected_loan.spread if selected_loan else 0.0, min_value=0.0, format='%f')
    interest_only_period = st.number_input('Interest Only Period (months)', value=selected_loan.interest_only_period if selected_loan else 0, min_value=0)
    amortization_period = st.number_input('Amortization Period (months)', value=selected_loan.amortization_period if selected_loan else 0, min_value=0)
    day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(selected_loan.day_count_method) if selected_loan else 0)

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
    spread=spread if spread else 0
)

# Display the unsecured loan schedule
st.write("Unsecured Loan Schedule:")
st.dataframe(pd.DataFrame(loan.get_unsecured_schedule()))

# Add buttons for adding new and updating existing loan
if st.button("Add New Unsecured Loan"):
    if 'portfolio' in st.session_state:
        st.session_state.portfolio.add_unsecured_loan(loan)
        st.success("New Unsecured Loan added successfully.")
    else:
        st.error("Portfolio not found in session state.")

if st.button("Update Unsecured Loan"):
    if 'portfolio' in st.session_state:
        if selected_loan:
            st.session_state.portfolio.remove_unsecured_loan(selected_loan.loan_id)
        st.session_state.portfolio.add_unsecured_loan(loan)
        st.success("Unsecured Loan updated successfully.")
    else:
        st.error("Portfolio not found in session state.")
