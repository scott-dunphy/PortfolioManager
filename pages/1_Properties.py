import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import uuid
from config import adjusted_column_config
from loan import Loan
from property import Property
import pandas as pd

def _standardize_date(d: date) -> date:
    """Standardize a date to the first of its month."""
    return date(d.year, d.month, 1)

def update_property(properties, selected_property, updated_data, fin_df, loan_data_list):
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
            prop.buyout_date = _standardize_date(updated_data['buyout_date'])
            prop.buyout_amount = updated_data['buyout_amount']
            
            # Update NOI and CapEx
            prop.add_noi_capex(fin_df)
            
            # Update loans
            prop.loans = []
            for loan_data in loan_data_list:
                if loan_data['loan_exists']:
                    loan = Loan(
                        origination_date=loan_data['origination_date'],
                        maturity_date=loan_data['maturity_date'],
                        original_balance=loan_data['original_balance'],
                        note_rate=loan_data['note_rate'] / 100,
                        interest_only_period=loan_data['interest_only_period'],
                        amortization_period=loan_data['amortization_period'],
                        day_count_method=loan_data['day_count_method']
                    )
                    prop.loans.append(loan)

            break

    st.session_state.properties = properties

if 'add_new_loan_checked' not in st.session_state:
    st.session_state.add_new_loan_checked = False
    
