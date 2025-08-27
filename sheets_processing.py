from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from unitas_helper import count_columns_in_range
import pathlib

SERVICE = None
SPREADSHEET_ID = None
BACKOFF = 5
RETRIES = 3

def sheets_setup(secrets):
    global SERVICE, SPREADSHEET_ID

    SPREADSHEET_ID = secrets["spreadsheet_id"]

    # Path to your downloaded service account key
    SERVICE_ACCOUNT_FILE = pathlib.Path(__file__).parent / 'credentials.json'

    # Scopes required for Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Authenticate with the service account
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Sheets API client
    SERVICE = build('sheets', 'v4', credentials=creds)

def write_to_sheet(values, RANGE_NAME):
    body = {
        'values': values
    }


    # Append the rows
    result = SERVICE.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',  # or RAW
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedRows')} rows appended.")

def read_from_sheet(RANGE_NAME):
    attempt = 0
    while attempt < RETRIES:
        try:
            # Read
            resp = SERVICE.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()

            values = resp.get("values", [])  # type: list[list[str]]

            cols = (count_columns_in_range(RANGE_NAME))
            #print(cols)
            values = [row + [""] * (cols - len(row)) for row in values]

            #print(values)
            return values

        except HttpError as error:
            # Handle Google Sheets API errors
            if error.resp.status == 500:
                logging.error(f"Google Sheets API server error (500) on attempt {attempt + 1}. Retrying in {BACKOFF} seconds...")
                time.sleep(BACKOFF)  # Backoff before retrying
                attempt += 1
                BACKOFF *= 2  # Exponential backoff for retries
            else:
                logging.error(f"An error occurred: {error}")
                break
        except Exception as e:
            # Handle other exceptions
            logging.error(f"Unexpected error: {e}")
            break

    logging.error("Failed to read from Google Sheets after multiple attempts.")
    return []

