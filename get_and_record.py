import os
import time
import json

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


# Load secrets
with open("environment.json", "r") as f:
    environment = json.load(f)

if not environment:
    raise SystemExit("Fatal error. Set up environment.json file.")

FARM_ID = environment["Farm_ID"]
HOUSE_ID = environment["House_ID"]
TIMEOUT = environment["Timeout"]
USERNAME = environment["Unitas_Username"]
PASSWORD = environment["Unitas_Password"]

if not USERNAME or not PASSWORD:
    raise SystemExit("Set Unitas_Username and Unitas_Password in environment.json!")

def make_driver(headless: bool = False):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

def wait(driver, by, locator, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

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
    WebDriverWait(driver, 10).until(
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
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h3[normalize-space()='House']"))
    )
    print("Yesterday's form opened.")
    # Just sit and wait for 3 seconds
    time.sleep(3)

def fill_production_form(driver, data: dict):
    for label, value in data.items():
        input_by_label_text(driver, label, value)

def save(driver):
    save_btn = click_when_clickable(driver, By.XPATH, "//button[contains(., 'Save') or contains(., 'Submit')]")
    save_btn.click()
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Saved successfully')]"))
    )

def main():
    driver = make_driver(HEADLESS)
    try:
        login(driver)
        open_production_page(driver, FARM_ID, HOUSE_ID)
        get_yesterdays_form(driver, TIMEOUT)
        data = {
            "Date": "2025-07-24",
            "Eggs collected": 12345,
            "Mortality": 3,
        }
        fill_production_form(driver, data)
        save(driver)
        print("Data submitted successfully!")
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
