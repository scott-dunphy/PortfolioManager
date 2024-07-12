import pandas as pd
import streamlit as st
from portfolio import Portfolio

class Portfolioviz:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def plot_loan_balance_distribution(self):
        """Plots the distribution of loan balances in the portfolio."""
        loan_balances = [loan.original_balance for loan in self.portfolio.unsecured_loans]
        chart_data = pd.DataFrame(loan_balances, columns=['Loan Balance'])
        st.bar_chart(chart_data)

    def plot_interest_rate_distribution(self):
        """Plots the distribution of interest rates in the portfolio."""
        interest_rates = [loan.note_rate for loan in self.portfolio.unsecured_loans]
        chart_data = pd.DataFrame(interest_rates, columns=['Interest Rate'])
        st.bar_chart(chart_data)

    def plot_loan_balance_over_time(self):
        """Plots the loan balances over time."""
        data = []
        for loan in self.portfolio.unsecured_loans:
            schedule = loan.get_unsecured_schedule()
            for entry in schedule:
                date = entry['date']
                balance = balance + entry['Adjusted Loan Proceeds'] + entry['Adjusted Principal Payments']
                data.append({'date': date, 'balance': balance, 'loan_id': loan.loan_id})

        if not data:
            st.error("No data available to plot.")
            return

        df = pd.DataFrame(data)
        st.write("DataFrame created from schedule data:")
        st.write(df)

        if 'date' not in df.columns:
            st.error("Date column is missing in the DataFrame.")
            return

        df['date'] = pd.to_datetime(df['date'])
        df = df.groupby('date')['balance'].sum().reset_index()

        st.line_chart(df.set_index('date'))

    def plot_property_type_distribution(self):
        """Plots the distribution of properties by type as a bar chart based on current value."""
        try:
            data = [(property_.property_type, property_.current_value) for property_ in self.portfolio.properties]
            df = pd.DataFrame(data, columns=['property_type', 'current_value'])
            property_type_values = df.groupby('property_type')['current_value'].sum().reset_index()

            st.bar_chart(property_type_values.set_index('property_type'))
        except AttributeError as e:
            st.error(f"Error accessing property attributes: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
