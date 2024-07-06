import pandas as pd
from property import Property
from loan import Loan
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import streamlit as st


# Initialize session state for properties
if 'properties' not in st.session_state:
    st.session_state.properties = [
        Property(
            property_id="CRE001",
            name="Downtown Office Building",
            address="123 Main St, Anytown, USA",
            property_type="Office",
            square_footage=50000.0,
            year_built=1995,
            purchase_price=25000000.00,
            purchase_date=date(2023, 1, 1),
            analysis_start_date=date(2023, 1, 1),
            analysis_end_date=date(2025, 12, 1),
            current_value=25000000.00,
            ownership_share=0.8
        ),
        Property(
            property_id="CRE002",
            name="Suburban Retail Center",
            address="456 Elm St, Anytown, USA",
            property_type="Retail",
            square_footage=75000.0,
            year_built=2005,
            purchase_price=35000000.00,
            purchase_date=date(2023, 1, 1),
            analysis_start_date=date(2023, 1, 1),
            analysis_end_date=date(2025, 12, 1),
            current_value=35000000.00,
            ownership_share=1.0
        )
    ]

properties = st.session_state.properties


class Portfolio:
  def __init__(self, name: str, start_date: date, end_date: date, properties: List['Property'] = None, unsecured_loans: List['Loan'] = None):
    self.name = name
    self.start_date = start_date
    self.end_date = end_date
    self.properties = properties or []
    self.unsecured_loans = unsecured_loans or []

def add_property(self, property: 'Property'):
        self.properties.append(property)

def remove_property(self, property_id: str):
    self.properties = [p for p in self.properties if p.property_id != property_id]

def get_property(self, property_id: str) -> 'Property':
    for property in self.properties:
        if property.property_id == property_id:
            return property
    raise ValueError(f"Property with ID {property_id} not found in the portfolio.")

def add_unsecured_loan(self, loan: 'Loan'):
    self.unsecured_loans.append(loan)

def remove_unsecured_loan(self, loan_id: str):
    self.unsecured_loans = [l for l in self.unsecured_loans if l.loan_id != loan_id]

def get_unsecured_loan(self, loan_id: str) -> 'Loan':
    for loan in self.unsecured:
        if loan.loan_id == loan_id:
            return loan
    raise ValueError(f"Unsecured loan with ID {loan_id} not found in the portfolio.")

def aggregate_hold_period_cash_flows(self) -> pd.DataFrame:
    # Initialize an empty DataFrame with date range index
    date_range = pd.date_range(self.start_date, self.end_date)
    aggregate_cf = pd.DataFrame(0, index=date_range, columns=['Cash Flow'])

    # Aggregate property cash flows
    for property in self.properties:
        property_cf = property.hold_period_cash_flows_x()
        # Ensure the DataFrame is within the specified date range
        property_cf = property_cf[(property_cf.index >= self.start_date) & (property_cf.index <= self.end_date)]
        aggregate_cf = aggregate_cf.add(property_cf, fill_value=0)

    # Aggregate loan cash flows
    #for loan in self.standalone_loans:
    #    loan_cf = loan.calculate_cash_flows()
    #    # Ensure the DataFrame is within the specified date range
    #    loan_cf = loan_cf[(loan_cf.index >= self.start_date) & (loan_cf.index <= self.end_date)]
    #    aggregate_cf = aggregate_cf.subtract(loan_cf, fill_value=0)

    return aggregate_cf
