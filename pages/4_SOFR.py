from chatham import Chatham
import streamlit as st

chatham = Chatham()
rates = chatham.rates

st.write(rates)
