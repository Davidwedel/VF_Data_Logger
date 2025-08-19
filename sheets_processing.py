from google.oauth2 import service_account
from googleapiclient.discovery import build
from unitas_processing_helper import count_columns_in_range

BACKOFF = 5
RETRIES = 3
def write_to_sheet(values, SPREADSHEET_ID, RANGE_NAME, service):
    body = {
        'values': values
    }


    # Append the rows
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',  # or RAW
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedRows')} rows appended.")

def read_from_sheet(SPREADSHEET_ID, RANGE_NAME, service):
    attempt = 0
    while attempt < RETRIES:
        try:

            # Read
            resp = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()

            values = resp.get("values", [])  # type: list[list[str]]

            cols = (count_columns_in_range(RANGE_NAME) - 1)
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

