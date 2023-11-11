import subprocess  # noqa

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains  # noqa
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from icecream import ic

from decouple import config

# User Credentials
USERNAME = config("USERNAME")
EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD", default="password not provided")
SECRET_ANSWER = config("SECRET_ANSWER", default="answer not provided")
PORTAL_LINK = config("PORTAL_LINK", default="https://www.upwork.com/ab/account-security/login")

# CONSTANTS
TIMEOUT_IN_SECONDS = 10.0

COOKIES_POPUP = "ot-sdk-container"
COOKIES_ACCEPT_ALL_BTN = "onetrust-accept-btn-handler"

USERNAME_INPUT = "login_username"
PASSWORD_INPUT = "login_password"  # noqa: S105
SECRET_ANSWER_INPUT = "login_answer"  # name="login[answer]"

LOGIN_PASS_NEXT_BTN = "login_password_continue"
LOGIN_CONTROL_NEXT_BTN = "login_control_continue"

COMPLETE_PROFILE_MODAL = "//div[contains(@class, 'profile-completeness-modal-container')]"
COMPLETE_PROFILE_MODAL_CLOSE_BTN = "//div[@role='dialog']//button[contains(text(),'Close')]"

# 1. Start the session
#  service_args=["--log-level=DEBUG"], log_output=subprocess.STDOUT
service = ChromeService(
    executable_path=ChromeDriverManager().install(),
)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options, service=service)

# 2. Navigate to Upwork login page
driver.get(PORTAL_LINK)
wait = WebDriverWait(driver, timeout=TIMEOUT_IN_SECONDS)

# ic(driver.get_cookies())
# ic(driver.current_url)
# Session info: chrome=119.0.6045.123

try:
    # option 1
    # wait = WebDriverWait(driver, timeout=TIMEOUT_IN_SECONDS)
    # wait.until(EC.element_to_be_clickable((By.ID, COOKIES_ACCEPT_ALL_BTN)))
    # cookie_ok_button = driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN)
    # cookie_ok_button.click()
    # -> selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element is not clickable at point (318, 853)

    # option 2, works-worked
    # cookie_accept_btn = driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN)
    # wait.until(lambda d : cookie_accept_btn.is_displayed())
    # actions = ActionChains(driver)
    # actions.move_to_element(cookie_accept_btn).click().perform()

    # option 2b,
    # cookie_accept_btn = driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN)
    # cookie_accept_btn = wait.until(EC.visibility_of_element_located((By.ID, COOKIES_ACCEPT_ALL_BTN)))
    # ActionChains(driver).click(cookie_accept_btn).perform()

    # option 3
    # cookie_accept_btn = wait.until(EC.visibility_of_element_located((By.ID, COOKIES_ACCEPT_ALL_BTN)))
    # driver.execute_script("arguments[0].scrollIntoView();", cookie_accept_btn)
    # cookie_accept_btn.click()

    # option 4 WORKS, 00:09, 9.11.2023 :)
    # cookies_popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, COOKIES_POPUP)))
    # wait.until(EC.element_to_be_clickable((By.ID, COOKIES_ACCEPT_ALL_BTN)))
    # cookie_accept_btn = driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN)
    # cookie_accept_btn.click()

    # option 5
    errors = [NoSuchElementException, ElementClickInterceptedException]
    wait = WebDriverWait(driver, timeout=TIMEOUT_IN_SECONDS, poll_frequency=1.0, ignored_exceptions=errors)
    cookies_popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, COOKIES_POPUP)))
    btn = wait.until(EC.element_to_be_clickable((By.ID, COOKIES_ACCEPT_ALL_BTN)))
    # location  {'x': 255, 'y': 819}
    # rect {'height': 40, 'width': 128, 'x': 254.765625, 'y': 819}
    # breakpoint()
    driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN).click()

    # option 6 - WORKS, 23:52, 8.11.2023 :)
    # cookie_accept_btn = driver.find_element(by=By.ID, value=COOKIES_ACCEPT_ALL_BTN)
    # wait.until(EC.visibility_of(cookie_accept_btn)).click()
except TimeoutException as exc:
    ic("STEP accept cookies")
    ic(exc)
    # If there are throttling/slow connection - just procceed next since we are not obliged to accept cookies
    pass


# STEP 1. Enter email
email_field = driver.find_element(by=By.ID, value=USERNAME_INPUT)
email_field.send_keys(EMAIL)
continue_with_email_btn = driver.find_element(by=By.ID, value=LOGIN_PASS_NEXT_BTN)
continue_with_email_btn.click()


# -> POST https://www.upwork.com/ab/account-security/login 200 OK
# payload = {
#     "login": {
#         "mode": "username",
#         "iovation": "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;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",
#         "username": "ivanprytula@ukr.net",
#         "elapsedTime": 219033,
#         "forterToken": "349b9d9c15484b2f9d6910472fb580de_1699382204153__UDF43-m4_14ck_tt",
#         "deviceType": "desktop"
#     }
# }

# resp = {"success":0,"userNid":"1941e405","mode":"password"}

