import pandas as pd
from property import Property
from loan import Loan
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict

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
