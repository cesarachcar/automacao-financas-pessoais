import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import sheet_id
import locale

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)
SHEET_ID = sheet_id
sheet = CLIENT.open_by_key(SHEET_ID)


locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
mes = datetime.now().strftime('%B').capitalize()
worksheet = sheet.worksheet(mes)

dados = worksheet.get("K29:K113")
print(dados)
print(len(dados))
linha_update = 29 + len(dados)
valor = 5
worksheet.update_acell(f'K{linha_update}', valor)
print(f"Atualizado K{linha_update} com o valor {valor}.")

def update_sheets(valor: float, data: str, sheet_id: str = SHEET_ID):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    CLIENT = gspread.authorize(CREDS)
    sheet = CLIENT.open_by_key(SHEET_ID)

    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    mes = datetime.now().strftime('%B').capitalize()
    worksheet = sheet.worksheet(mes)

    dados_gastos = worksheet.get("K29:K113")
    linha_update = 29 + len(dados_gastos)
    worksheet.update_acell(f'K{linha_update}', valor)
    worksheet.update_acell(f'M{linha_update}', data)
    


# linha_relativa = None
# for i, (k,) in enumerate(dados):
#     print (k)
#     if k == '':
#         linha_relativa = i + 1 # i começa em 0
#         print('knone')
#         break

# if linha_relativa is None:
#     print("Não há mais linhas vazias no intervalo K29:L113.")
# else:
# linha_update = 29 + (linha_relativa - 1)
# worksheet.update_acell(f'K{linha_update}', 5)
# print(f"Atualizado K{linha_update} com o valor 5.")

# print(f'valor k30: {worksheet.acell('K30').value}')