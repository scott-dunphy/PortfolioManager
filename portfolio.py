import pandas as pd
from property import Property
from loan import Loan
from datetime import date
from typing import List

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
  
    def aggregate_hold_period_cash_flows(self) -> pd.DataFrame:
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
                
                # Debug: Log the initial loan schedule
                #st.write("Initial loan schedule DataFrame:")
                st.write(loan_cf)
    
                # Convert 'date' column to datetime and set as index
                loan_cf['date'] = pd.to_datetime(loan_cf['date'], errors='coerce')
                loan_cf.set_index('date', inplace=True)
    
                # Debug: Log the converted index
                st.write("Converted loan_cf.index type:", type(loan_cf.index))
                st.write("Converted loan_cf.index:", loan_cf.index)
    
                # Check for any NaT (Not a Time) values that could cause issues
                if loan_cf.index.isna().any():
                    st.write("Warning: loan_cf.index contains NaT values after conversion.")
                
                # Ensure the DataFrame is within the specified date range
                start_date_dt = pd.to_datetime(self.start_date)
                end_date_dt = pd.to_datetime(self.end_date)
    
                st.write(f"Filtering loan_cf with start_date: {start_date_dt} and end_date: {end_date_dt}")
                
                try:
                    loan_cf = loan_cf[(loan_cf.index >= start_date_dt) & (loan_cf.index <= end_date_dt)]
                except Exception as e:
                    st.write("Error during filtering:", e)
    
                # Debug: Log the filtered loan_cf DataFrame
                st.write("Filtered loan_cf DataFrame:")
                st.write(loan_cf)
                
                aggregate_cf = aggregate_cf.add(loan_cf, fill_value=0)
    
        return aggregate_cf
