import requests

url = 'http://127.0.0.1:8000/miner_performance'
response = requests.get(url)
print(response.status_code)
print('prediction', response.json())
