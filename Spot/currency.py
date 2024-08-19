import requests


class CurrencyApi:
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparking': False,
    }

    def get_all_currencies(self):
        response = requests.get(self.url, params=self.params)
        if response.status_code == 200:
            print(response)
            return response.json()
        else:
            raise Exception("Error getting all currencies")

    def get_currency(self, symbol):
        currencies = self.get_all_currencies()
        for currency in currencies:
            if currency['symbol'] == symbol:
                return currency
        return None
