import logging
import sys
import pathlib
import schedule
import time
import argparse
from xml_processing import do_xml_setup, run_xml_stuff, deleteOldFiles
from sheets_processing import read_from_sheet, write_to_sheet, sheets_setup
from unitas_production import do_unitas_setup, run_unitas_stuff
import unitas_coolerlog as coolerlog
from unitas_login import setup_unitas_login
from unitas_helper import set_timeout
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import runstate as runstate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.info("This will show up in systemd logs")

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
parser.add_argument(
    '--CoolerLogToUnitas', '-CTU',
    action='store_true',
    help='Log yesterdays Cooler Temps to Unitas'
)

args = parser.parse_args()

# Load secrets

CONFIG_FILE = pathlib.Path(__file__).parent / "secrets.json"

with open(CONFIG_FILE, "r") as f:
    secrets = json.load(f)
    
# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = pathlib.Path(__file__).parent / 'credentials.json'

# Scopes required for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = secrets["spreadsheet_id"]

XML_TO_SHEET_RANGE_NAME = secrets["xml_to_sheet_range_name"]

SHEET_TO_UNITAS_RANGE_NAME = secrets["sheet_to_unitas_range_name"]

RETRIEVE_FROM_XML_TIME = secrets["retrieve_from_xml_time"]

LOG_COOLER_TO_UNITAS = secrets["Cooler_Log_To_Unitas"]

# Authenticate with the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Sheets API client
service = build('sheets', 'v4', credentials=creds)

#checkbox log cell
checkbox_cell = "Send_To_Bot!AU3:AU3"

#cooler log to unitas cell range
COOLER_LOG_TO_UNITAS_CELL_RANGE = "Send_To_Bot!AV3:BC3"

TIMEOUT = secrets["Timeout"]

##End of Google Sheets stuff

runstate.make_sure_exists()
sheets_setup(secrets, service)
setup_unitas_login(secrets)
set_timeout(TIMEOUT)
coolerlog.do_coolerlog_setup(secrets, COOLER_LOG_TO_UNITAS_CELL_RANGE)

if args.CoolerLogToUnitas:
    coolerlog.run_coolerlog_to_unitas()

elif args.SingleRun or args.LogToSheet or args.DoXMLStuff or args.XMLThenCheckBox or args.LogToUnitas:
    print(f"Running in Single Run mode.")

    # read XMLs, delete
    if not args.LogToUnitas:
        do_xml_setup(secrets)
        valuesFromXML = run_xml_stuff()
        write_to_sheet(valuesFromXML, SPREADSHEET_ID, XML_TO_SHEET_RANGE_NAME, service)
        runstate.save_data()

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

        valuesToSend = read_from_sheet(SHEET_TO_UNITAS_RANGE_NAME)
        run_unitas_stuff(valuesToSend)


else:
    print(f"Running in Forever Run mode.")

    do_unitas_setup(secrets)
    do_xml_setup(secrets)

    do_unitas_stuff = False
    xml_to_sheet_ran = runstate.load_data()
    sheet_to_unitas_ran = False

    def coolerlog_unitas():
        if(LOG_COOLER_TO_UNITAS):
            coolerlog.run_coolerlog_to_unitas()


    def reset_flags():
        """Reset daily run flags at midnight."""
        global xml_to_sheet_ran, sheet_to_unitas_ran
        xml_to_sheet_ran = False
        sheet_to_unitas_ran = False
        print("[Reset] Flags reset at midnight")

    def xml_to_sheet_job():
        """Run XML → Sheets logging once per day."""
        global xml_to_sheet_ran
        if not xml_to_sheet_ran:
            if not args.LogToUnitas:
                valuesFromXML = run_xml_stuff()
                write_to_sheet(valuesFromXML, SPREADSHEET_ID, XML_TO_SHEET_RANGE_NAME, service)
                runstate.save_data()
                if not args.NoDelete:
                    deleteOldFiles()
                xml_to_sheet_ran = True
                print("[XML] Logged XML → Sheets")

    def check_and_run_unitas():
        """Poll spreadsheet and run Unitas if checkbox is TRUE."""
        global xml_to_sheet_ran, sheet_to_unitas_ran
        if xml_to_sheet_ran and not sheet_to_unitas_ran and not args.LogToSheet:
            do_unitas_stuff = read_from_sheet(SPREADSHEET_ID, checkbox_cell, service)
            bool_value = do_unitas_stuff[0][0].upper() == 'TRUE'
            if bool_value:
                valuesToSend = read_from_sheet(SPREADSHEET_ID, SHEET_TO_UNITAS_RANGE_NAME, service)
                run_unitas_stuff(valuesToSend)
                sheet_to_unitas_ran = True
                print("[Unitas] Logged Sheet → Unitas")

    # ─── Scheduling ───
    schedule.every().day.at("00:00:00").do(reset_flags)      # reset daily
    schedule.every().day.at(RETRIEVE_FROM_XML_TIME).do(xml_to_sheet_job) # XML → Sheets
    schedule.every(10).seconds.do(check_and_run_unitas)      # poll spreadsheet

    # define a helper to calculate the coolerlog->unitas run time
    def schedule_offset(base_time="00:15:00", offset_minutes=15):
        h, m, s = map(int, base_time.split(":"))
        target = (datetime.combine(datetime.today(), datetime.min.time())
                  + timedelta(hours=h, minutes=m, seconds=s)
                  + timedelta(minutes=offset_minutes))
        return target.strftime("%H:%M:%S")

    run_time = schedule_offset("00:15:00", 15)  # -> "00:30:00"
    schedule.every().day.at(run_time).do(coolerlog_unitas)

    print(f"Job scheduled at {run_time}")

    try:

        ##this is the forever loop
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped by user")
