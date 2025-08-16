import time
import argparse
from xml_processing import do_xml_setup, run_xml_stuff, deleteOldFiles
from sheets_processing import read_from_sheet, write_to_sheet
from unitas_processing import do_unitas_setup, run_unitas_stuff
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
##Google Sheets stuff

##handle arguments
parser = argparse.ArgumentParser(
        epilog="""***!!!REMEMBER!!!*** All actions are performed on Yesterdays data. This includes all logging from XMLs and logging to Unitas!
        All arguments will only run once. To run in 'Forever Mode', where the script is fully automatic, just drop all arguments."""
        )

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
parser.add_argument(
    '--SingleRun', '-SR',
    action='store_true',
    help="Run once, for single log, not the forever run"
)
parser.add_argument(
    '--XMLThenCheckBox', '-XTC',
    action='store_true',
    help='Log from XMLs, then watch checkbox in spreadsheet, and log to Unitas when it is checked'
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

#checkbox log cell
checkbox_cell = "Send_To_Bot!BD3:BD3"

##End of Google Sheets stuff

if args.SingleRun or args.LogToSheet or args.DoXMLStuff or args.XMLThenCheckBox or args.LogToUnitas:
    print(f"Running in Single Run mode.")

    # read XMLs, delete
    if not args.LogToUnitas:
        do_xml_setup(secrets)
        valuesFromXML = run_xml_stuff()
        write_to_sheet(valuesFromXML, SPREADSHEET_ID, XML_TO_SHEET_RANGE_NAME, service)
        #delete all old files, so directory doesn't fill up.
        if not args.NoDelete:
            deleteOldFiles()

    # we want to log to Unitas *at some point*
    if not args.LogToSheet:
        do_unitas_setup(secrets)

        if args.XMLThenCheckBox:
            while True:
                do_unitas_stuff = read_from_sheet(SPREADSHEET_ID, checkbox_cell, service)
                string_value = do_unitas_stuff[0][0]
                bool_value = string_value.upper() == 'TRUE'
                do_unitas_stuff = bool_value
                if do_unitas_stuff:
                    break

                time.sleep(10)

        valuesToSend = read_from_sheet(SPREADSHEET_ID, SHEET_TO_UNITAS_RANGE_NAME, service)
        run_unitas_stuff(valuesToSend)


else:
    print(f"Running in Forever Run mode.")

    do_unitas_setup(secrets)
    do_xml_setup(secrets)

    do_unitas_stuff = False
    xml_to_sheet_ran = False
    sheet_to_unitas_ran = False

    try:
        while True:
            now = datetime.datetime.now()

            if now.hour == 0 and now.minute == 15:
                if not xml_to_sheet_ran:
                    
                    if not args.LogToUnitas:
                        # log from XML file to sheets
                        valuesFromXML = run_xml_stuff()
                        write_to_sheet(valuesFromXML, SPREADSHEET_ID, XML_TO_SHEET_RANGE_NAME, service)

                        #delete all old files, so directory doesn't fill up.
                        if not args.NoDelete:
                            deleteOldFiles()

                    xml_to_sheet_ran = True

            elif now.hour == 0 and now.minute == 00:
                sheet_to_unitas_ran = False  # Reset at midnight 
                xml_to_sheet_ran = False

            elif xml_to_sheet_ran and not sheet_to_unitas_ran:
                if not args.LogToSheet:
                    do_unitas_stuff = read_from_sheet(SPREADSHEET_ID, checkbox_cell, service)
                    string_value = do_unitas_stuff[0][0]
                    bool_value = string_value.upper() == 'TRUE'
                    do_unitas_stuff = bool_value
                    if do_unitas_stuff:
                        valuesToSend = read_from_sheet(SPREADSHEET_ID, SHEET_TO_UNITAS_RANGE_NAME, service)
                        run_unitas_stuff(valuesToSend)

                        sheet_to_unitas_ran = True

                

            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped by user")
