import streamlit as st
import pandas as pd
from loan import Loan
from property import Property
from upload import load_cashflows, load_properties_and_loans
from portfolio import Portfolio
from datetime import date, datetime

st.title('Property and Loan Importer')
    
properties_and_loans_file = st.file_uploader('Upload Properties and Loans Excel File', type=['xlsx'])
#cashflows_file = st.file_uploader('Upload Cashflows Excel File', type=['xlsx'])

if st.button("Upload Portfolio"):
    if properties_and_loans_file:
        properties, loans = load_properties_and_loans(properties_and_loans_file)
        noi, capex = load_cashflows(properties_and_loans_file)
        
        for property_obj in properties:
            property_obj.noi = noi.get(property_obj.property_id, {})
    
    st.session_state.properties = properties
    portfolio = Portfolio(name='XYZ', properties=properties, analysis_start_date=datetime(2023,1,1), analysis_end_date=datetime(2030,12,1))
    st.session_state.portfolio = portfolio
