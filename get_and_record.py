import argparse
import os
import time
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- config ----------
LOGIN_URL = "https://vitalfarms.poultrycloud.com/login"  # confirm this
PRODUCTION_URL_TMPL = "https://vitalfarms.poultrycloud.com/farm/production?farmId={farm_id}&houseId={house_id}"

HEADLESS = False  # set True for headless mode
# ----------------------------

##handle arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '--nowebsite', '-N',
    action='store_true',
    help='Pull from Google Sheets only.'
)
args = parser.parse_args()

# Load secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)

if not secrets:
    raise SystemExit("Fatal error. Set up secrets.json file.")

FARM_ID = secrets["Farm_ID"]
HOUSE_ID = secrets["House_ID"]
TIMEOUT = secrets["Timeout"]
USERNAME = secrets["Unitas_Username"]
PASSWORD = secrets["Unitas_Password"]
RANGE_NAME = secrets["range_name"]
SPREADSHEET_ID = secrets["spreadsheet_id"]

if not USERNAME or not PASSWORD:
    raise SystemExit("Set Unitas_Username and Unitas_Password in secrets.json!")

def make_driver(headless: bool = False):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

def click_when_clickable(driver, by, locator, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))

def input_by_label_text(driver, label_text: str, value: str, timeout=TIMEOUT):
    """
    Find an input, textarea or select following a label with text.
    Adjust the XPath if the site's DOM differs.
    """
    xpath = (
        f"//label[normalize-space(text())='{label_text}']"
        "/following::*[self::input or self::textarea or self::select][1]"
    )
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    el.clear()
    el.send_keys(str(value))

def login(driver):
    wait = WebDriverWait(driver, 10)
    driver.get(LOGIN_URL)
    username_box = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    password_box = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    username_box.send_keys(USERNAME)
    password_box.send_keys(PASSWORD)
    login_btn = click_when_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
    login_btn.click()
    WebDriverWait(driver, TIMEOUT).until_not(EC.url_contains("/login"))
    print("Logged in")

def open_production_page(driver, farm_id: int, house_id: int):
    url = PRODUCTION_URL_TMPL.format(farm_id=farm_id, house_id=house_id)
    driver.get(url)
    ## wait until page loaded
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".px-4.py-5"))
    )

    print("Production page opened")

def get_yesterdays_form(driver, timeout):
    wait = WebDriverWait(driver, timeout)

    target = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "(//li[@data-cy='list-item' and @aria-label='daily'])[2]"
    )))
    target.click()
    print("Opening Yesterday's form.")

    # Wait for the next page/section to be ready
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, "//h3[normalize-space()='House']"))
    )
    print("Yesterday's form opened.")
    # Just sit and wait for 3 seconds
    time.sleep(.5)

