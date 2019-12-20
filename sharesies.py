import requests


class Sharesies:

    def __init__(self):
        # session to remain logged in
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 Firefox/71.0",
            "Accept": "*/*",
            "content-type": "application/json",
        }

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
        )

        return r.json()['authenticated']

    def get_profile(self):
        '''
        Returns the logged in users profile
        '''

        r = self.session.get(
            'https://app.sharesies.nz/api/identity/check'
        )

        return r.json()

    def get_companies(self):
        '''
        Returns all companies accessible through Sharesies
        '''

        r = self.session.get(
            'https://app.sharesies.nz/api/fund/list'
        )

        funds = r.json()['funds']

        return [fund for fund in funds if fund['fund_type'] == 'company']

    def buy(self, user, company, amount):
        '''
        Purchase stocks from the NZX Market
        '''

        buy_info = {
            'acting_as_id': user,
            'action': 'place',
            'amount': amount,
            'expected_fee': amount*0.005,
            'fund_id': company['id']
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/cart/immediate-buy-v2',
            json=buy_info
        )

        return r.status_code == 200

    def sell(self, user, company, shares):
        '''
        Sell shares from the NZX Market
        '''

        sell_info = {
            'acting_as_id': user,
            'fund_id': company['id'],
            'shares': shares
        }

        r = self.session.post(
            'https://app.sharesies.nz/api/fund/sell',
            json=sell_info
        )

        return r.status_code == 200
