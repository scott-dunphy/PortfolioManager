import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
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
        st.pyplot(plt)

    def plot_interest_rate_distribution(self):
        """Plots the distribution of interest rates in the portfolio."""
        interest_rates = [loan.note_rate for loan in self.portfolio.unsecured_loans]
        plt.figure(figsize=(10, 6))
        plt.hist(interest_rates, bins=20, edgecolor='k', alpha=0.7)
        plt.title('Distribution of Interest Rates')
        plt.xlabel('Interest Rate (%)')
        plt.ylabel('Frequency')
        plt.grid(True)
        st.pyplot(plt)

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
        st.pyplot(plt)

    def plot_property_type_distribution(self):
        """Plots the distribution of properties by type as a donut chart."""
        try:
            property_types = [property_.property_type for property_ in self.portfolio.properties]
            property_type_counts = pd.Series(property_types).value_counts()

            plt.figure(figsize=(10, 6))
            plt.pie(property_type_counts, labels=property_type_counts.index, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.3))
            plt.title('Distribution of Property Types')
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(plt)
        except AttributeError as e:
            st.error(f"Error accessing property type: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Usage example:
# portfolio = Portfolio()
# viz = Portfolioviz(portfolio)
# viz.plot_loan_balance_distribution()
# viz.plot_interest_rate_distribution()
# viz.plot_loan_balance_over_time()
# viz.plot_property_type_distribution()