# STEP 2. Enter password on the next step of the "auth wizard" form / id="main-auth-card"
wait.until(
    EC.element_to_be_clickable((By.ID, PASSWORD_INPUT))
)  #  return element if element.is_displayed() == visibility else False
password_field = driver.find_element(by=By.ID, value=PASSWORD_INPUT)
password_field.send_keys(PASSWORD)
login_btn = driver.find_element(by=By.ID, value=LOGIN_CONTROL_NEXT_BTN)  # continue_btn.text = Continue
login_btn.click()

# -> POST https://www.upwork.com/ab/account-security/login 200 OK
# payload = {
#   "login": {
#     "mode": "password",
#     "iovation": "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;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",
#     "username": "recruitment+scanners+task@argyle.com",
#     "elapsedTime": 38179,
#     "forterToken": "d03a98ef571b41449df5a43cde64aa84_1699487873182__UDF43-m4_14ck_tt",
#     "deviceType": "desktop",
#     "password": "ArgyleAwesome!@",
#     "securityCheckCertificate": "eyJraWQiOiJyZWdpc3RyYXRpb24ua2V5LnJzYTUxMi5wdWJsaWMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhdXRoRFMiLCJzdWIiOiIxOTQxZTQwNSIsInJlcXVlc3RJZCI6InYydHdJelhFS0xYZGlVTlFXd0VUSjR6bTBWOUhlX3hyMkJoWnZ5VldZMWMiLCJpc3MiOiJhdXRoRFMiLCJ2bmRfZW9fdHlwZSI6IlNFQ1VSSVRZX0NIRUNLIiwidmVuZG9ySWQiOiJJT1ZBVElPTiIsImV4cCI6MTY5OTQ4NzkyMiwiaWF0IjoxNjk5NDg3OTEyfQ.FKoW2oWzd9WDd34XOQG7rC5CI2b8oMjAyktP221sVcXTU9p-hq4p8FFhelZDISyZCykHJCBcg8hC_jQgf5hgcg",
#     "authToken": "f258c95fee62377f5cf24bb661a7aca62cd3f74b3370100ba20f4a5b3ffd4fb6"
#   }
# }
# resp = {
#     "success": 0,
#     "alerts": {
#         "top": [
#             {
#                 "message": "",
#                 "type": "danger"
#             }
#         ]
#     },
#     "eventCode": "securityCheckCertificate",
#     "authToken": "f258c95fee62377f5cf24bb661a7aca62cd3f74b3370100ba20f4a5b3ffd4fb6",
#     "requestId": "v2twIzXEKLXdiUNQWwETJ4zm0V9He_xr2BhZvyVWY1c",
#     "securityCheckCertificate": "eyJraWQiOiJyZWdpc3RyYXRpb24ua2V5LnJzYTUxMi5wdWJsaWMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhdXRoRFMiLCJzdWIiOiIxOTQxZTQwNSIsInJlcXVlc3RJZCI6InYydHdJelhFS0xYZGlVTlFXd0VUSjR6bTBWOUhlX3hyMkJoWnZ5VldZMWMiLCJpc3MiOiJhdXRoRFMiLCJ2bmRfZW9fdHlwZSI6IlNFQ1VSSVRZX0NIRUNLIiwidmVuZG9ySWQiOiJJT1ZBVElPTiIsImV4cCI6MTY5OTQ4NzkyMiwiaWF0IjoxNjk5NDg3OTEyfQ.FKoW2oWzd9WDd34XOQG7rC5CI2b8oMjAyktP221sVcXTU9p-hq4p8FFhelZDISyZCykHJCBcg8hC_jQgf5hgcg"
# }

# STEP 4. Enter security answer if applicable
try:
    wait.until(EC.element_to_be_clickable((By.ID, SECRET_ANSWER_INPUT)))
    answer_field = driver.find_element(by=By.ID, value=SECRET_ANSWER_INPUT)
    answer_field.send_keys(SECRET_ANSWER)

    continue_btn = driver.find_element(by=By.ID, value=LOGIN_CONTROL_NEXT_BTN)  # continue_btn.text = Continue
    continue_btn.click()
except TimeoutException as exc:
    # Security question modal may not be displayed, so proceed next
    ic("STEP 4. Enter security answer if applicable")
    ic(str(exc))
    pass

# STEP 5. Close 'Complete your profile' popup if applicable
try:
    wait.until(EC.element_to_be_clickable((By.XPATH, COMPLETE_PROFILE_MODAL_CLOSE_BTN))).click()
    # close_btn = driver.find_element(By.XPATH, COMPLETE_PROFILE_MODAL_CLOSE_BTN)
except TimeoutException as exc:
    ic("STEP 5. Close 'Complete your profile' popup if applicable")
    ic(exc)
    # If profile is 100% completed, 'Complete your profile' popup is not displayed
    pass

# After login user is redirected to:
# https://www.upwork.com/nx/find-work/ ->> https://www.upwork.com/nx/find-work/best-matches

# End the session
# driver.quit()


# TODO: 9.11 - switch to  Playwright for login
