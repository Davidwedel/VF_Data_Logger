from google.oauth2 import service_account
from googleapiclient.discovery import build
from unitas_helper import count_columns_in_range

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

