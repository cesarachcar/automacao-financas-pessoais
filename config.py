import os
from dotenv import load_dotenv

load_dotenv()


item_id_nu = os.getenv("ITEM_ID_NU")
item_id_meu_pluggy = os.getenv("ITEM_ID_MEU_PLUGGY")
account_id_bank = os.getenv("ACCOUNT_ID_BANK")
account_id_credit = os.getenv("ACCOUNT_ID_CREDIT")
sheet_id = os.getenv("SHEET_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")