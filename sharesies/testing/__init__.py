import os.path
import requests
import pickle
import sharesies


class Stock:
    '''
    Fake stock wrapper for pretend
    buy and sell to see real profits
    '''
    def __init__(self, company_id, amount):
        self.company = company_id
        self.amount = amount
        self.fee = amount*0.005

        # Stock value on purchase
        self.starting_value = self.get_price()

        # Sale profit
        self.profit = 0

    def sell(self):
        '''
        Calculate profit/loss from trade
        '''

        price_now = self.get_price()
        self.profit = (price_now - self.starting_value) - self.fee

    def get_price(self):
        '''
        Grab price of stock at moment in time
        '''

        r = requests.get('https://app.sharesies.nz/api/fund/list')
        funds = r.json()['funds']
        for fund in funds:
            if fund['name'] == self.company:
                return float(fund['market_price'])

        return None


class Backtest(sharesies.Client):
    '''
    Clone of the Sharesies class
    except without making any purchases
    or sales on the account. This is
    purely for strategy testing
    '''

    def __init__(self, wallet_ballence=1000):
        super().__init__()  # Execute Sharesies init

        self.wallet_ballence = wallet_ballence

        self.current_stocks = []
        self.sold_stocks = []

    def login(self, email, password):
        '''
        Login if profile not cached
        '''

        # Cookies saved
        if self.is_login_cached():
            with open('cookie_cache.pk', 'rb') as f:
                self.session.cookies.update(pickle.load(f))

            return True

        # Login and save cookies
        else:

            logged_in = super().login(
                email, password
            )

            if logged_in:
                with open('cookie_cache.pk', 'wb') as f:
                    cookies = self.session.cookies
                    pickle.dump(cookies, f)

            return logged_in

    def sell(self, company, shares):
        '''
        Pretend to sell stocks
        '''

        # Find stock
        found_stock = None
        for i in range(len(self.current_stocks)):
            if self.current_stocks[i].company == company['name']:
                found_stock = i
                break

        # Sell stock
        if found_stock is not None:
            self.current_stocks[found_stock].sell()
            self.wallet_ballence += self.current_stocks[found_stock].profit

            self.sold_stocks.append(
                self.current_stocks[found_stock]
            )

            self.current_stocks.pop(found_stock)

            return True

        # Stock wasn't found
        else:
            print("[!] Tried to sell stock that didn't exist!")
            return False

    def buy(self, company, amount):
        '''
        Pretend to buy stocks
        '''

        purchased_stock = Stock(
            company['name'],
            amount
        )

        self.current_stocks.append(purchased_stock)
        self.wallet_ballence -= amount

        return True

    def get_profile(self):
        '''
        Returns modified profile data
        '''

        profile_data = super().get_profile()

        # Manipulate data...
        profile_data['user']['wallet_ballence'] = self.wallet_ballence

        return profile_data

    def is_login_cached(self):
        '''
        Checks if cookie cache exists
        '''

        return os.path.exists('cookie_cache.pk')
