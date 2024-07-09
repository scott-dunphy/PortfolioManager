import streamlit as st
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import uuid
from config import adjusted_column_config
from loan import Loan
from property import Property

# Initialize session state for properties if it doesn't exist
if 'properties' not in st.session_state:
    st.session_state.properties = []

properties = st.session_state.properties

if properties:
    # Existing code for when properties exist
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

    if st.button('Update and Recalculate'):
        update_property()
        st.session_state.properties = properties
        st.success("Property updated successfully.")

else:
    # New code for when no properties exist
    st.write("No properties exist. Add a new property:")

    col1, col2 = st.columns(2)

    with col1:
        property_id = str(uuid.uuid4())  # Generate a new UUID for the property
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

    # Loan inputs
    with st.expander("Loan Details"):
        loan_exists = st.checkbox('Add Loan')
        if loan_exists:
            origination_date = st.date_input('Origination Date')
            maturity_date = st.date_input('Maturity Date')
            original_balance = st.number_input('Original Balance', min_value=0.0, format='%f')
            note_rate = st.number_input('Note Rate (%)', min_value=0.0, format='%f')
            interest_only_period = st.number_input('Interest Only Period (months)', min_value=0)
            amortization_period = st.number_input('Amortization Period (months)', min_value=0)
            day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"])

    # Financial Data inputs
    with st.expander("Financial Data"):
        noi_data = st.text_area("Net Operating Income (space-separated values)")
        capex_data = st.text_area("Capital Expenditures (space-separated values)")

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
            buyout_amount=buyout_amount
        )

        if loan_exists:
            new_loan = Loan(
                origination_date=origination_date,
                maturity_date=maturity_date,
                original_balance=original_balance,
                note_rate=note_rate / 100,
                interest_only_period=interest_only_period,
                amortization_period=amortization_period,
                day_count_method=day_count_method
            )
            new_property.add_loan(new_loan)

        if noi_data:
            new_property.streamlit_add_noi(noi_data)
        if capex_data:
            new_property.streamlit_add_capex(capex_data)

        st.session_state.properties.append(new_property)
        st.success("New property added successfully.")

# Save session state button
if st.button("Save Session State"):
    save_session_state()
    st.success("Session state saved to file.")
