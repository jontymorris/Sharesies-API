import requests
from sharesies.util import PropagatingThread
from queue import Queue


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

        resp = self.session.post(
            'https://app.sharesies.nz/api/identity/login',
            json=login_form
        )

        r = resp.json()

        if r['authenticated']:
            self.user_id = r['user_list'][0]['id']
            self.password = password  # Used for reauth
            self.auth_token = r['distill_token']
            self.session_cookie = resp.cookies['session']
            return True

        return False
    
    def logout(self):
        '''
        Clears the login session data
        '''

        self.user_id = None
        self.password = None
        self.auth_token = None
        self.session_cookie = None

    def get_transactions(self, since=0):
        '''
        Get all transactions in wallet since a certain transaction_id
        (0 is all-time)
        '''

        transactions = []

        cookies = {
            'session': self.session_cookie
        }

        params = {
            'limit': 50,
            'acting_as_id': self.user_id,
            'since': since
        }

        has_more = True
        while has_more:
            r = self.session.get(
                "https://app.sharesies.nz/api/accounting/transaction-history",
                params=params, cookies=cookies)
            responce = r.json()
            transactions.extend(responce['transactions'])
            has_more = responce['has_more']
            params['before'] = transactions[-1]['transaction_id']

        return transactions

    def get_shares(self, managed_funds=False):
        '''
        Get all shares listed on Sharesies
        '''

        shares = []

        page = self.get_instruments(1, managed_funds)
        number_of_pages = page['numberOfPages']
        shares += page['instruments']

        threads = []
        que = Queue()

        # make threads
        for i in range(2, number_of_pages):
            threads.append(PropagatingThread(
                target=lambda q,
                arg1: q.put(self.get_instruments(arg1, managed_funds)),
                args=(que, i)))

        # start threads
        for thread in threads:
            thread.start()

        # join threads
        for thread in threads:
            thread.join()

        while not que.empty():
            shares += que.get()['instruments']

        return shares

    def get_instruments(self, page, managed_funds=False):
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

        if managed_funds:
            params['instrumentTypes'] = ['mf']

        r = self.session.get("https://data.sharesies.nz/api/v1/instruments",
                             params=params, headers=headers)
        responce = r.json()

        # get dividends and price history
        for i in range(len(responce['instruments'])):
            current = responce['instruments'][i]
            id_ = current['id']
            # current['dividends'] = self.get_dividends(id_)
            current['priceHistory'] = self.get_price_history(id_)

        return responce

    def get_dividends(self, share_id):
        '''
        Get certain stocks dividends
        '''

        headers = self.session.headers
        headers['Authorization'] = f'Bearer {self.auth_token}'

        r = self.session.get(
            "https://data.sharesies.nz/api/v1/instruments/"
            f"{share_id}/dividends")

        # TODO: Clean up output
        return r.json()['dividends']

    def get_price_history(self, share_id):
        '''
        Get certain stocks price history
        '''

        headers = self.session.headers
        headers['Authorization'] = f'Bearer {self.auth_token}'

        r = self.session.get(
            "https://data.sharesies.nz/api/v1/instruments/"
            f"{share_id}/pricehistory")

        return r.json()['dayPrices']

    def get_companies(self):
        '''
        Returns all companies accessible through Sharesies
        '''

        r = self.session.get(
            'https://app.sharesies.nz/api/fund/list'
        )

        funds = r.json()['funds']

        return [fund for fund in funds if fund['fund_type'] == 'company']

    def get_info(self):
        '''
        Get basic market info
        '''
        headers = self.session.headers
        headers['Authorization'] = f'Bearer {self.auth_token}'

        r = self.session.get(
            "https://data.sharesies.nz/api/v1/instruments/info")
        return r.text

    def get_profile(self):
        '''
        Returns the logged in users profile
        '''

        r = self.session.get(
            'https://app.sharesies.nz/api/identity/check'
        )

        return r.json()

    def get_order_history(self, fund_id):
        '''
        Returns your order history for a given fund.
        '''

        self.reauth()  # Avoid timeout

        r = self.session.get(
            'https://app.sharesies.nz/api/accounting/order-history-v4' +
            '?fund_id=' + fund_id + '&acting_as_id=' + self.user_id
        )

        return r.json()['orders']

    def buy(self, company, amount):
        '''
        Purchase stocks from the NZX Market
        '''

        self.reauth()  # avoid timeout

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

        self.reauth()  # Avoid timeout

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
