![Sharesies NZ](https://images.squarespace-cdn.com/content/58bc788c59cc68b9696b9ee0/1543372882154-5E6PGXVJGOIQU30NTJKJ/sharesies.png?content-type=image%2Fpng)

Unoffical Python API for Sharesies NZ

# Documentation

## Installing
``pip install git+ssh://git@github.com/jontymorris/Sharesies-API.git``

## Logging in
```python
import sharesies

client = sharesies.Client()

if client.login('you@example.com', 'password123'):
  print('Login succeeded')
else:
  print('Login failed')
```

## Profile information
```python
profile = client.get_profile()

user_id = profile['user']['id']
portfolio = profile['portfolio']
```

## Buying shares
```python
companies = client.get_companies()

if client.buy(companies[0], 10):
  print('Bought $10 worth of shares')
else:
  print('Something went wrong')
```

## Selling shares
```python
companies = client.get_companies()

if client.sell(companies[0], 1):
  print('Sold 1 share')
else:
  print('Something went wrong')
```

## Historic price data
```python
companies = client.get_companies()

client.get_price_history(companies[0])
{
    "2014-06-25": "1.110000",
    "2014-06-30": "1.050000",
    "2014-07-07": "1.050000",
    "2014-07-10": "1.100000",
    ...
}
```

## Your order history
```python
# get your portfolio
profile = client.get_profile()
portfolio = profile['portfolio']

# loop through your portfolio
for item in portfolio:
  fund_id = item['fund_id']
  order_history = client.get_order_history(fund_id)
  
  '''
  each item has:
    type: buy/sell
    contribution: amount buy/sold
    order_unit_price: price at time
    created: Unix timestamp
  '''
```

<hr>

## Development

To setup a development environment you can install the package in [development mode](https://packaging.python.org/tutorials/installing-packages/#installing-from-vcs).

```bash
git clone https://github.com/jontymorris/Sharesies-API.git
cd Sharesies-API
python3 -m pip install -e .
```
