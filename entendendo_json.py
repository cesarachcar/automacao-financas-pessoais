import requests
import json
from google.oauth2.service_account import Credentials
from datetime import date, datetime
from config import client_id, client_secret, item_id_meu_pluggy

BASE_URL = 'https://api.pluggy.ai'

def get_api_key() -> str:
    payload = {
        'clientId': client_id,
        'clientSecret': client_secret
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    response = requests.post(f'{BASE_URL}/auth', json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['apiKey']

def get_account_id(api_key: str, item_id: str):
    headers = {'X-API-KEY': api_key}
    params = {'itemId': item_id}
    response = requests.get(f'{BASE_URL}/accounts', headers=headers, params=params)
    account_id = response.json()['results'][0]['id']
    return account_id

def get_transactions(api_key: str, account_id: str, from_date: date | None = None, to_date: date | None = None):
    headers = {'X-API-KEY': api_key}
    params = {'accountId': account_id}

    if from_date:
        params['from'] = from_date.isoformat()
    if to_date:
        params['to'] = to_date.isoformat()

    response = requests.get(f'{BASE_URL}/transactions', headers=headers, params=params)
    response.raise_for_status()
    return response.json()

api_key = get_api_key()
account_id = get_account_id(api_key, item_id_meu_pluggy)

from_date = datetime.strptime('09/12/2025', '%d/%m/%Y').date() # formato brasileiro
to_date = datetime.strptime('10/12/2025', '%d/%m/%Y').date() # formato brasileiro

transactions_response = get_transactions(api_key, account_id, from_date, to_date)

with open('entendendo_json.json', 'w', encoding='utf-8') as arquivo:
    json.dump(transactions_response, arquivo, indent=4, ensure_ascii=False)