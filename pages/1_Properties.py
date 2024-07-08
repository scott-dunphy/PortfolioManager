from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict
import pandas as pd
import streamlit as st
from config import adjusted_column_config

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import uuid
import pandas as pd
import json
from loan import Loan
from property import Property

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import streamlit as st

# Check if properties exist in session state
if 'properties' in st.session_state and st.session_state.properties:
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
        square_footage = st.number_input('Square Footage', min_value=0.0, value=float(selected_property.square_footage) if selected_property and selected_property.square_footage else 0.0, format='%f')
        year_built = st.number_input('Year Built', min_value=0, value=selected_property.year_built)
        current_value = st.number_input('Current Value', min_value=0.0, value=float(selected_property.current_value), format='%f')
        purchase_price = st.number_input('Purchase Price', min_value=0.0, value=float(selected_property.purchase_price), format='%f')
        purchase_date = st.date_input('Purchase Date', value=selected_property.purchase_date)

    with col2:
        analysis_start_date = st.date_input('Analysis Start Date', value=selected_property.analysis_start_date)
        analysis_end_date = st.date_input('Analysis End Date', value=selected_property.analysis_end_date)
        ownership_share = st.number_input('Ownership Share', min_value=0.0, max_value=1.0, value=float(selected_property.ownership_share), format='%f')
        default_sale_date = selected_property.analysis_start_date.replace(day=1) + relativedelta(years=10)
        sale_date = selected_property._standardize_date(st.date_input('Sale Date', value=selected_property.sale_date or default_sale_date))
        sale_price = st.number_input('Sale Price', min_value=0.0, value=float(selected_property.sale_price) if selected_property.sale_price else 0.0, format="%f")
        buyout_date = selected_property._standardize_date(st.date_input('Partner Buyout Date', value=selected_property.buyout_date or datetime(2100,12,1)))
        buyout_amount = st.number_input('Buyout Amount', min_value=0.0, value=float(selected_property.buyout_amount) if selected_property.buyout_amount else 0.0, format="%f")

    # Loan inputs
    with st.expander("Loan Details"):
        loan_exists = st.checkbox('Add/Edit Loan', value=selected_property.loan is not None)
        if loan_exists:
            origination_date = st.date_input('Origination Date', value=selected_property.loan.origination_date if selected_property.loan else date.today())
            maturity_date = st.date_input('Maturity Date', value=selected_property.loan.maturity_date if selected_property.loan else date.today())
            original_balance = st.number_input('Original Balance', min_value=0.0, value=float(selected_property.loan.original_balance) if selected_property.loan else 0.0, format='%f')
            note_rate = st.number_input('Note Rate (%)', min_value=0.0, value=float(selected_property.loan.note_rate * 100) if selected_property.loan else 0.0, format='%f')
            interest_only_period = st.number_input('Interest Only Period (months)', min_value=0, value=int(selected_property.loan.interest_only_period) if selected_property.loan else 0)
            amortization_period = st.number_input('Amortization Period (months)', min_value=0, value=int(selected_property.loan.amortization_period) if selected_property.loan else 0)
            day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(selected_property.loan.day_count_method) if selected_property.loan else 0)

    # Financial Data inputs
    with st.expander("Financial Data"):
        noi_data = st.text_area("Net Operating Income (space-separated values)", value=' '.join([str(v) for v in selected_property.noi.values()]))
        capex_data = st.text_area("Capital Expenditures (space-separated values)", value=' '.join([str(v) for v in selected_property.capex.values()]))

else:
    st.write("No properties found. Please add a new property.")

    # Inputs for a new property
    col1, col2 = st.columns(2)

    with col1:
        property_id = st.text_input('Property ID')
        property_name = st.text_input('Property Name')
        property_address = st.text_input('Property Address')
        property_type = st.text_input('Property Type')
        square_footage = st.number_input('Square Footage', min_value=0.0, format='%f')
        year_built = st.number_input('Year Built', min_value=0)
        current_value = st.number_input('Current Value', min_value=0.0, format='%f')
        purchase_price = st.number_input('Purchase Price', min_value=0.0, format='%f')
        purchase_date = st.date_input('Purchase Date')

    with col2:
        analysis_start_date = st.date_input('Analysis Start Date')
        analysis_end_date = st.date_input('Analysis End Date')
        ownership_share = st.number_input('Ownership Share', min_value=0.0, max_value=1.0, format='%f')
        sale_date = st.date_input('Sale Date')
        sale_price = st.number_input('Sale Price', min_value=0.0, format="%f")
        buyout_date = st.date_input('Partner Buyout Date')
        buyout_amount = st.number_input('Buyout Amount', min_value=0.0, format="%f")

    # Button to add new property
    if st.button('Add Property'):
        new_property = Property(
            property_id=property_id,
            name=property_name,
            address=property_address,
            property_type=property_type,
            square_footage=square_footage,
            year_built=year_built,
            current_value=current_value,
            purchase_price=purchase_price,
            purchase_date=purchase_date,
            analysis_start_date=analysis_start_date,
            analysis_end_date=analysis_end_date,
            ownership_share=ownership_share,
            sale_date=sale_date,
            sale_price=sale_price,
            buyout_date=buyout_date,
            buyout_amount=buyout_amount,
            loan=None,  # Initialize with no loan
            noi={},  # Initialize empty
            capex={}  # Initialize empty
        )

        if 'properties' not in st.session_state:
            st.session_state.properties = []

        st.session_state.properties.append(new_property)
        st.success("Property added successfully.")
        selected_property = new_property
    
    # Display cash flows
    st.subheader("Hold Period Cash Flows")
    hold_period_cf = selected_property.hold_period_cash_flows_x()
    cf = selected_property.get_cash_flows_dataframe()
    st.dataframe(hold_period_cf, column_config=adjusted_column_config, use_container_width=True)

    st.dataframe(selected_property.loan.schedule)

    st.write(selected_property.loan.amortization_period)
    st.write(selected_property.loan.monthly_payment)



if st.button('Update and Recalculate'):
    update_property()
    # Save updated properties to session state
    st.session_state.properties = properties


from io import BytesIO

def update_property(properties, selected_property, updated_data):
    for prop in properties:
        if prop.property_id == selected_property.property_id:
            prop.name = updated_data['name']
            prop.address = updated_data['address']
            prop.property_type = updated_data['property_type']
            prop.square_footage = updated_data['square_footage']
            prop.year_built = updated_data['year_built']
            prop.current_value = updated_data['current_value']
            prop.purchase_price = updated_data['purchase_price']
            prop.purchase_date = updated_data['purchase_date']
            prop.analysis_start_date = updated_data['analysis_start_date']
            prop.analysis_end_date = updated_data['analysis_end_date']
            prop.ownership_share = updated_data['ownership_share']
            prop.sale_date = updated_data['sale_date']
            prop.sale_price = updated_data['sale_price']
            prop.buyout_date = updated_data['buyout_date']
            prop.buyout_amount = updated_data['buyout_amount']
            break
    st.session_state.properties = properties
    st.success("Property updated successfully.")
    

def save_session_state():
    properties_dict = [prop.to_dict() for prop in st.session_state.properties]
    json_str = json.dumps(properties_dict)

    # Use BytesIO to create a binary file-like object
    file_like = BytesIO(json_str.encode('utf-8'))

    # Create a download button in Streamlit
    st.download_button(
        label="Download Session State",
        data=file_like,
        file_name="session_state.json",
        mime="application/json"
    )

        
if st.button("Save Session State"):
    save_session_state()
    st.success("Session state saved to file.")
