import pandas as pd
from property import Property
from loan import Loan
from datetime import date
from typing import List
import streamlit as st

class Portfolio:
    def __init__(self, name: str, start_date: date, end_date: date, properties: List['Property'] = None, unsecured_loans: List['Loan'] = None, beg_cash = 0):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.properties = properties or []
        self.unsecured_loans = unsecured_loans or []
        self.beg_cash = beg_cash or 0
        self.capital_flows = pd.DataFrame(columns=['Capital Call', 'Redemption Payment']).rename_axis('Date')

    def _standardize_date(self, d: date) -> date:
        """Standardize a date to the first of its month."""
        return date(d.year, d.month, 1)
        
    def add_property(self, property: 'Property'):

        self.properties.append(property)

    def add_capital_flows(self, df: pd.DataFrame):
        df.index = df.index.map(self._standardize_date)
        self.capital_flows = pd.concat([self.capital_flows, df])
  
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

    def validate_date_index(self, df: pd.DataFrame) -> bool:
        """
        Validate that the DataFrame index is of type date.
    
        Parameters:
        df (pd.DataFrame): The DataFrame to validate.
    
        Returns:
        bool: True if the index is of type date, False otherwise.
        """
        return all(isinstance(idx, date) for idx in df.index)
    
    def aggregate_hold_period_cash_flows(self, start_date: date=None, end_date: date=None) -> pd.DataFrame:
        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date
        date_range = pd.date_range(start_date, end_date, freq='MS').to_pydatetime()
        # Initialize an empty DataFrame with date range index
        columns_order = [
            'Capital Call', 'Redemption Payment', 'Adjusted Purchase Price', 'Adjusted Loan Proceeds', 'Adjusted Net Operating Income',
            'Adjusted Capital Expenditures', 'Adjusted Interest Expense', 'Adjusted Principal Payments',
            'Adjusted Debt Scheduled Repayment', 'Adjusted Debt Early Prepayment', 'Adjusted Sale Proceeds',
            'Adjusted Partner Buyout', 'Total Cash Flow'
        ]
        aggregate_cf = pd.DataFrame(0, index=date_range, columns=columns_order)
        aggregate_cf.index = aggregate_cf.index.map(lambda x: x.date())  # Ensure index is in date format
    
        # Aggregate property cash flows
        for property in self.properties:
            property_cf = property.hold_period_cash_flows(start_date=start_date, end_date=end_date)
            # Ensure the DataFrame is within the specified date range
            property_cf = property_cf.loc[(property_cf.index >= start_date) & (property_cf.index <= end_date)]
            aggregate_cf = aggregate_cf.add(property_cf, fill_value=0)

        aggregate_cf = aggregate_cf.add(self.capital_flows, fill_value=0)
    
        # Aggregate loan cash flows
        if self.unsecured_loans:
            for loan in self.unsecured_loans:
                loan_schedule = loan.get_unsecured_schedule()
                loan_cf = pd.DataFrame(loan_schedule)
                loan_cf['date'] = pd.to_datetime(loan_cf['date'], errors='coerce').dt.date
                loan_cf.set_index('date', inplace=True)
    
                # Ensure columns match the order
                for column in columns_order:
                    if column not in loan_cf.columns:
                        loan_cf[column] = 0
    
                loan_cf = loan_cf[columns_order]
                aggregate_cf = aggregate_cf.add(loan_cf, fill_value=0)
    
        # Reorder the columns
        aggregate_cf = aggregate_cf[columns_order]
        aggregate_cf.drop(columns=['Total Cash Flow'],inplace=True)
    
        # Ensure the dates are consistent
        #aggregate_cf = aggregate_cf.loc[start_date:end_date]
    
        return aggregate_cf

    def calculate_monthly_cash(self) -> pd.DataFrame:
        aggregate_cf = self.aggregate_hold_period_cash_flows()
        monthly_cash = pd.DataFrame(index=aggregate_cf.index, columns=['Beginning Cash', 'Monthly Cash Flow', 'Ending Cash'])
        
        monthly_cash['Monthly Cash Flow'] = aggregate_cf.sum(axis=1)
        monthly_cash['Beginning Cash'].iloc[0] = self.beg_cash
        monthly_cash['Ending Cash'].iloc[0] = self.beg_cash + monthly_cash['Monthly Cash Flow'].iloc[0]
        
        for i in range(1, len(monthly_cash)):
            monthly_cash['Beginning Cash'].iloc[i] = monthly_cash['Ending Cash'].iloc[i-1]
            monthly_cash['Ending Cash'].iloc[i] = monthly_cash['Beginning Cash'].iloc[i] + monthly_cash['Monthly Cash Flow'].iloc[i]
        
        return monthly_cash

    def calculate_monthly_dscr(self) -> pd.DataFrame:
        """
        Calculate the Debt Service Coverage Ratio (DSCR) by month.
        
        DSCR = Net Operating Income / (Interest Expense + Principal Payments)
        
        Returns:
        pd.DataFrame: A DataFrame with the DSCR calculated for each month.
        """
        # Aggregate the cash flows over the hold period
        aggregate_cf = self.aggregate_hold_period_cash_flows()

        # Extract the necessary columns for DSCR calculation
        noi = aggregate_cf['Adjusted Net Operating Income']
        interest_expense = aggregate_cf['Adjusted Interest Expense']
        principal_payments = aggregate_cf['Adjusted Principal Payments']
        
        # Calculate the Debt Service Coverage Ratio
        debt_service = interest_expense + principal_payments
        dscr = noi / debt_service
        
        # Create a DataFrame to hold the results
        dscr_df = pd.DataFrame({
            'Net Operating Income': noi,
            'Interest Expense': interest_expense,
            'Principal Payments': principal_payments,
            'Debt Service': debt_service,
            'DSCR': dscr
        })
        
        return dscr_df
