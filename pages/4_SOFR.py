from chatham import Chatham
import streamlit as st
import pandas as pd

# Initialize Chatham and get monthly rates
chatham = Chatham()
rates = chatham.get_monthly_rates()

# Convert the rates to a DataFrame if it's not already one
if not isinstance(rates, pd.DataFrame):
    rates = pd.DataFrame(rates)

# Plot the rates in a line chart
st.line_chart(rates)
