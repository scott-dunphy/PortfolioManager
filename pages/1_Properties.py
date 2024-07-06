from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict
import pandas as pd
import streamlit as st

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import uuid
import pandas as pd
import json
from loan import Loan
from property import Property

properties = st.session_state.properties

property_names = [prop.name for prop in properties]
selected_property_name = st.selectbox("Select Property", property_names)

selected_property = next(prop for prop in properties if prop.name == selected_property_name)

# Property inputs
col1, col2 = st.columns(2)

with col1:
    property_name = st.text_input('Property Name', value=selected_property.name)
    property_address = st.text_input('Property Address', value=selected_property.address)
    property_type = st.text_input('Property Type', value=selected_property.property_type)
    square_footage = st.number_input('Square Footage', min_value=0.0, value=selected_property.square_footage, format='%f')
    year_built = st.number_input('Year Built', min_value=0, value=selected_property.year_built)
    current_value = st.number_input('Current Value', min_value=0.0, value=selected_property.current_value, format='%f')
    

with col2:
    purchase_price = st.number_input('Purchase Price', min_value=0.0, value=selected_property.purchase_price, format='%f')
    purchase_date = st.date_input('Purchase Date', value=selected_property.purchase_date)
    analysis_start_date = st.date_input('Analysis Start Date', value=selected_property.analysis_start_date)
    analysis_end_date = st.date_input('Analysis End Date', value=selected_property.analysis_end_date)
    ownership_share = st.number_input('Ownership Share', min_value=0.0, max_value=1.0, value=selected_property.ownership_share, format='%f')
    default_sale_date = selected_property.analysis_start_date.replace(day=1) + relativedelta(years=10)
    
    # Sale Date input: if sale_date is None, default to ten years from the analysis date
    sale_date = selected_property._standardize_date(st.date_input('Sale Date', value=selected_property.sale_date or default_sale_date))

    sale_price = st.number_input('Sale Price', min_value=0.0, value=float(selected_property.sale_price) if selected_property.sale_price else 0.0, format="%f")

# Loan inputs
with st.expander("Loan Details"):
    loan_exists = st.checkbox('Add/Edit Loan', value=selected_property.loan is not None)
    if loan_exists:
        origination_date = st.date_input('Origination Date', value=selected_property.loan.origination_date if selected_property.loan else date.today())
        maturity_date = st.date_input('Maturity Date', value=selected_property.loan.maturity_date if selected_property.loan else date.today())
        original_balance = st.number_input('Original Balance', min_value=0.0, value=selected_property.loan.original_balance if selected_property.loan else 0.0, format='%f')
        note_rate = st.number_input('Note Rate (%)', min_value=0.0, value=selected_property.loan.note_rate * 100 if selected_property.loan else 0.0, format='%f')
        interest_only_period = st.number_input('Interest Only Period (months)', min_value=0, value=selected_property.loan.interest_only_period if selected_property.loan else 0)
        amortization_period = st.number_input('Amortization Period (months)', min_value=0, value=selected_property.loan.amortization_period if selected_property.loan else 0)
        day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(selected_property.loan.day_count_method) if selected_property.loan else 0)

# Financial Data inputs
with st.expander("Financial Data"):
    noi_data = st.text_area("Net Operating Income (space-separated values)", value=' '.join([str(v) for v in selected_property.noi.values()]))
    capex_data = st.text_area("Capital Expenditures (space-separated values)", value=' '.join([str(v) for v in selected_property.capex.values()]))

def update_property():
    selected_property.name = property_name
    selected_property.address = property_address
    selected_property.property_type = property_type
    selected_property.square_footage = square_footage
    selected_property.year_built = year_built
    selected_property.purchase_price = purchase_price
    selected_property.purchase_date = purchase_date
    selected_property.analysis_start_date = analysis_start_date
    selected_property.analysis_end_date = analysis_end_date
    selected_property.current_value = current_value
    selected_property.sale_date = sale_date
    selected_property.sale_price = sale_price
    selected_property.sale_price = ownership_share

    # Call update_ownership_share if ownership_share is changed
    selected_property.update_ownership_share(start_date=analysis_start_date, new_share=ownership_share)

    #selected_property.ownership_share = ownership_share

    # Update loan details based on inputs
    if loan_exists:
        if selected_property.loan:
            selected_property.loan.origination_date = origination_date
            selected_property.loan.maturity_date = maturity_date
            selected_property.loan.original_balance = original_balance
            selected_property.loan.note_rate = note_rate / 100
            selected_property.loan.interest_only_period = interest_only_period
            selected_property.loan.amortization_period = amortization_period
            selected_property.loan.day_count_method = day_count_method
        else:
            selected_property.add_loan(Loan(
                origination_date=origination_date,
                maturity_date=maturity_date,
                original_balance=original_balance,
                note_rate=note_rate,
                interest_only_period=interest_only_period,
                amortization_period=amortization_period,
                day_count_method=day_count_method
            ))
    else:
        if selected_property.loan:
            selected_property.remove_loan()

    # Parse financial data and update the property
    if noi_data:
        try:
            selected_property.streamlit_add_noi(noi_data)
        except ValueError as e:
            st.error(f"Error parsing NOI data: {e}")

    if capex_data:
        try:
            selected_property.streamlit_add_capex(capex_data)
        except ValueError as e:
            st.error(f"Error parsing CapEx data: {e}")

    st.session_state.properties = properties  # Save updated properties to session state
    
    # Display cash flows
    st.subheader("Hold Period Cash Flows")
    hold_period_cf = selected_property.hold_period_cash_flows_x()
    cf = selected_property.get_cash_flows_dataframe()
    st.table(hold_period_cf)



if st.button('Update and Recalculate'):
    update_property()
    # Save updated properties to session state
    st.session_state.properties = properties


# Function to save session state to a file
def save_session_state(filename="session_state.json"):
    properties_dict = [prop.to_dict() for prop in st.session_state.properties]
    with open(filename, 'w') as f:
        json.dump(properties_dict, f)
        
if st.button("Save Session State"):
    save_session_state()
    st.success("Session state saved to file.")
