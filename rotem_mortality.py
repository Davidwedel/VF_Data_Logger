from rotem_login import login
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_mortality_page(driver):
   print("blah")

def make_driver(headless: bool = False):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

def run_mortality_to_rotem():
    driver = make_driver(False)
    login(driver)
    
    exit()
