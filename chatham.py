import requests
from datetime import datetime, timedelta
import pandas as pd

class Chatham:
    def __init__(self):
        self.url = "https://www.chathamfinancial.com/getrates/285116"
        self.curve_date = None
        self.get_curve()

    def get_curve(self):
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
            self.curve_date = datetime.strptime(data["CurveDate"], "%Y-%m-%dT%H:%M:%S")
            self.rates = {pd.to_datetime(rate["Date"]): rate["Rate"] for rate in data["Rates"]}
            return data
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except KeyError as e:
            print(f"Key error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_rate(self, date):
        if not self.rates:
            self.get_curve()
        while date not in self.rates:
            date += timedelta(days=1)
        return self.rates.get(date)


    def get_rates(self):
        if not self.rates:
            self.get_curve()
        return self.rates

    def get_monthly_rates(self):
        
        if not self.rates:
            self.get_curve()
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
