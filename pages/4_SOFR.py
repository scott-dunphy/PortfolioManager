from chatham import Chatham
import streamlit as st
import pandas as pd

# Initialize Chatham and get monthly rates
chatham = Chatham()
rates = chatham.get_monthly_rates()

# Convert the rates dictionary to a DataFrame
rates_df = pd.DataFrame(list(rates.items()), columns=['Date', 'Rate'])

# Convert the Date column to datetime format
rates_df['Date'] = pd.to_datetime(rates_df['Date'])

# Set the Date column as the index
rates_df.set_index('Date', inplace=True)

# Display the rates DataFrame
#st.write(rates_df)

# Plot the rates in a line chart
st.title("SOFR Forward Curve (Source: Chatham Financial)")
st.line_chart(rates_df)
