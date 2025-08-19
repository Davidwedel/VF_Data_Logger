from unitas_login import login
from sheets_processing import read_from_sheet
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

FARM_ID = None
HOUSE_ID = None
COOLERLOG_URL = None
TIMEOUT = None
RANGE_NAME = None

def do_coolerlog_setup(secrets):
    global FARM_ID, HOUSE_ID, COOLERLOG_URL, TIMEOUT, RANGE_NAME
    
    COOLERLOG_URL = f"https://vitalfarms.poultrycloud.com/farm/cooler-log/coolerlog/new?farmId={FARM_ID}&houseId={HOUSE_ID}"
    RANGE_NAME = "Send_To_Bot!AW3:BB3"
    FARM_ID = secrets["Farm_ID"]
    HOUSE_ID = secrets["House_ID"]
    TIMEOUT = secrets["Timeout"]

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

def run_coolerlog_to_unitas():
    driver = make_driver(False)
    try:
        login(driver)
        open_coolerlog_page(driver)
        valuesToSend = read_from_sheet(RANGE_NAME)
        print(valuesToSend)
    finally:
        print("Quitting.")
        print("Goodbye!")
    
