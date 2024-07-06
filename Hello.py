import streamlit as st
from datetime import date, datetime
from portfolio import Portfolio
import pandas as pd

st.set_page_config(
    page_title="CRE Portfolio Manager",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a demo above.")

properties = st.session_state.properties

portfolio = Portfolio(
    name = 'Dunphy Property Fund',
    start_date = datetime(2023,1,1),
    end_date = datetime(2025,1,1),
    properties = properties
)

cash_flows = portfolio.aggregate_hold_period_cash_flows()

st.table(cash_flows)


