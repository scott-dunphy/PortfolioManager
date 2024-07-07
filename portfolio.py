import pandas as pd
from property import Property
from loan import Loan
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import streamlit as st





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
      date_range = pd.date_range(self.start_date, self.end_date, freq='MS')
      aggregate_cf = pd.DataFrame(0, index=date_range, columns=['Cash Flow'])
  
      # Aggregate property cash flows
      for property in self.properties:
          property_cf = property.hold_period_cash_flows_x(start_date=self.start_date, end_date=self.end_date )
          # Ensure the DataFrame is within the specified date range
          property_cf = property_cf[(property_cf.index >= self.start_date) & (property_cf.index <= self.end_date)]
          aggregate_cf = aggregate_cf.add(property_cf, fill_value=0)
          aggregate_cf = aggregate_cf[['Adjusted Purchase Price','Adjusted Loan Proceeds','Adjusted Net Operating Income','Adjusted Capital Expenditures','Adjusted Interest Expense','Adjusted Principal Payments','Adjusted Debt Scheduled Repayment','Adjusted Debt Early Prepayment','Adjusted Sale Proceeds','Adjusted Partner Buyout','Total Cash Flow']]
  
      # Aggregate loan cash flows
      if self.unsecured_loans:
          for loan in self.unsecured_loans:
              loan_cf = pd.DataFrame(loan.get_unsecured_schedule())
              # Ensure the DataFrame is within the specified date range
              loan_cf = loan_cf[(loan_cf.index >= self.start_date) & (loan_cf.index <= self.end_date)]
              aggregate_cf = aggregate_cf.add(loan_cf, fill_value=0)
  
      return aggregate_cf
