from chatham import Chatham

chatham = Chatham()
rates = chatham.get_curve()

st.write(rates)
