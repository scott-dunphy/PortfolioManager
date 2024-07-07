import pandas as pd
from property import Property
from loan import Loan
from datetime import date
from typing import List
import streamlit as st
from typing import List, Tuple

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
        for loan in self.unsecured_loans:
            if loan.loan_id == loan_id:
                return loan
        raise ValueError(f"Unsecured loan with ID {loan_id} not found in the portfolio.")
  
    
    def aggregate_hold_period_cash_flows(self) -> Tuple[pd.DataFrame, List[str]]:
        debug_logs = []
        # Initialize an empty DataFrame with date range index
        date_range = pd.date_range(self.start_date, self.end_date, freq='MS')
        aggregate_cf = pd.DataFrame(0, index=date_range, columns=['Cash Flow'])
    
        # Aggregate property cash flows
        for property in self.properties:
            property_cf = property.hold_period_cash_flows_x(start_date=self.start_date, end_date=self.end_date)
            # Ensure the DataFrame is within the specified date range
            property_cf = property_cf[(property_cf.index >= self.start_date) & (property_cf.index <= self.end_date)]
            aggregate_cf = aggregate_cf.add(property_cf, fill_value=0)
    
        # Aggregate loan cash flows
        if self.unsecured_loans:
            for loan in self.unsecured_loans:
                loan_schedule = loan.get_unsecured_schedule()
                loan_cf = pd.DataFrame(loan_schedule)
                
                # Add to debug logs
                debug_logs.append("Initial loan schedule DataFrame:")
                debug_logs.append(loan_cf.to_string())
    
                try:
                    # Convert 'date' column to datetime and set as index
                    loan_cf['date'] = pd.to_datetime(loan_cf['date'], errors='coerce')
                    loan_cf.set_index('date', inplace=True)
                except Exception as e:
                    debug_logs.append("Error converting date column to datetime: " + str(e))
                
                aggregate_cf = aggregate_cf.add(loan_cf, fill_value=0)
    
        return aggregate_cf
