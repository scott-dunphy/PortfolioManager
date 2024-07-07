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

col1 = st.columns(1)

with col1:
    origination_date = st.date_input('Origination Date', value=selected_property.loan.origination_date if selected_property.loan else date.today())
    maturity_date = st.date_input('Maturity Date', value=selected_property.loan.maturity_date if selected_property.loan else date.today())
    original_balance = st.number_input('Original Balance', min_value=0.0, value=float(selected_property.loan.original_balance) if selected_property.loan else 0.0, format='%f')
    note_rate = st.number_input('Note Rate (%)', min_value=0.0, value=float(selected_property.loan.note_rate * 100) if selected_property.loan else 0.0, format='%f')
    interest_only_period = st.number_input('Interest Only Period (months)', min_value=0, value=int(selected_property.loan.interest_only_period) if selected_property.loan else 0)
    amortization_period = st.number_input('Amortization Period (months)', min_value=0, value=int(selected_property.loan.amortization_period) if selected_property.loan else 0)
    day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"], index=["Actual/360", "Actual/365", "30/360"].index(selected_property.loan.day_count_method) if selected_property.loan else 0)

