from chatham import Chatham

chatham = Chatham()
rates = chatham.get_monthly_rates()

st.write(len(rates))