if 'properties' in st.session_state and st.session_state.properties:
    properties = st.session_state.properties

    # Button to add a new property
    add_property_mode = st.checkbox('Add New Property')

    if not add_property_mode:
        # Existing code for when properties exist
        property_names = [prop.name for prop in properties]
        selected_property_name = st.selectbox("Select Property", property_names)
        selected_property = next(prop for prop in properties if prop.name == selected_property_name)

        # Property inputs
        col1, col2 = st.columns(2)

        with col1:
            property_id = st.text_input('Property ID', value=selected_property.property_id)
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
            sale_date = st.date_input('Sale Date', value=selected_property.sale_date or default_sale_date)
            sale_price = st.number_input('Sale Price', min_value=0.0, value=float(selected_property.sale_price) if selected_property.sale_price else 0.0, format="%f")
            buyout_date = st.date_input('Partner Buyout Date', value=selected_property.buyout_date or date(2100,12,1))
            buyout_amount = st.number_input('Buyout Amount', min_value=0.0, value=float(selected_property.buyout_amount) if selected_property.buyout_amount else 0.0, format="%f")

        # Loan inputs for multiple loans
        loan_data_list = []
        for i, loan in enumerate(selected_property.loans):
            with st.expander(f"Loan Details {i + 1}"):
                loan_exists = st.checkbox(f'Add/Edit Loan {i + 1}', value=loan is not None)
                origination_date = st.date_input(f'Origination Date {i + 1}', value=loan.origination_date if loan else date.today())
                maturity_date = st.date_input(f'Maturity Date {i + 1}', value=loan.maturity_date if loan else date.today())
                original_balance = st.number_input(f'Original Balance {i + 1}', min_value=0.0, value=float(loan.original_balance) if loan else 0.0, format='%f')
                note_rate = st.number_input(f'Note Rate (%) {i + 1}', min_value=0.0, value=float(loan.note_rate * 100) if loan else 0.0, format='%f')
                interest_only_period = st.number_input(f'Interest Only Period (months) {i + 1}', min_value=0, value=int(loan.interest_only_period) if loan else 0)
                amortization_period = st.number_input(f'Amortization Period (months) {i + 1}', min_value=0, value=int(loan.amortization_period) if loan else 0)
                day_count_method = st.selectbox(f'Day Count Method {i + 1}', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(loan.day_count_method) if loan else 0)
                
                loan_data = {
                    'loan_exists': loan_exists,
                    'origination_date': origination_date,
                    'maturity_date': maturity_date,
                    'original_balance': original_balance,
                    'note_rate': note_rate,
                    'interest_only_period': interest_only_period,
                    'amortization_period': amortization_period,
                    'day_count_method': day_count_method
                }
                loan_data_list.append(loan_data)
        
        # Adding a new loan if needed
        with st.expander("Add New Loan"):
            st.session_state.add_new_loan_checked = st.checkbox('Add New Loan', value=st.session_state.add_new_loan_checked)
            if st.session_state.add_new_loan_checked:
                origination_date = st.date_input('New Loan Origination Date')
                maturity_date = st.date_input('New Loan Maturity Date')
                original_balance = st.number_input('New Loan Original Balance', min_value=0.0, format='%f')
                note_rate = st.number_input('New Loan Note Rate (%)', min_value=0.0, format='%f')
                interest_only_period = st.number_input('New Loan Interest Only Period (months)', min_value=0)
                amortization_period = st.number_input('New Loan Amortization Period (months)', min_value=0)
                day_count_method = st.selectbox('New Loan Day Count Method', options=["Actual/360", "Actual/365", "30/360"])
        
                loan_data = {
                    'loan_exists': True,
                    'origination_date': origination_date,
                    'maturity_date': maturity_date,
                    'original_balance': original_balance,
                    'note_rate': note_rate,
                    'interest_only_period': interest_only_period,
                    'amortization_period': amortization_period,
                    'day_count_method': day_count_method
                }
                loan_data_list.append(loan_data)
            else:
                st.session_state.add_new_loan_checked = False
                
        #st.write(selected_property.noi_capex)
        # Financial Data inputs
        with st.expander("Financial Data"):
            fin_df = st.data_editor(selected_property.noi_capex)

        if st.button('Update and Recalculate'):
            updated_data = {
                'property_id': property_id,
                'name': property_name,
                'address': property_address,
                'property_type': property_type,
                'square_footage': square_footage,
                'year_built': year_built,
                'current_value': current_value,
                'purchase_price': purchase_price,
                'purchase_date': purchase_date,
                'analysis_start_date': analysis_start_date,
                'analysis_end_date': analysis_end_date,
                'ownership_share': ownership_share,
                'sale_date': sale_date,
                'sale_price': sale_price,
                'buyout_date': _standardize_date(buyout_date),
                'buyout_amount': buyout_amount
            }
            
            update_property(properties, selected_property, updated_data, fin_df, loan_data_list)
            st.success("Property updated successfully.")
            # Display cash flows
            st.subheader("Hold Period Cash Flows")
            hold_period_cf = selected_property.hold_period_cash_flows()
            st.dataframe(hold_period_cf, column_config=adjusted_column_config, use_container_width=True)
            
            # Display loan schedules
            for i, loan in enumerate(selected_property.loans):
                st.subheader(f"Loan Schedule {i + 1}")
                loan_schedule = loan.get_schedule()
                st.dataframe(loan_schedule)
                #st.write("Amortization Period:", loan.amortization_period)
                #st.write("Monthly Payment:", loan.monthly_payment)

    else:
        # New property inputs
        st.subheader("Add New Property")
        col1, col2 = st.columns(2)

        with col1:
            property_id = st.text_input('Property ID', value=str(uuid.uuid4()))
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

        # Loan inputs for new property
        loan_data_list = []
        with st.expander("Add Loan"):
            loan_exists = st.checkbox('Add Loan')
            if loan_exists:
                origination_date = st.date_input('Origination Date')
                maturity_date = st.date_input('Maturity Date')
                original_balance = st.number_input('Original Balance', min_value=0.0, format='%f')
                note_rate = st.number_input('Note Rate (%)', min_value=0.0, format='%f')
                interest_only_period = st.number_input('Interest Only Period (months)', min_value=0)
                amortization_period = st.number_input('Amortization Period (months)', min_value=0)
                day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"])

                loan_data = {
                    'loan_exists': loan_exists,
                    'origination_date': origination_date,
                    'maturity_date': maturity_date,
                    'original_balance': original_balance,
                    'note_rate': note_rate,
                    'interest_only_period': interest_only_period,
                    'amortization_period': amortization_period,
                    'day_count_method': day_count_method
                }
                loan_data_list.append(loan_data)

        # Financial Data inputs for new property
        with st.expander("Financial Data"):
            columns = ['Date', 'Net Operating Income', 'Capital Expenditures']
            # Create a blank DataFrame
            fin_df = pd.DataFrame(columns=columns)
            fin_df = st.data_editor(fin_df)

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
                buyout_date=_standardize_date(buyout_date),
                buyout_amount=buyout_amount,
                loans=[],  # Initialize with an empty list of loans
            )

            for loan_data in loan_data_list:
                if loan_data['loan_exists']:
                    new_loan = Loan(
                        origination_date=loan_data['origination_date'],
                        maturity_date=loan_data['maturity_date'],
                        original_balance=loan_data['original_balance'],
                        note_rate=loan_data['note_rate'] / 100,
                        interest_only_period=loan_data['interest_only_period'],
                        amortization_period=loan_data['amortization_period'],
                        day_count_method=loan_data['day_count_method']
                    )
                    new_property.add_loan(new_loan)
            
            new_property.add_noi_capex(fin_df)

            st.session_state.properties.append(new_property)
            st.success("New property added successfully.")
            st.experimental_rerun()  # Rerun to reflect the new property in the session state

