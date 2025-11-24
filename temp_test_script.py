from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from urllib.request import urlopen
from urllib.parse import urlparse

# Set up the web driver
driver = webdriver.Chrome()

# Load the test data from the API endpoints JSON file
with open('data/api_endpoints.json') as f:
    api_endpoints = json.load(f)

# Navigate to the target URL
driver.get('http://localhost:8000/static/checkout.html')

# Wait for the discount code field to be available
discount_code_field = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'discountCode'))
)

# Enter an invalid discount code
discount_code_field.send_keys('INVALID15')

# Click the Apply button to apply the discount code
apply_discount_button = driver.find_element_by_id('applyDiscount')
apply_discount_button.click()

# Wait for the error message to appear
error_message = WebDriverWait(driver, 10).until(
    EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#discountMessage'), 'Invalid code')
)

# Verify that the error message is displayed
assert error_message.text == 'Invalid code'

# Close the browser window
driver.quit()