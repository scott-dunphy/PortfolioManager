from chatham import Chatham
import streamlit as st

chatham = Chatham()
rates = chatham.get_monthly_rates()

st.write(rates)
