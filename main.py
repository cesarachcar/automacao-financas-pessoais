import requests
import gspread
import locale
from collections import deque
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from config import client_id, client_secret, item_id_meu_pluggy, sheet_id
import logging
import sys

# --- Logging Config ---
logging.basicConfig(level=logging.INFO, filename=f"{__file__}.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

BASE_URL = 'https://api.pluggy.ai'
SHEET_ID = sheet_id # 2026

with open('main.py.log', 'r') as f:
    ultima_linha_log = deque(f, maxlen=1)[0]
    ultimo_timestamp = ultima_linha_log.split("Processado em: ")[1].strip()
    ultimo_timestamp = datetime.fromisoformat(ultimo_timestamp)

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

def put_label(description):
    '''Categoriza tipo de gasto se for reconhecido'''
    label = None
    if '99' in description or 'uber' in description.lower():
        label = '🚗 Uber/99/inDrive'
    if 'UNIVERSIDADE DE SAO PAULO' in description:
        label = '🍗 Alimentação'
    if 'ifood' in description.lower():
        label = '🍔 Restaurante'
    if 'grick' in description.lower():
        label = '🧺 Mercado'
    return label

def put_payment_method(description, operationType):
    '''Categoriza a forma de pagamento. Obs: não confundir com tipo de transação (creditada ou debitada)'''
    payment_method = None
    if 'crédito' in description:
        payment_method = 'Crédito'
    if 'débito' in description:
        payment_method = 'Débito'
    if 'PIX' in operationType:
        payment_method = 'Pix / Dinheiro'
    return payment_method

def update_sheets(valor: float, data: date, label: str, payment_method: str, sheet_id: str = SHEET_ID):
    '''Atualiza a planilha com os valores capturados'''
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    CLIENT = gspread.authorize(CREDS)
    sheet = CLIENT.open_by_key(sheet_id)

    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    mes = data.strftime('%B').capitalize()
    worksheet = sheet.worksheet(mes)

    if valor < 0: # entra em gastos
        valor = abs(valor)
        data = data.strftime("%d/%m/%Y") #formata r["date"] de iso para br (dd/mm/yyyy)
        dados_gastos = worksheet.get("K29:K113")
        linha_update = 29 + len(dados_gastos) if len(dados_gastos[0]) != 0 else 29
        worksheet.update_acell(f'K{linha_update}', valor)
        worksheet.update_acell(f'M{linha_update}', data)
        worksheet.update_acell(f'H{linha_update}', label)
        worksheet.update_acell(f'I{linha_update}', payment_method)
    else:
        dados_entradas = worksheet.get("E29:E113")
        linha_update = 29 + len(dados_entradas) if len(dados_entradas[0]) != 0 else 29
        worksheet.update_acell(f'E{linha_update}', valor)

def main():
    api_key = get_api_key()
    account_id = get_account_id(api_key, item_id_meu_pluggy)

    from_date = ultimo_timestamp
    to_date = datetime.now()
    #from_date = datetime.strptime('01/12/2025', '%d/%m/%Y').date() # formato brasileiro
    #to_date = datetime.strptime('01/12/2025', '%d/%m/%Y').date() # formato brasileiro
    transactions_response = get_transactions(api_key, account_id, from_date, to_date)
    results = transactions_response["results"]
    for r in reversed(results): # reversed para ler json dos mais antigos para os mais recentes
        valor = r["amount"]
        data = r["date"]
        data = datetime.fromisoformat(data[:-1])
        data_brasil = data - timedelta(hours=3)
        label = put_label(r["description"])
        payment_method = put_payment_method(r["description"], r["operationType"])
        update_sheets(valor, data_brasil, label, payment_method)



if __name__ == "__main__":
    try:
        main()
        logging.info(f'Processado em: {datetime.now()}')
    except Exception as e:
        logging.error(f'Ocorreu um erro durante a execução: {e}')