from unitas_login import login
from sheets_processing import read_from_sheet
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import unitas_helper as helper

FARM_ID = None
HOUSE_ID = None
COOLERLOG_URL = None
TIMEOUT = None
RANGE_NAME = None
INITIALS = None

def do_coolerlog_setup(secrets, range_name):
    global FARM_ID, HOUSE_ID, COOLERLOG_URL, TIMEOUT, RANGE_NAME, INITIALS
    
    COOLERLOG_URL = f"https://vitalfarms.poultrycloud.com/farm/cooler-log/coolerlog/new?farmId={FARM_ID}&houseId={HOUSE_ID}"
    RANGE_NAME = range_name
    FARM_ID = secrets["Farm_ID"]
    HOUSE_ID = secrets["House_ID"]
    TIMEOUT = secrets["Timeout"]
    INITIALS = secrets["Cooler_Log_Initials"]

def make_driver(headless: bool = False):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )
def open_coolerlog_page(driver):
    driver.get(COOLERLOG_URL)

def fill_coolerlog_values(driver, data):

    # yesterday in "01 Jul 2025"
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d %b %Y")
    print("Setting date:", yesterday_str)

    date_input = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "select-date-input"))
    )
    # Find the input
    date_input = driver.find_element("id", "select-date-input")

    # Inject the value and trigger events
    driver.execute_script(f"""
        arguments[0].value = "{yesterday_str}";
        """, date_input)

    # start filling in the rest

    #AM_Check_hh
    if data[0][0].strip() != "":
        formatted_hour = f"{int(data[0][0]):02d}"
        helper.fill_input_by_datacy_and_id(driver, "input-hour", "AMCheck-H1", formatted_hour)

    #AM_Check_mm
    if data[0][1].strip() != "":
        formatted_minute = f"{int(data[0][1]):02d}"  # "05"
        helper.fill_input_by_datacy_and_id(driver, "input-minute", "AMCheck-H1", formatted_minute)

    ## am temp
    helper.fill_input_by_id(driver, "AMTemp-H1", data[0][2])

    ## am temp initials
    helper.fill_input_by_id(driver, "AMInitial-H1", INITIALS)

    #PM_Check_hh = data[17]
    if data[0][3].strip() != "":
        formatted_hour = f"{int(data[0][3]):02d}"
        helper.fill_input_by_datacy_and_id(driver, "input-hour", "PMCheck-H1", formatted_hour)

    #PM_Check_mm = data[18]
    if data[0][4].strip() != "":
        formatted_minute = f"{int(data[0][4]):02d}"  # "05"
        helper.fill_input_by_datacy_and_id(driver, "input-minute", "PMCheck-H1", formatted_minute)
        
    ## pm temp
    helper.fill_input_by_id(driver, "PMTemp-H1", data[0][5])

    ## pm temp initials
    helper.fill_input_by_id(driver, "PMInitial-H1", INITIALS)

    ## eggs picked up
    helper.fill_input_by_id(driver, "EggsPick-H1", data[0][6])

    ## comments
    helper.fill_input_by_id(driver, "Comments-H1", data[0][7])


def run_coolerlog_to_unitas():
    driver = make_driver(False)
    try:
        login(driver)
        open_coolerlog_page(driver)
        valuesToSend = read_from_sheet(RANGE_NAME)
        print(valuesToSend)
        fill_coolerlog_values(driver, valuesToSend)
        
    finally:
        print("Quitting.")
        print("Goodbye!")
    
