from icecream import ic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 1. Start the session
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# 2. Take action on browser
driver.get("https://www.selenium.dev/selenium/web/web-form.html")

# 3. Request browser information
title = driver.title
ic(title)

# 4. Establish Waiting Strategy: This method only needs to be called one time per session
# https://www.selenium.dev/documentation/webdriver/waits/#implicit-waits
driver.implicitly_wait(0.5)

# 5. Find an element
text_box = driver.find_element(by=By.NAME, value="my-text")
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

# 6. Take action on element
text_box.send_keys("Selenium")
submit_button.click()

message = driver.find_element(by=By.ID, value="message")

# 7. Request element information
text = message.text
ic(text)

# 8. End the session
# Important note: the quit method is different from the close method, and it is recommended to always use quit to end the session
driver.quit()
