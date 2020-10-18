import requests
from datetime import date


class Client:

    def __init__(self):
        # session to remain logged in
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 Firefox/71.0",
            "Accept": "*/*",
            "content-type": "application/json",
        }

        self.user_id = ""
        self.password = ""
        self.auth_token = ""

    def login(self, email, password):
        '''
        You must login first to access certain features
        '''

        login_form = {
            'email': email,
            'password': password,
            'remember': True
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/identity/login',
            json=login_form
        ).json()

        if r['authenticated']:
            self.user_id = r['user_list'][0]['id']
            self.password = password # Used for reauth
            self.auth_token = r['distill_token']
            return True
        
        return False

    def get_shares(self):
        '''
        Get all shares listed on Sharesies
        '''

        shares = []
        current_page = 1

        while True:
            page = self.get_instruments(current_page)
            shares += page['instruments']

            if current_page >= page['numberOfPages']:
                break

            current_page += 1

        return shares

    def get_instruments(self, page):
        '''
        Get a certain page of shares
        '''
        headers = self.session.headers
        headers['Authorization'] = f'Bearer {self.auth_token}'

        params = {
            'Page': page,
            'Sort': 'marketCap',
            'PriceChangeTime': '1y',
            'Query': ''
        }

        r = self.session.get("https://data.sharesies.nz/api/v1/instruments",
                             params=params, headers=headers)
        return r.json()

    def get_info(self):
        '''
        Get basic market info
        '''
        headers = self.session.headers
        headers['Authorization'] = f'Bearer {self.auth_token}'

        r = self.session.get("https://data.sharesies.nz/api/v1/instruments/info")
        return r.text

    def get_profile(self):
        '''
        Returns the logged in users profile
        '''

        r = self.session.get(
            'https://app.sharesies.nz/api/identity/check'
        )

        return r.json()

    def get_price_history(self, company):
        '''
        Returns daily price history for a company
        '''

        today = date.today()

        r = self.session.get(
            'https://app.sharesies.nz/api/fund/price-history?'
            'fund_id={}&first={}&last={}'.format(
                company['id'], '2000-01-01', today.strftime("%Y-%m-%d")
            )
        )

        return r.json()['day_prices']

    def buy(self, company, amount):
        '''
        Purchase stocks from the NZX Market
        '''

        self.reauth() # avoid timeout

        buy_info = {
            'action': 'place',
            'amount': amount,
            'fund_id': company['id'],
            'expected_fee': amount*0.005,
            'acting_as_id': self.user_id
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/cart/immediate-buy-v2',
            json=buy_info
        )

        return r.status_code == 200

    def sell(self, company, shares):
        '''
        Sell shares from the NZX Market
        '''

        self.reauth() # Avoid timeout

        sell_info = {
            'shares': shares,
            'fund_id': company['fund_id'],
            'acting_as_id': self.user_id,
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/fund/sell',
            json=sell_info
        )

        return r.status_code == 200

    def reauth(self):
        '''
        Reauthenticates user on server
        '''

        creds = {
            "password": self.password,
            "acting_as_id": self.user_id
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/identity/reauthenticate',
            json=creds
        )

        return r.status_code == 200
        