def fill_production_form(driver, data: dict):
    
    def fill_input_by_datacy_and_id(driver, data_cy: str, element_id: str, value, timeout: int = 10):

        if value is None or value == "":
            print("none")
            return

        wait = WebDriverWait(driver, timeout)
        try:
            el = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//select[@data-cy='{data_cy}' and @id='{element_id}']"
                ))
            )

            el.send_keys(value) # Insert the new value

        except TimeoutException:
            raise RuntimeError(
                f"No <select> found with data-cy='{data_cy}' and id='{element_id}'"
            )


    def fill_input_by_id(driver, field_id, value, timeout=TIMEOUT):
        # empty. return
        if value is None or value == "":
            return

        # Wait for the input field to be visible
        input_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, field_id))
        )    

        # check if input is select box
        if input_element.tag_name.lower() != "select":
            input_element.clear()          # Clear any existing text
            
        input_element.send_keys(value) # Insert the new value


    #mortality_indoor = data[0]
    fill_input_by_id(driver, "V33-H1", data[0][0])

    #mortality_outdoor = data[1]
    fill_input_by_id(driver, "V35-H1", data[0][1])

    #euthanized_indoor = data[2]
    fill_input_by_id(driver, "V34-H1", data[0][2])
    
    #euthanized_outdoor = data[3]
    fill_input_by_id(driver, "V36-H1", data[0][3])

    #depop_number = data[4]
    fill_input_by_id(driver, "V101-H1", data[0][4])

    #cull_reason = data[5]
    #mortality_reason = data[6]


    #mortality_comments = data[7]
    fill_input_by_id(driver, "V81-H1", data[0][7])

    #total_eggs = data[8]
    fill_input_by_id(driver, "V4-H1", data[0][8])

    #floor_eggs = data[9]
    fill_input_by_id(driver, "V1-H1", data[0][9])

    #nutritionist = data[10]
    fill_input_by_id(driver, "V32-H1", data[0][10])

    #ration_used = data[11]
    fill_input_by_id(driver, "V31-H1", data[0][11])

    #feed_consumption = data[12]
    fill_input_by_id(driver, "V39-H1", data[0][12])
    
    #ration_delivered = data[13]
    fill_input_by_id(driver, "V70-H1", data[0][13])
    
    #amount_delivered = data[14]
    fill_input_by_id(driver, "V23-H1", data[0][14])

    #lights_on_hh = data[15]
    if data[0][15].strip() != "":
        formatted_hour = f"{int(data[0][15]):02d}"
        fill_input_by_datacy_and_id(driver, "input-hour", "V99-H1", formatted_hour)

    #lights_on_mm = data[16]
    if data[0][16].strip() != "":
        formatted_minute = f"{int(data[0][16]):02d}"  # "05"
        fill_input_by_datacy_and_id(driver, "input-minute", "V99-H1", formatted_minute)

    #lights_off_hh = data[17]
    if data[0][17].strip() != "":
        formatted_hour = f"{int(data[0][17]):02d}"
        fill_input_by_datacy_and_id(driver, "input-hour", "V100-H1", formatted_hour)

    #lights_off_mm = data[18]
    if data[0][18].strip() != "":
        formatted_minute = f"{int(data[0][18]):02d}"  # "05"
        fill_input_by_datacy_and_id(driver, "input-minute", "V100-H1", formatted_minute)

    #added_supplements = data[19]
    fill_input_by_id(driver, "V25-H1", data[0][19])

    #water_consumption = data[20]
    fill_input_by_id(driver, "V27-H1", data[0][20])
        
    #body_weight = data[21]
    fill_input_by_id(driver, "V37-H1", data[0][21])
        
    #case_weight = data[22]
    fill_input_by_id(driver, "V11-H1", data[0][22])
        
    #yolk_color = data[23]
    fill_input_by_id(driver, "V98-H1", data[0][23])
        
    #door_open_hh = data[24]
    if data[0][24].strip() != "":
        formatted_hour = f"{int(data[0][24]):02d}"
        fill_input_by_datacy_and_id(driver, "input-hour", "V78-H1", formatted_hour)

    #door_open_mm = data[25]
    if data[0][25].strip() != "":
        formatted_minute = f"{int(data[0][25]):02d}"  # "05"
        fill_input_by_datacy_and_id(driver, "input-minute", "V78-H1", formatted_minute)

    #door_close_hh = data[26]
    if data[0][26].strip() != "":
        formatted_hour = f"{int(data[0][26]):02d}"
        fill_input_by_datacy_and_id(driver, "input-hour", "V79-H1", formatted_hour)

    #door_close_mm = data[27]
    if data[0][27].strip() != "":
        formatted_minute = f"{int(data[0][27]):02d}"  # "05"
        fill_input_by_datacy_and_id(driver, "input-minute", "V79-H1", formatted_minute)

    #birds_restricted = data[28]
    fill_input_by_id(driver, "V92-H1", data[0][28])
        
    #birds_restricted_reason = data[29]
    fill_input_by_id(driver, "V97-H1", data[0][29])
        
    #inside_high = data[30]
    fill_input_by_id(driver, "V28-H1", data[0][30])
        
    #inside_low = data[31]
    fill_input_by_id(driver, "V29-H1", data[0][31])
        
    #outside_high = data[32]
    fill_input_by_id(driver, "V72-H1", data[0][32])
        
    #outside_low = data[33]
    fill_input_by_id(driver, "V71-H1", data[0][33])
        
    #air_sensory = data[34]
    fill_input_by_id(driver, "V89-H1", data[0][34])
        
    #weather_conditions = data[35]
    fill_input_by_id(driver, "V90-H1", data[0][35])
        
    #outside_drinkers_clean = data[36]
    fill_input_by_id(driver, "V95-H1", data[0][36])
        
    #birds_found_under_slats = data[37]
    fill_input_by_id(driver, "V77-H1", data[0][37])
        
    #safe_environment_indoors = data[38]
    fill_input_by_id(driver, "V93-H1", data[0][38])
        
    #safe_environment_outdoors = data[39]
    fill_input_by_id(driver, "V94-H1", data[0][39])
        
    #equipment_functioning = data[40]
    fill_input_by_id(driver, "V91-H1", data[0][40])
        
    #predator_activity = data[41]
    fill_input_by_id(driver, "V88-H1", data[0][41])
        
    #comment = data[42]
    #fill_input_by_id(driver, "Comment-H1", data[0][42])

def main():

    ##Google Sheets stuff

    # Path to your downloaded service account key
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    # Scopes required for Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Auth
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    ## end of Google Sheets stuff

    driver = make_driver(HEADLESS)
    try:
        if args.nowebsite:
            print("Dry Run! Website Disabled!")
        else:
            login(driver)
            open_production_page(driver, FARM_ID, HOUSE_ID)
            get_yesterdays_form(driver, TIMEOUT)


        # Sheets client
        service = build("sheets", "v4", credentials=creds)

        # Read
        resp = service.spreadsheets().values().get(
             spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = resp.get("values", [])  # type: list[list[str]]
        print(values)
        fill_production_form(driver, values)
        print("Worked!")
        time.sleep(1)

    finally:
        print("Quitting. Look over the data and Save.")
        print("Don't forget to close the browser window when you are done.")
        print("Goodbye!")

if __name__ == "__main__":
    main()
