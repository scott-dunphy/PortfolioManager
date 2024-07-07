import requests
from datetime import datetime, timedelta
import streamlit as st

class Chatham:
    def __init__(self):
        self.url = "https://www.chathamfinancial.com/getrates/285116"
        self.curve_date = None
        self.rates = {}

    @st.cache_data(ttl=3600)  # Cache the data for an hour
    def get_curve(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            self.curve_date = datetime.strptime(data["CurveDate"], "%Y-%m-%dT%H:%M:%S")
            self.rates = {datetime.strptime(rate["Date"], "%Y-%m-%dT%H:%M:%S"): rate["Rate"] for rate in data["Rates"]}
            return self.curve_date, self.rates
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
        if not self.rates:
            self.curve_date, self.rates = self.get_curve()
        while date not in self.rates:
            date += timedelta(days=1)
        return self.rates.get(date)

    def get_rates(self):
        if not self.rates:
            self.curve_date, self.rates = self.get_curve()
        return self.rates

    def get_monthly_rates(self):
        if not self.rates:
            self.curve_date, self.rates = self.get_curve()
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

    def plot_rates_ascii(self, rates):
        dates = sorted(rates.keys())
        rate_values = [rates[date] for date in dates]

        min_rate = min(rate_values)
        max_rate = max(rate_values)
        rate_range = max_rate - min_rate
        width = 50
        height = 20

        def get_y(rate):
            return int((rate - min_rate) / rate_range * height)

        plot = [[' ' for _ in range(width)] for _ in range(height + 1)]

        for i, rate in enumerate(rate_values):
            y = get_y(rate)
            x = int(i / len(rate_values) * width)
            plot[y][x] = '*'

        for y in reversed(range(height + 1)):
            print(''.join(plot[y]))
        print(f"Min Rate: {min_rate:.4f}, Max Rate: {max_rate:.4f}")