else:
    # New code for when no properties exist
    st.write("No properties exist. Add a new property:")
    st.session_state.properties = []
    col1, col2 = st.columns(2)

    with col1:
        property_id = st.text_input('Property ID', value=str(uuid.uuid4()))
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

    # Loan inputs for new property
    loan_data_list = []
    with st.expander("Add Loan"):
        loan_exists = st.checkbox('Add Loan')
        if loan_exists:
            origination_date = st.date_input('Origination Date')
            maturity_date = st.date_input('Maturity Date')
            original_balance = st.number_input('Original Balance', min_value=0.0, format='%f')
            note_rate = st.number_input('Note Rate (%)', min_value=0.0, format='%f')
            interest_only_period = st.number_input('Interest Only Period (months)', min_value=0)
            amortization_period = st.number_input('Amortization Period (months)', min_value=0)
            day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"])

            loan_data = {
                'loan_exists': loan_exists,
                'origination_date': origination_date,
                'maturity_date': maturity_date,
                'original_balance': original_balance,
                'note_rate': note_rate,
                'interest_only_period': interest_only_period,
                'amortization_period': amortization_period,
                'day_count_method': day_count_method
            }
            loan_data_list.append(loan_data)

    # Financial Data inputs for new property
    with st.expander("Financial Data"):
        columns = ['Date', 'Net Operating Income', 'Capital Expenditures']
        # Create a blank DataFrame
        fin_df = pd.DataFrame(columns=columns)
        fin_df = st.data_editor(fin_df)

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
            buyout_date=_standardize_date(buyout_date),
            buyout_amount=buyout_amount,
            loans=[],  # Initialize with an empty list of loans
        )

        for loan_data in loan_data_list:
            if loan_data['loan_exists']:
                new_loan = Loan(
                    origination_date=loan_data['origination_date'],
                    maturity_date=loan_data['maturity_date'],
                    original_balance=loan_data['original_balance'],
                    note_rate=loan_data['note_rate'] / 100,
                    interest_only_period=loan_data['interest_only_period'],
                    amortization_period=loan_data['amortization_period'],
                    day_count_method=loan_data['day_count_method']
                )
                new_property.add_loan(new_loan)
        new_property.add_noi_capex(fin_df)
        st.session_state.properties.append(new_property)
        st.success("New property added successfully.")
        st.experimental_rerun()  # Rerun to reflect the new property in the session state

# Save session state button
if st.button("Save Session State"):
    save_session_state()
    st.success("Session state saved to file.")

if 'properties' in st.session_state and property_id in [prop.property_id for prop in st.session_state.properties]:
    if st.button("Delete Property"):
        st.session_state.properties = [prop for prop in st.session_state.properties if prop.property_id != property_id]
        st.rerun()
