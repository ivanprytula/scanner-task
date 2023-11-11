import json
from pathlib import Path

from decouple import config
from icecream import ic
from loguru import logger
from playwright.sync_api import Error, Playwright, expect, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# User Credentials
USERNAME = config("USERNAME")
EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD", default="password not provided")
SECRET_ANSWER = config("SECRET_ANSWER", default="answer not provided")
PORTAL_LINK = config("PORTAL_LINK", default="https://www.upwork.com/ab/account-security/login")


# CONSTANTS
TIMEOUT_IN_MS = 5_000
PROJECT_ROOT = Path(__file__).resolve(strict=True).parent
PRODUCTION_LOG_FILE = PROJECT_ROOT / "production.log"
TASK_LEVEL_1_RESULTS = PROJECT_ROOT / f"{USERNAME}_task_level_1.json"
DEBUG = config("DEBUG", default=False, cast=bool)
PRODUCTION = not DEBUG


def run(playwright: Playwright) -> None:
    # 0. Setup browser. Make sure to run headed.
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # def log_and_continue_request(route, request):
    #     ic(request.url, request.method, request.redirected_from)
    #     route.continue_()

    # # Log and continue all network requests
    # context.route("**/*", log_and_continue_request)

    # Create a new page in a pristine context
    page = context.new_page()

    # main_page_find_work = {}
    def on_main_portal_page_load(request):
        if request.url == "https://www.upwork.com/nx/find-work/":
            # ic(dir(request))
            # ic(request.url)
            ic(request.headers)
            # ic(request.redirected_from)  # https://www.upwork.com/signup/home
            # ic(request.response())
            ic("\n\n")
            # page.pause()
            # ic(request.response().text())

    """
    ic| request.url: 'https://www.upwork.com/nx/find-work/'
    ic| request.headers: {'referer': 'https://www.upwork.com/ab/account-security/login',
                        'sec-ch-ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Linux"',
                        'upgrade-insecure-requests': '1',
                        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                                        'like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    ic| request.redirected_from: <Request url='https://www.upwork.com/signup/home' method='GET'>
    ic| request.response(): <Response url='https://www.upwork.com/nx/find-work/' request=<Request url='https://www.upwork.com/nx/find-work/' method='GET'>>
        """

    profile_fwh = {}
    profile_pib_status = {}

    def get_targeted_resp(response):
        # urls = [
        #     "https://www.upwork.com/freelancers/api/v1/profile/me/completeness/pci-details",
        #     "https://www.upwork.com/freelancers/api/v1/profile/me/fwh",
        #     "https://www.upwork.com/freelancers/api/v1/profile/me/pib/status",
        # ]

        if response.request.url == "https://www.upwork.com/freelancers/api/v1/profile/me/fwh":
            nonlocal profile_fwh
            profile_fwh = response.json()

        if response.request.url == "https://www.upwork.com/freelancers/api/v1/profile/me/pib/status":
            nonlocal profile_pib_status
            profile_pib_status = response.json()

        # if response.request.url in urls:
        #     ic(response.request.url)
        #     ic(response.json())
        # ic(response.text())

    page.on("requestfinished", on_main_portal_page_load)
    page.on("response", get_targeted_resp)

    # 1. Navigate to Upwork login page
    page.goto("https://www.upwork.com/ab/account-security/login")

    # 2. Accept cookies popup
    page.get_by_role("button", name="Accept All", exact=True).click()
    # ... OR reject ookies popup
    # page.locator("//button[contains(@class, 'onetrust-close-btn-handler')]").click()
    # page.get_by_label("Close").click()

    # 3. Enter email
    page.get_by_placeholder("Username or Email").fill(EMAIL)
    page.get_by_role("button", name="Continue with Email").click()

    # 4. Enter password
    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Log in").click()

    # 5. [OPTIONAL] Enter security answer
    try:
        page.get_by_placeholder("Your Answer").fill(value=SECRET_ANSWER, timeout=TIMEOUT_IN_MS)
        page.get_by_role("button", name="Continue").click()
    except PlaywrightTimeoutError:
        logger.debug("'Security question' step was not displayed")
        # ic(exc)
        pass
    except Error as exc:
        # Happens before fill(...) timeout.
        logger.error(exc)
        ic(f"Page terminated abnormally.\nMessage: {exc.message} \nName: {exc.name} \nStack: {exc.stack}")

    # [OPTIONAL]
    # TODO: handle case for Backup 1, Rachel Worker - when Upwork sends an email with a 6-digit code
    # and user need to enter it manually. After that user need to reset security question
    # -> log this case in file / send notification to Scanner Engineering squad
    try:
        locator = page.get_by_placeholder("Enter 6-digit code")
        expect(locator).to_be_visible(timeout=TIMEOUT_IN_MS)
        """
        AssertionError: Locator expected to be visible
        Actual value: None
        Call log:
        LocatorAssertions.to_be_visible with timeout 5000ms
        waiting for get_by_role("button", name="Accept All")
        """

        logger.warning(f"Username {EMAIL} needs to enter 6-digit code")

        page.pause()
        """
        NB: There are 2 ways to solve this problem:
        1.Manually (quick but time consuming). We ask account owner to check its email and give us the code (1h deadline).
            We press 'Resume' button in the page overlay or call playwright.resume() in the DevTools console.
        2.Automation (long to do for the first time but quick to re-use).
            2.1. via API - call API of email provider and get the code (REST/IMAP protocol)
            2.2. via UI - get code from inbox as User would do it (HTML):
        Create separate context, login to User email, find specific and newest inbox email, parse and grab the code:
        email_context = browser.new_context()
        email_page = email_context.new_page()
        email_page.goto("...")
        SECRET_6_DIGIT_CODE = email_page.locator('#my-element-with-code').text_content()
        locator.fill(SECRET_6_DIGIT_CODE, timeout=TIMEOUT_IN_MS)
        page.get_by_role("button", name="Continue").click()
        """
    except Error as exc:
        logger.error(exc)
        ic(f"Page terminated abnormally.\nMessage: {exc.message} \nName: {exc.name} \nStack: {exc.stack}")
    except AssertionError:
        logger.debug("'Entering 6-digit code' step was not displayed")
        # ic(exc)
        pass

    # On successful login we should be redirected to:
    # page.goto("https://www.upwork.com/nx/find-work/")
    # page.goto("https://www.upwork.com/nx/find-work/best-matches")

    # 6. [OPTIONAL] Close modal about completing profile to 100%
    try:
        page.locator("xpath=//div[@role='dialog']//button[contains(text(),'Close')]").click(timeout=TIMEOUT_IN_MS)
    except PlaywrightTimeoutError:
        logger.debug("'Complete your profile to 100%' popup was not displayed")
        pass

    # [x] 100% Task Level 1 - https://www.upwork.com/nx/find-work/best-matches
    # 1. Collect data 'manually' by clicking on interesting elements        -> dump into .json file
    # page.pause()
    # 2. Parse HTML page with BeautifulSoup / Parcel                        -> dump into .json file
    # 3. [x] Wait for/listen for specified API requests and grab JSON responses -> dump into .json file
    # page.pause()

    profile_data_level_1 = {
        "identity": profile_fwh.get("identity"),
        "personUid": profile_fwh.get("personUid"),
        "name": profile_fwh.get("name"),
        "picture_url": profile_fwh.get("portrait").get("smallPortrait"),
        "title": profile_fwh.get("title"),
        "availability": profile_fwh.get("availability"),
        "employment_type": profile_fwh.get("availability").get("capacity"),
        "offers": profile_fwh.get("offers"),
        "skills": profile_fwh.get("skills"),
        "jobCategories": profile_fwh.get("jobCategories"),
        "interviews": profile_fwh.get("interviews"),
        "activeProposals": profile_fwh.get("activeProposals"),
        "contractToHire": profile_fwh.get("contractToHire"),
        "visibility": profile_fwh.get("visibility"),
        "locked": profile_fwh.get("locked"),
    }

    with open(TASK_LEVEL_1_RESULTS, "w") as f:
        json.dump(profile_data_level_1, f)

    # [ ] WIP Task Level 2 - https://www.upwork.com/freelancers/settings/contactInfo
    # 1. Navigate to freelancer settings profile
    # page.goto("https://www.upwork.com/freelancers/settings/profile")

    # [ ] WIP Task Level 3 - Handle possible errors, add retry if the scanning fails.
    # def retry_failed_requests(page, max_retries=3):
    #     for _ in range(max_retries):
    #         try:
    #             with page.expect_request("**/*") as request_info:
    #                 page.goto("https://example.com")
    #                 request_info.response()
    #             return
    #         except Exception as exc:
    #             logger.debug(f"One by one retry: {exc}")
    #             pass
    #     raise Exception(f"Failed to load page after {max_retries} retries")

    # retry_failed_requests(page)

    # ---------------------
    # Gracefully close up everything
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
