import streamlit as st
import pandas as pd
from loan import Loan
from property import Property
from upload import load_cashflows, load_properties_and_loans
from portfolio import Portfolio
from datetime import date, datetime

st.title('Property and Loan Importer')

# Get the current date
now = date.today()
start_date = date(now.year, now.month, 1)
end_date = date(start_date.year + 3, start_date.month, 1)

properties_and_loans_file = st.file_uploader('Upload Properties and Loans Excel File', type=['xlsx'])

if st.button("Upload Portfolio"):
    if properties_and_loans_file:
        properties, loans = load_properties_and_loans(properties_and_loans_file)
        noi, capex = load_cashflows(properties_and_loans_file)
        st.write(noi)
        
        for property_obj in properties:
            property_id = property_obj.property_id
            property_obj.noi = noi.get(property_id, {})
            property_obj.capex = capex.get(property_id, {})
            
        
        st.session_state.properties = properties
        portfolio = Portfolio(name='Dunphy', properties=properties, start_date=start_date, end_date=end_date)
        st.session_state.portfolio = portfolio
