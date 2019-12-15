![Sharesies NZ](https://images.squarespace-cdn.com/content/58bc788c59cc68b9696b9ee0/1543372882154-5E6PGXVJGOIQU30NTJKJ/sharesies.png?content-type=image%2Fpng)

Unoffical Python API for Sharesies NZ

# Documentation

## Logging in
```python
import sharesies


s = sharesies.Sharesies()

if s.login('you@example.com', 'password123'):
  print('Login succeeded')
else:
  print('Login failed')
```

## Profile information
```python
profile = s.get_profile()

user_id = profile['user']['id']
portfolio = profile['portfolio']
```

## Buying shares
```python
companies = s.get_companies()

if s.buy(user_id, companies[0], 10):
  print('Bought $10 worth of shares')
else:
  print('Something went wrong')
```

## Selling shares
```python
companies = s.get_companies()

if s.sell(user_id, companies[0], 1):
  print('Sold 1 share')
else:
  print('Something went wrong')
```
