from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict
import pandas as pd
import streamlit as st

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import uuid
import pandas as pd
import json
from loan import Loan


class Property:
    def __init__(
        self,
        property_id: str,
        name: str,
        address: str,
        property_type: str,
        square_footage: float,
        year_built: int,
        purchase_price: float,
        purchase_date: date,
        analysis_start_date: date,
        analysis_end_date: date,
        current_value: Optional[float] = None,
        sale_date: Optional[date] = None,
        sale_price: Optional[float] = None,
        loan: Optional['Loan'] = None,
        noi: Optional[Dict[date, float]] = None,
        capex: Optional[Dict[date, float]] = None,
        ownership_share: float = 1,
        buyout_date: Optional[date] = None,
        buyout_amount: Optional[float] = None
    ):
        self.property_id = property_id
        self.name = name
        self.address = address
        self.property_type = property_type
        self.square_footage = square_footage
        self.year_built = year_built
        self.purchase_price = purchase_price
        self.purchase_date = self._standardize_date(purchase_date)
        self.analysis_start_date = self._standardize_date(analysis_start_date)
        self.analysis_end_date = self._standardize_date(analysis_end_date)
        self.sale_date = pd.Timestamp(self._standardize_date(sale_date)) if sale_date else None
        self.sale_price = sale_price
        self.current_value = current_value if current_value is not None else purchase_price
        self.loan = loan
        self.noi = self._standardize_cash_flow_dates(noi) if noi is not None else {}
        self.capex = self._standardize_cash_flow_dates(capex) if capex is not None else {}
        self.ownership_share = ownership_share
        self._initialize_ownership_share()
        #self._align_noi_and_capex()
        self.buyout_date = None
        self.buyout_amount = 0
        
    def to_dict(self):
        return {
            'name': self.name,
            'address': self.address,
            'property_type': self.property_type,
            'square_footage': self.square_footage,
            'year_built': self.year_built,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat(),
            'analysis_start_date': self.analysis_start_date.isoformat(),
            'analysis_end_date': self.analysis_end_date.isoformat(),
            'ownership_share': self.ownership_share,
            'current_value': self.current_value,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'sale_price': self.sale_price,
            'loan': self.loan.to_dict() if self.loan else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            address=data['address'],
            property_type=data['property_type'],
            square_footage=data['square_footage'],
            year_built=data['year_built'],
            purchase_price=data['purchase_price'],
            purchase_date=date.fromisoformat(data['purchase_date']),
            analysis_start_date=date.fromisoformat(data['analysis_start_date']),
            analysis_end_date=date.fromisoformat(data['analysis_end_date']),
            ownership_share=data['ownership_share'],
            current_value=data['current_value'],
            sale_date=date.fromisoformat(data['sale_date']) if data['sale_date'] else None,
            sale_price=data['sale_price'],
            loan=Loan.from_dict(data['loan']) if data['loan'] else None
        )

    def _standardize_date(self, d: date) -> pd.Timestamp:
        """Standardize a date to the first of its month."""
        return pd.Timestamp(date(d.year, d.month, 1))

    def _standardize_cash_flow_dates(self, cash_flows: Dict[date, float]) -> Dict[pd.Timestamp, float]:
        """Standardize all dates in a cash flow dictionary to the first of their respective months."""
        return {self._standardize_date(d): v for d, v in cash_flows.items()}

    def _initialize_ownership_share(self):
        ownership_dict = {}
        current_date = self.analysis_start_date
        end_date = self.analysis_end_date
        while current_date <= end_date:
            ownership_dict[current_date] = self.ownership_share
            current_date += relativedelta(months=1)
        self.ownership_share_series = ownership_dict

    #def _align_noi_and_capex(self):
    #    """Ensure that NOI and CapEx have the same dates, with CapEx defaulting to 0."""
    ##    all_dates = set(self.noi.keys()) | set(self.capex.keys())
    #   for d in all_dates:
    #        if d not in self.noi:
    #            self.noi[d] = 0
    #        if d not in self.capex:
    #            self.capex[d] = 0

    def add_loan(self, loan: 'Loan'):
        self.loan = loan

    def add_noi(self, _date: 'datetime', noi: 'float'):
        self.noi[_date] = noi

    def add_capex(self, _date: 'datetime', capex: 'float'):
        self.capex[_date] = capex

    def remove_loan(self):
        self.loan = None

    def get_loan_details(self) -> str:
        if self.loan:
            return f"Loan Details: Original Balance: ${self.loan.original_balance:,.2f}, " \
                   f"Interest Rate: {self.loan.note_rate * 100:.2f}%, " \
                   f"Maturity Date: {self.loan.maturity_date}"
        else:
            return "This property is not encumbered."

    def calculate_equity(self, as_of_date: date = date.today()) -> float:
        as_of_date = self._standardize_date(as_of_date)
        if self.loan:
            return self.current_value - self.loan.get_current_balance(as_of_date)
        else:
            return self.current_value

    def calculate_ltv(self, as_of_date: date = date.today()) -> float:
        as_of_date = self._standardize_date(as_of_date)
        if self.loan:
            return self.loan.get_current_balance(as_of_date) / self.current_value
        else:
            return 0.0

    def add_financial_data(self, date: date, noi: float, capex: float = 0):
            date = self._standardize_date(date)
            self.noi[date] = noi
            self.capex[date] = capex
            self._align_noi_and_capex()
            
    def streamlit_add_noi(self, noi: [float]):
        noi_length = len(noi)
        noi = noi.split(" ")
        noi = [float(x) for x in noi]
        dates = pd.date_range(start=self.analysis_start_date, periods=noi_length, freq='MS')
        
        # Create a new NOI dictionary
        new_noi = dict(zip(dates, noi))
        
        # Update the property's NOI
        self.noi = new_noi
            
    def streamlit_add_capex(self, capex: [float]):
        capex_length = len(capex)
        capex = capex.split(" ")
        capex = [float(x) for x in capex]
        dates = pd.date_range(start=self.analysis_start_date, periods=capex_length, freq='MS')
        
        # Create a new NOI dictionary
        new_capex = dict(zip(dates, capex))
        
        # Update the property's NOI
        self.capex = new_capex

    def get_cash_flows_dataframe(self, ownership_adjusted: bool = True, start_date: Optional[pd.Timestamp] = None, end_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        if start_date is None:
            start_date = self.analysis_start_date
        if end_date is None:
            end_date = self.analysis_end_date
        # Generate a date range for the entire analysis period
        if self.sale_date:
            end_date = min(pd.Timestamp(end_date), pd.Timestamp(self.sale_date))
        dates = pd.date_range(start=self._standardize_date(start_date), end=end_date, freq='MS')
    
        # Create a DataFrame with these dates as the index
        cash_flows_df = pd.DataFrame(index=dates, columns=[
            'Ownership Share',
            'Purchase Price',
            'Net Operating Income',
            'Capital Expenditures',
            'Interest Expense',
            'Principal Payments',
            'Loan Proceeds',
            'Sale Proceeds',
            'Partner Buyout',
            'Debt Scheduled Repayment',
            'Debt Early Prepayment',
        ])
        
        cash_flows_df.at[pd.Timestamp(self.purchase_date), 'Purchase Price'] = self.purchase_price
    
        # Fill in the DataFrame with cash flow data
        for date in dates:
            standardized_date = pd.Timestamp(self._standardize_date(date.date()))
            cash_flows_df.at[standardized_date, 'Ownership Share'] = self.ownership_share_series.get(standardized_date, 1.0)
            cash_flows_df.at[standardized_date, 'Net Operating Income'] = self.noi.get(standardized_date, 0)
            cash_flows_df.at[standardized_date, 'Capital Expenditures'] = self.capex.get(standardized_date, 0)
    
        if self.loan:
            loan_cash_flows = self.loan.get_schedule()
            for loan_cf in loan_cash_flows:
                standardized_date = pd.Timestamp(self._standardize_date(loan_cf['date']))
                cash_flows_df.at[standardized_date, 'Interest Expense'] = loan_cf['Interest Expense']
                cash_flows_df.at[standardized_date, 'Principal Payments'] = loan_cf['Principal Payments']
                if standardized_date == pd.Timestamp(self.loan.origination_date):
                    cash_flows_df.at[standardized_date, 'Loan Proceeds'] = self.loan.original_balance
                if standardized_date == pd.Timestamp(self.loan.maturity_date) and not self.sale_date:
                    cash_flows_df.at[standardized_date, 'Debt Repayment'] = self.loan.get_current_balance(self.loan.maturity_date)
    
        if self.sale_date is not None:
            cash_flows_df.at[pd.Timestamp(self.sale_date), 'Sale Proceeds'] = self.sale_price
            if self.loan:
                cash_flows_df.at[pd.Timestamp(self.sale_date), 'Debt Early Prepayment'] = self.loan.get_current_balance(pd.Timestamp(self.sale_date))
    
        for col in cash_flows_df.columns[1:]:
            adjusted_column = "Adjusted " + col
            cash_flows_df[adjusted_column] = cash_flows_df[col] * cash_flows_df['Ownership Share']
    
        if self.buyout_date:
            standardized_buyout_date = pd.Timestamp(self.buyout_date)
            cash_flows_df.at[standardized_buyout_date, 'Partner Buyout'] = self.buyout_amount
            cash_flows_df.at[standardized_buyout_date, 'Adjusted Partner Buyout'] = self.buyout_amount
    
        # Replace NaN values with 0
        cash_flows_df.fillna(0, inplace=True)
    
        return cash_flows_df

    def calculate_cash_flow_before_debt_service(self, start_date: date, end_date: date, ownership_adjusted: bool = True) -> Dict[pd.Timestamp, float]:
        start_date = self._standardize_date(start_date)
        end_date = self._standardize_date(end_date)
        cf_before_debt = {}
        for d in self.noi.keys():
            if start_date <= d <= end_date:
                noi = self.noi[d]
                capex = self.capex[d]
                if ownership_adjusted:
                    ownership_share = self.ownership_share_series.get(d, 1.0)
                    noi *= ownership_share
                    capex *= ownership_share
                cf_before_debt[d] = noi - capex
        return cf_before_debt

    def calculate_cash_flow_after_debt_service(self, start_date: date, end_date: date, ownership_adjusted: bool = True) -> Dict[pd.Timestamp, float]:
        cf_before_debt = self.calculate_cash_flow_before_debt_service(start_date, end_date, ownership_adjusted)
        
        if not self.loan:
            return cf_before_debt
    
        cf_after_debt = {}
        for d in cf_before_debt.keys():
            interest, principal = self.loan.get_monthly_interest_and_principal(d)
            loan_payment = interest + principal
            cf_after_debt[d] = cf_before_debt[d] - loan_payment
        
        return cf_after_debt
    
    def hold_period_cash_flows_x(self, ownership_adjusted: bool = True, start_date: Optional[pd.Timestamp] = None, end_date: Optional[pd.Timestamp] = None) -> Dict[pd.Timestamp, float]:
        if start_date is None:
            start_date = self.analysis_start_date
        if end_date is None:
            end_date = self.analysis_end_date

        start_date = self._standardize_date(start_date)
        end_date = self._standardize_date(end_date)
        
        if self.buyout_date:
            self.update_ownership_share(self.buyout_date,1)
        df = self.get_cash_flows_dataframe(start_date=start_date, end_date=end_date)
    
        # Define the columns that need their signs changed
        columns_to_change_sign = ['Capital Expenditures', 'Purchase Price', 'Interest Expense','Principal Payments','Partner Buyout','Debt Scheduled Repayment','Debt Early Prepayment']  # Replace with your actual column names
    
        adjusted_columns = [col for col in df.columns if 'Adjusted' in col]
        if ownership_adjusted:
            cf_df = df[adjusted_columns]
            cf_df['Ownership Share'] = df['Ownership Share']
            cf_df [['Ownership Share','Adjusted Purchase Price','Adjusted Loan Proceeds','Adjusted Net Operating Income','Adjusted Capital Expenditures','Adjusted Interest Expense','Adjusted Principal Payments','Adjusted Debt Scheduled Repayment','Adjusted Debt Early Prepayment','Adjusted Sale Proceeds','Adjusted Partner Buyout']]
        else:
            non_adjusted_columns = [col for col in df.columns if 'Adjusted' not in col]
            cf_df = df[non_adjusted_columns]
            cf_df['Ownership Share'] = df['Ownership Share']
        
        
    
        # Adjust the signs of the specified columns
        for col in columns_to_change_sign:
            adjusted_col_name = f'Adjusted {col}' if ownership_adjusted else col
            if adjusted_col_name in cf_df.columns:
                cf_df[adjusted_col_name] = -cf_df[adjusted_col_name]
    
        # Calculate the Total column
        cf_df['Total Cash Flow'] = cf_df.drop(columns=['Ownership Share']).sum(axis=1)
    
        return cf_df
    

    def update_ownership_share(self, start_date: date, new_share: float):
            """
            Update the ownership share starting from the given date.
            
            Parameters:
            - start_date: The date from which the new ownership share applies.
            - new_share: The new ownership share (e.g., 1.0 for full ownership).
            """
            print(f"Debug: Entering update_ownership_share method")
            print(f"Debug: start_date type: {type(start_date)}, value: {start_date}")
            print(f"Debug: new_share type: {type(new_share)}, value: {new_share}")
            print(f"Debug: self.analysis_end_date type: {type(self.analysis_end_date)}, value: {self.analysis_end_date}")
    
            start_date = pd.Timestamp(self._standardize_date(start_date))
            print(f"Debug: Standardized start_date: {start_date}")
    
            # Update ownership share for the start_date and all subsequent dates
            for d in sorted(self.ownership_share_series.keys()):
                if d >= start_date:
                    self.ownership_share_series[d] = new_share
    
            # Ensure the ownership share for future dates not already in the dictionary
            max_existing_date = pd.Timestamp(max(self.ownership_share_series.keys(), default=start_date))
            current_date = max(start_date, max_existing_date)
            print(f"Debug: current_date before loop: {current_date}")
    
            try:
                while pd.Timestamp(current_date) <= pd.Timestamp(self.analysis_end_date):
                    self.ownership_share_series[current_date] = new_share
                    current_date += relativedelta(months=1)
                    print(f"Debug: Updated date in loop: {current_date}")
            except TypeError as e:
                print(f"Debug: TypeError occurred: {e}")
                print(f"Debug: current_date type: {type(current_date)}, value: {current_date}")
                print(f"Debug: self.analysis_end_date type: {type(self.analysis_end_date)}, value: {self.analysis_end_date}")
            except Exception as e:
                print(f"Debug: Unexpected error occurred: {e}")
    
            print("Debug: Exiting update_ownership_share method")

    def buy_out_partner(self, buyout_date: date, buyout_amount: float):
        """
        Buy out a partner's share of the property.
        
        Parameters:
        - buyout_date: The date of the buyout.
        - buyout_amount: The amount paid to buy out the partner's share.
        """
        standardized_date = self._standardize_date(buyout_date)
        self.update_ownership_share(standardized_date, 1.0)
        self.buyout_amount = buyout_amount
        self.buyout_date = standardized_date

    def sell_property(self, sale_date: date, sale_price: float):
        """
        Sell the property on the specified date for the specified price.
        This method updates the property's sale information and handles loan payoff if applicable.
        
        Parameters:
        - sale_date: The date of the sale.
        - sale_price: The sale price of the property.
        """
        standardized_sale_date = self._standardize_date(sale_date)
        
        if standardized_sale_date <= self.purchase_date:
            raise ValueError("Sale date must be after the purchase date.")
        
        if sale_price <= 0:
            raise ValueError("Sale price must be positive.")
    
        self.sale_date = standardized_sale_date
        self.sale_price = sale_price
        self.current_value = sale_price
    
        if self.loan:
            loan_balance = self.loan.get_current_balance(self.sale_date)
            if loan_balance > 0:
                print(f"Loan balance of ${loan_balance:,.2f} paid off upon sale.")
    
        print(f"Property sold on {self.sale_date} for ${self.sale_price:,.2f}")

    def __str__(self) -> str:
        loan_status = "Encumbered" if self.loan else "Unencumbered"
        sale_info = f", Sold on {self.sale_date} for ${self.sale_price:,.2f}" if self.sale_date else ""
        return f"{self.name} - {self.address} ({self.property_type}) - {loan_status} - Purchased on {self.purchase_date}{sale_info} - Analysis period: {self.analysis_start_date} to {self.analysis_end_date}"

