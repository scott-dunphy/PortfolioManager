import streamlit as st
import pandas as pd
from loan import Loan
from property import Property
from upload import load_cashflows, load_properties_and_loans

st.title('Property and Loan Importer')
    
properties_and_loans_file = st.file_uploader('Upload Properties and Loans Excel File', type=['xlsx'])
cashflows_file = st.file_uploader('Upload Cashflows Excel File', type=['xlsx'])

if properties_and_loans_file and cashflows_file:
    properties = load_properties_and_loans(properties_and_loans_file)
    noi, capex = load_cashflows(cashflows_file)
    
    for property_obj in properties:
        property_obj.noi = noi.get(property_obj.property_id, {})

st.session_state.properties = properties
