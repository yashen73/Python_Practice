from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Create a Chrome browser instance
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open a website
driver.get("https://www.google.com")

print("Chrome opened successfully!")

# Keep browser open for a few seconds (optional)
import time
time.sleep(30)

# Close browser
driver.quit()
