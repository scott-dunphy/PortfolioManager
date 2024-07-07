from chatham import Chatham
import streamlit as st

chatham = Chatham()
rates = chatham.get_curve()

st.write(rates)
