import matplotlib.pyplot as plt
import pandas as pd
from portfolio import Portfolio

class Portfolioviz:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def plot_loan_balance_distribution(self):
        """Plots the distribution of loan balances in the portfolio."""
        loan_balances = [loan.original_balance for loan in self.portfolio.unsecured_loans]
        plt.figure(figsize=(10, 6))
        plt.hist(loan_balances, bins=20, edgecolor='k', alpha=0.7)
        plt.title('Distribution of Loan Balances')
        plt.xlabel('Loan Balance')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.show()

    def plot_interest_rate_distribution(self):
        """Plots the distribution of interest rates in the portfolio."""
        interest_rates = [loan.note_rate for loan in self.portfolio.unsecured_loans]
        plt.figure(figsize=(10, 6))
        plt.hist(interest_rates, bins=20, edgecolor='k', alpha=0.7)
        plt.title('Distribution of Interest Rates')
        plt.xlabel('Interest Rate (%)')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.show()

    def plot_loan_balance_over_time(self):
        """Plots the loan balances over time."""
        data = []
        for loan in self.portfolio.unsecured_loans:
            schedule = loan.get_unsecured_schedule()
            for date, balance in schedule.items():
                data.append({'date': date, 'balance': balance, 'loan_id': loan.loan_id})

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.groupby('date')['balance'].sum().reset_index()

        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['balance'], marker='o')
        plt.title('Loan Balances Over Time')
        plt.xlabel('Date')
        plt.ylabel('Total Loan Balance')
        plt.grid(True)
        plt.show()

    def plot_property_type_distribution(self):
        """Plots the distribution of properties by type."""
        property_types = [property_.property_type for property_ in self.portfolio.properties]
        plt.figure(figsize=(10, 6))
        plt.hist(property_types, bins=len(set(property_types)), edgecolor='k', alpha=0.7)
        plt.title('Distribution of Property Types')
        plt.xlabel('Property Type')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.show()

# Usage example:
# portfolio = Portfolio()
# viz = Portfolioviz(portfolio)
# viz.plot_loan_balance_distribution()
# viz.plot_interest_rate_distribution()
# viz.plot_loan_balance_over_time()
# viz.plot_property_type_distribution()
