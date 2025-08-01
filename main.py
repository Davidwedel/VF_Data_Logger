import argparse
from xml_processing import do_xml_setup, run_xml_stuff, deleteOldFiles
from sheets_processing import read_from_sheet, write_to_sheet
from unitas_processing import do_unitas_setup, run_unitas_stuff
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
##Google Sheets stuff

##handle arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '--LogToSheet', '-LS',
    action='store_true',
    help='Just Log to Google Sheets from XML'
)
parser.add_argument(
    '--LogToUnitas', '-LU',
    action='store_true',
    help='Just Log to Unitas from Google Sheets'
)
parser.add_argument(
    '--DoXMLStuff', '-DXS',
    action='store_true',
    help='Just do XML stuff. No log to Sheets or send to Unitas'
)
parser.add_argument(
    '--NoDelete', '-ND',
    action='store_true',
    help="Don't delete old XML files"
)
args = parser.parse_args()

# Load secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)
    
# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Scopes required for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = secrets["spreadsheet_id"]

XML_TO_SHEET_RANGE_NAME = secrets["xml_to_sheet_range_name"]

SHEET_TO_UNITAS_RANGE_NAME = secrets["sheet_to_unitas_range_name"]

# Authenticate with the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Sheets API client
service = build('sheets', 'v4', credentials=creds)

##End of Google Sheets stuff

if not args.LogToUnitas:
    do_xml_setup(secrets)
    valuesFromXML = run_xml_stuff()
    write_to_sheet(valuesFromXML, SPREADSHEET_ID, XML_TO_SHEET_RANGE_NAME, service)

if not args.LogToSheet
    do_unitas_setup(secrets)
    valuesToSend = read_from_sheet(SPREADSHEET_ID, SHEET_TO_UNITAS_RANGE_NAME, service)
    run_unitas_stuff(valuesToSend)

#delete all old files, so directory doesn't fill up.
if not args.NoDelete:
    deleteOldFiles()
