import requests
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

class Chatham:
    def __init__(self):
        self.url = "https://www.chathamfinancial.com/getrates/285116"
        self.curve_date = None
        self.rates = {}

    def fetch_data(self):
        """Fetches data from the given URL and updates the curve_date and rates."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.chathamfinancial.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            self.curve_date = datetime.strptime(data["CurveDate"], "%Y-%m-%d")
            self.rates = {datetime.strptime(rate["Date"], "%Y-%m-%d"): rate["Rate"] for rate in data["Rates"]}
        except requests.exceptions.RequestException as e:
            st.error(f"Request error: {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP error: {e}")
        except requests.exceptions.JSONDecodeError as e:
            st.error(f"JSON decode error: {e}")
        except KeyError as e:
            st.error(f"Key error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    def get_rate(self, date):
        """Gets the rate for a specific date. If the date is not found, it finds the closest next date."""
        if not self.rates:
            self.fetch_data()
        while date not in self.rates and date <= datetime.today():
            date += timedelta(days=1)
        return self.rates.get(date, None)

    def get_all_rates(self):
        """Returns all rates after fetching data if not already done."""
        if not self.rates:
            self.fetch_data()
        return self.rates

    def get_monthly_rates(self):
        """Returns rates for the first available date of each month."""
        if not self.rates:
            self.fetch_data()
        monthly_rates = {}
        sorted_dates = sorted(self.rates.keys())
        current_month = sorted_dates[0].month
        current_year = sorted_dates[0].year

        for date in sorted_dates:
            if date.month != current_month or date.year != current_year:
                monthly_rates[datetime(current_year, current_month, 1)] = self.rates[date]
                current_month = date.month
                current_year = date.year
        return monthly_rates
