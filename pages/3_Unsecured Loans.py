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


origination_date = st.date_input('Origination Date')
maturity_date = st.date_input('Maturity Date')
original_balance = st.number_input('Original Balance')
note_rate = st.number_input('Note Rate (%)', min_value=0.0)
interest_only_period = st.number_input('Interest Only Period (months)')
amortization_period = st.number_input('Amortization Period (months)')
day_count_method = st.selectbox('Day Count Method', options=["Actual/360", "Actual/365", "30/360"])

