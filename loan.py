from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import uuid
import pandas as pd
import json


class Loan:    
    @property
    def amortization_period(self):
        return self._amortization_period

    @amortization_period.setter
    def amortization_period(self, value):
        self._amortization_period = value
        self._calculate_monthly_payment()
        self.get_schedule()
        
    def __init__(
        self,
        origination_date: date,
        maturity_date: date,
        original_balance: float,
        note_rate: float,
        interest_only_period: Optional[int] = None,
        amortization_period: Optional[int] = None,
        day_count_method: str = "30/360",
        loan_id: Optional[str] = None
    ):
        self.loan_id = loan_id if loan_id is not None else str(uuid.uuid4())
        self.origination_date = self._adjust_to_month_start(origination_date)
        self.maturity_date = self._adjust_to_month_start(
            pd.Timestamp(maturity_date))
        self.original_balance = original_balance
        self.note_rate = note_rate / 100  # Convert to decimal
        self.day_count_method = day_count_method

        # Calculate total loan term in months
        self.total_months = (self.maturity_date.year - self.origination_date.year) * 12 + \
                            (self.maturity_date.month - self.origination_date.month)

        # Handle optional parameters
        self.interest_only_period = interest_only_period if interest_only_period is not None else 0
        self._amortization_period = amortization_period if amortization_period is not None else self.total_months - self.interest_only_period
        self.monthly_payment = self._get_monthly_payment()
        self.schedule = self.get_schedule()

        self._validate_inputs()
        
    def to_dict(self):
        return {
            'origination_date': self.origination_date.isoformat(),
            'maturity_date': self.maturity_date.isoformat(),
            'original_balance': self.original_balance,
            'note_rate': self.note_rate,
            'interest_only_period': self.interest_only_period,
            'amortization_period': self.amortization_period,
            'day_count_method': self.day_count_method
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            origination_date=date.fromisoformat(data['origination_date']),
            maturity_date=date.fromisoformat(data['maturity_date']),
            original_balance=data['original_balance'],
            note_rate=data['note_rate'],
            interest_only_period=data['interest_only_period'],
            amortization_period=data['amortization_period'],
            day_count_method=data['day_count_method']
        )

    def _adjust_to_month_start(self, date_to_adjust: pd.Timestamp) -> pd.Timestamp:
        """Adjust the given date to the first day of the current month if it's not already the first day of a month."""
        return date_to_adjust.replace(day=1)

    def _validate_inputs(self):
        assert self.origination_date < self.maturity_date, "Origination date must be before maturity date."
        assert self.original_balance > 0, "Original balance must be positive."
        assert 0 < self.note_rate < 1, "Note rate must be between 0 and 100 percent."
        assert self.interest_only_period >= 0, "Interest-only period must be non-negative."
        assert self.amortization_period >= 0, "Amortization period must be positive."
        assert self.day_count_method in [
            "Actual/360", "Actual/365", "30/360"], "Invalid day count method."

    def _calculate_monthly_payment(self):
        if self.amortization_period > 0:
            monthly_rate = self.note_rate / 12
            self.monthly_payment = self.original_balance * (monthly_rate * (1 + monthly_rate)**self.amortization_period) / \
                ((1 + monthly_rate)**self.amortization_period - 1)
        else:
            self.monthly_payment = 0

    def _calculate_interest(self, balance: float, start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        if self.day_count_method == "30/360":
            days = 30
            year_basis = 360
        elif self.day_count_method == "Actual/360":
            days = (end_date - start_date).days
            year_basis = 360
        else:  # Actual/365
            days = (end_date - start_date).days
            year_basis = 365
        return balance * self.note_rate * days / year_basis

    def get_monthly_interest_and_principal(self, current_date: pd.Timestamp) -> Tuple[float, float]:
        if current_date < self.origination_date or current_date > self.maturity_date:
            return 0, 0

        months_since_origination = (current_date.year - self.origination_date.year) * \
            12 + current_date.month - self.origination_date.month - 1
        if months_since_origination < self.interest_only_period:
            interest = self._calculate_interest(
                self.original_balance, current_date, current_date + relativedelta(months=1))
            principal = 0
        else:
            current_balance = self.get_current_balance(
                current_date + relativedelta(months=-1))
            interest = self._calculate_interest(
                current_balance, current_date, current_date + relativedelta(months=1))
            principal = self.monthly_payment - interest if self.monthly_payment else 0
        return interest, principal

    def _standardize_date(self, d: pd.Timestamp) -> pd.Timestamp:
        """Standardize a date to the first of its month."""
        return d.replace(day=1)

    def get_schedule(self) -> List[Dict[str, float]]:
        self._calculate_monthly_payment()
        cash_flows = []
        current_date = self.origination_date
        current_balance = self.original_balance

        # Add the initial cash flow (loan disbursement)
        cash_flows.append({
            'date': self._standardize_date(current_date),
            'Beginning Balance': self.original_balance,
            'Interest Expense': 0,
            'Principal Payments': 0,
            'Total Payment': -self.original_balance,
            'Ending Balance': self.original_balance
        })

        while current_date < self.maturity_date:
            next_date = min(
                current_date + relativedelta(months=1), self.maturity_date)
            standardized_date = self._standardize_date(next_date)
            interest = self._calculate_interest(
                current_balance, current_date, next_date)

            months_since_origination = (current_date.year - self.origination_date.year) * 12 + \
                current_date.month - self.origination_date.month

            if months_since_origination < self.interest_only_period:
                principal = 0
                payment = interest
            else:
                payment = self.monthly_payment
                principal = payment - interest

            current_balance -= principal
            cash_flows.append({
                'date': standardized_date,
                'Beginning Balance': cash_flows[-1]['Ending Balance'],
                'Interest Expense': interest,
                'Principal Payments': principal,
                'Total Payment': payment,
                'Ending Balance': current_balance
            })
            current_date = next_date
        self.schedule = cash_flows

        return cash_flows

        # Adjust final payment if necessary
        if abs(current_balance) > 0.01:
            final_payment = current_balance + cash_flows[-1]['Total Payment']
            cash_flows[-1] = {
                'date': self.maturity_date,
                'Loan Proceeds': 0,
                'Interest Expense': 0,
                'Principal Payments': 0,
                'Debt Repayment': current_balance,
                'Total Payment': final_payment
            }

        return cash_flows

    def get_cash_flows(self) -> Dict[pd.Timestamp, float]:
        """
        Calculate the total cash flows of the loan.
        Includes loan proceeds as a positive cash flow, loan payments as negative cash flows,
        and debt repayment at maturity as a negative cash flow.
        Returns a dictionary with dates as keys and cash flows as values.
        """
        cash_flows = {}
    
        # Add the loan proceeds at origination as a positive cash flow
        cash_flows[self.origination_date] = self.original_balance
    
        # Add the regular loan payments as negative cash flows
        for entry in self.schedule[1:]:
            date = entry['date']
            cash_flows[date] = cash_flows.get(date, 0) - entry['Total Payment']
    
        # Add the debt repayment at maturity as a negative cash flow
        maturity_date = self.maturity_date
        if maturity_date in cash_flows:
            cash_flows[maturity_date] -= self.get_current_balance(maturity_date)
        else:
            cash_flows[maturity_date] = -self.get_current_balance(maturity_date)
    
        return cash_flows

    def calculate_debt_service(self, calculation_date: pd.Timestamp) -> float:
        if self.origination_date <= calculation_date <= self.maturity_date:
            months_from_origination = (calculation_date.year - self.origination_date.year) * 12 + \
                calculation_date.month - self.origination_date.month
            if months_from_origination < self.interest_only_period:
                return self._calculate_interest(self.original_balance, calculation_date, calculation_date + relativedelta(months=1))
            else:
                return self.monthly_payment
        else:
            return 0

    def get_current_balance(self, as_of_date: pd.Timestamp) -> float:
        self.get_schedule()
        closest_entry = None
        for entry in self.schedule:
            entry_date = pd.Timestamp(entry['date'])
            if entry_date <= as_of_date:
                closest_entry = entry
            else:
                break
    
        # If the as_of_date is past the maturity date, return the last entry's balance
        if as_of_date > pd.Timestamp(self.schedule[-1]['date']):
            return 0
        
        # If no entry is found before the as_of_date, return 0
        if closest_entry is None:
            return 0
    
        return closest_entry['Ending Balance']

    def get_payoff_amount(self, payoff_date: pd.Timestamp) -> float:
        current_balance = self.get_current_balance(payoff_date)
        return current_balance

    def get_payment_info(self, payment_date: pd.Timestamp) -> Dict[str, float]:
        if payment_date < self.origination_date or payment_date > self.maturity_date:
            return {
                'interest': 0,
                'principal': 0,
                'total_payment': 0,
                'remaining_balance': self.get_current_balance(payment_date)
            }

        # Find the closest date in the schedule that is less than or equal to the payment_date
        closest_date = max(pd.Timestamp(
            d['date']) for d in self.schedule if pd.Timestamp(d['date']) <= payment_date)
        schedule_entry = next(entry for entry in self.schedule if pd.Timestamp(
            entry['date']) == closest_date)

        interest = schedule_entry['Interest Expense']
        principal = schedule_entry['Principal Payments']
        total_payment = schedule_entry['Total Payment']
        remaining_balance = schedule_entry['Ending Balance']

        return {
            'interest': interest,
            'principal': principal,
            'total_payment': total_payment,
            'remaining_balance': remaining_balance
        }

    def __str__(self):
        return (f"Loan {self.loan_id}: ${self.original_balance:,.2f} at {self.note_rate*100:.2f}% "
                f"maturing on {self.maturity_date}, using {self.day_count_method} day count, "
                f"with {self.interest_only_period} months interest-only")

