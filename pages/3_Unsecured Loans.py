from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict
import pandas as pd
import streamlit as st
from config import adjusted_column_config

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict
import uuid
import pandas as pd
import json
from loan import Loan
from property import Property


st.write("Unsecured Loan Inputs")
origination_date = pd.to_datetime(st.date_input('Origination Date'))
maturity_date = pd.to_datetime(st.date_input('Maturity Date'))
original_balance = st.number_input('Original Balance')
note_rate = st.number_input('Note Rate (%)', min_value=0.0)
spread = st.number_input('Floating Rate Spread (%)', min_value=0.0)
fixed_floating = st.selectbox('Fixed/Floating', options=["Fixed", "Floating"])
interest_only_period = st.number_input('Interest Only Period (months)')
amortization_period = st.number_input('Amortization Period (months)')
day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"])

loan = Loan(
  origination_date = origination_date,
  maturity_date = maturity_date,
  original_balance = original_balance,
  note_rate = note_rate,
  interest_only_period = interest_only_period,
  amortization_period = amortization_period,
  day_count_method = day_count_method,
  loan_id = 'U01',
  fixed_floating = fixed_floating,
  spread = spread
)

st.dataframe(loan.get_unsecured_schedule())



