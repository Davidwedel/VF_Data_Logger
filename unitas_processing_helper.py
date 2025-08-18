from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
from selenium.webdriver.common.by import By

TIMEOUT = None

#I hate this
def set_timeout(timeout):
    global TIMEOUT
    TIMEOUT = timeout

def col_to_num(col):
    num = 0
    for c in col:
        num = num * 26 + (ord(c.upper()) - ord('A') + 1)
    return num

def count_columns_in_range(range_str):
    match = re.search(r'!([A-Z]+)\d+:([A-Z]+)\d+', range_str)
    if not match:
        raise ValueError("Invalid range format")
    start_col, end_col = match.groups()
    return col_to_num(end_col) - col_to_num(start_col) + 1

def click_when_clickable(driver, by, locator, timeout = TIMEOUT):
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
    el = WebDriverWait(driver, timeout = TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    el.clear()
    el.send_keys(str(value))


def fill_input_by_datacy_and_id(driver, data_cy: str, element_id: str, value, timeout = TIMEOUT):

    if value is None or value == "":
        print("none")
        return

    wait = WebDriverWait(driver, timeout = TIMEOUT)
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
    input_element = WebDriverWait(driver, timeout = TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, field_id))
    )    

    # check if input is select box
    if input_element.tag_name.lower() != "select":
        input_element.clear()          # Clear any existing text
        
    input_element.send_keys(value) # Insert the new value

def fill_multiselect_box(driver, label, items):

    ul_id = f"list-{label}"

    # return if nothing
    if items == "":
        return

    print(label)

    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'[aria-labelledby="{label}"] button'))
)
    dropdown.click()

    # Wait for the dropdown options panel to be visible
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, ul_id))
    )

    # Convert string to list if needed
    if isinstance(items, str):
        items = [item.strip() for item in items.split(",")]

    # Click each item by visible text
    for item in items:
        try:
            xpath = f'//li[@data-cy="list-item"]//span[normalize-space()="{item}"]'
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            option.click()
        except Exception as e:
            print(f"⚠️ Could not select '{item}': {e}")

    # Close the dropdown again
    dropdown.click()

