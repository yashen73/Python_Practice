from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Launch browser
driver = webdriver.Chrome()  # Make sure ChromeDriver is installed
driver.get("https://example.com")

# Wait for site to load
time.sleep(2)

# Find a button by ID, class, text, or CSS selector
button = driver.find_element(By.XPATH, "//div[@role = 'button' and .='Login']")

# Click the button
button.click()

print("Button clicked!")
