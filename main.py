from xml_to_sheet import do_xml_setup, run_xml_stuff
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
##Google Sheets stuff

# Load secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)
    
# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Scopes required for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

RANGE_NAME = secrets["xml_to_sheet_range_name"]

# Authenticate with the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

##End of Google Sheets stuff

do_xml_setup(secrets)
run_xml_stuff()
