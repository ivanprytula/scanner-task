import json

from decouple import config
from icecream import ic
from loguru import logger
from playwright.sync_api import Error, Playwright, expect, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from scanner.constants import RESULTS_DIR_NAME, TIMEOUT_IN_MS
from scanner.helpers import (
    convert_iso_to_date_string,
    create_directory_with_file,
    get_pay_cycle,
)
from scanner.models import create_identity

# Target User/Identity credentials
USERNAME = config("IDENTITY_USERNAME")
EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD", default="password not provided")
SECRET_ANSWER = config("SECRET_ANSWER", default="answer not provided")
PORTAL_LINK = config("PORTAL_LINK", default="https://www.upwork.com/ab/account-security/login")

task_level_1_file_name = f"{EMAIL}_task_level_1.json"
task_level_2_file_name = f"{EMAIL}_task_level_2.json"

AUTH_ENDPOINTS = {
    "oauth2": "https://auth.upwork.com/api/v3/oauth2/token/subordinate/v3/",
}

UPWORK_API_V1 = {
    "graphql_main": "https://www.upwork.com/graphql/v1",
    "profile_me_fwh": "https://www.upwork.com/freelancers/api/v1/profile/me/fwh",
    "pci_details": "https://www.upwork.com/freelancers/api/v1/profile/me/completeness/pci-details",
    "projects_summary": "https://www.upwork.com/ab/find-work/api/catalog/projects-summary",
    "get_ad_unified": "https://www.upwork.com/ab/plans/api/get-ad-unified",
    "gold_track_eligible": "https://www.upwork.com/freelancers/settings/api/v2/gold-track/eligible",
    "send_otp": "https://www.upwork.com/ab/account-security/api/device-authorization/send-otp",
    "custom_url": "https://www.upwork.com/freelancers/settings/api/v1/profile/~01b5ffe1df46c24d0e/custom-url",
    "pib_status": "https://www.upwork.com/freelancers/api/v1/profile/me/pib/status",
    "pib_status_owner": "https://www.upwork.com/freelancers/api/v1/profile/me/pib/status/owner",
    "catalog_state": "https://www.upwork.com/freelancers/api/v1/talent_nudges/catalog/state",
    "contact_info": "https://www.upwork.com/freelancers/settings/api/v1/contactInfo",
    "profile_settings": "https://www.upwork.com/freelancers/settings/api/v1/profile-settings",
    "profile_get_phone": "https://www.upwork.com/freelancers/settings/api/v1/profile/get/phone",
    "disbursement_methods": "https://www.upwork.com/ab/payments/api/{organization_id}/disbursement-methods",
    "tax_info_status": "https://www.upwork.com/ab/payments/api/{organization_id}/tax-info/status/v2",
    "tax_info_billing_address": "https://www.upwork.com/ab/payments/api/{organization_id}/tax-info/billing-address",
    "messages": "https://www.upwork.com/ab/payments/api/{organization_id}/messages",
    "payments_deposit_methods": "https://www.upwork.com/ab/payments/api/{organization_id}/deposit-methods/page-data",
    "upi_metrics": "https://www.upwork.com/upi/metrics/rum/v1",
}

BASE_URL = "https://www.upwork.com"

SETTINGS_URLS = {
    "billingMethods": f"{BASE_URL}/nx/payments/deposit-methods",
    "membership": f"{BASE_URL}/nx/plans/membership/index",
    "contact": f"{BASE_URL}/freelancers/settings/contactInfo",
    "taxInfo": f"{BASE_URL}/nx/tax",
    "taxInfoHistory": f"{BASE_URL}/nx/tax/tax-info-history",
    "userProfile": f"{BASE_URL}/freelancers/~01c093b1daf1b5c98f",
    "profileSettings": f"{BASE_URL}/freelancers/settings/profile",
    "withdrawalMethods": f"{BASE_URL}/nx/payments/disbursement-methods",
    "linked": f"{BASE_URL}/nx/connected-services/",
    "passwordSecurity": f"{BASE_URL}/ab/account-security/password-and-security",
    "notifications": f"{BASE_URL}/ab/notification-settings/",
}


def run(playwright: Playwright) -> None:
    # 0. Setup browser. Make sure to run headed.
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Create a new page in a pristine context
    page = context.new_page()

    profile_fwh_details = {}
    completeness_pci_details = {}

    def get_targeted_resp(response):
        if response.request.url == UPWORK_API_V1["profile_me_fwh"]:
            nonlocal profile_fwh_details
            profile_fwh_details = response.json()

        if response.request.url == UPWORK_API_V1["pci_details"]:
            nonlocal completeness_pci_details
            completeness_pci_details = response.json()

    page.on("response", get_targeted_resp)

    # 1. Navigate to Upwork login page
    page.goto(PORTAL_LINK)

    # 2. Accept cookies popup
    page.get_by_role("button", name="Accept All", exact=True).click()
    # OR reject cookies popup in quick way, "x" mark on top right:
    #   Option 1: page.get_by_role("button", name="Close")
    #   Option 2: page.locator("//button[contains(@class, 'onetrust-close-btn-handler')]").click()
    # OR customize if specific business case is needed:
    # page.get_by_label("Privacy Preference Center").get_by_label("Close").click()
    # page.get_by_role("button", name="Customize")
    # page.get_by_role("button", name="Allow All") | # page.get_by_role("button", name="Reject All")

    # 3. Enter email
    page.get_by_placeholder("Username or Email").fill(EMAIL)
    page.get_by_role("button", name="Continue with Email").click()

    # 4. Enter password
    # NB: Check "Keep me logged in" to enable persistent session.
    # This will potentially help to avoid device reauthentication later on
    page.locator('[data-test="checkbox-input"]').set_checked(True)

    page.get_by_role("textbox", name="Password").fill(PASSWORD)
    page.get_by_role("button", name="Log in").click()

    # 5. [OPTIONAL] Enter security answer
    try:
        page.get_by_placeholder("Your Answer").fill(value=SECRET_ANSWER, timeout=TIMEOUT_IN_MS)
        page.get_by_role("button", name="Continue").click()
    except PlaywrightTimeoutError:
        logger.debug("'Security question' step was not displayed")
        pass
    except Error as exc:
        logger.error(exc)
        ic(f"Page terminated abnormally.\n{exc.message}, {exc.name}, {exc.stack}")

    # [OPTIONAL TODO]: handle case for Backup 1, Rachel Worker - when Upwork sends an email with a 6-digit code
    # and user need to enter it manually. After that user needs to reset security question
    # -> log this case in file / send notification to Scanner Engineering squad
    try:
        locator = page.get_by_placeholder("Enter 6-digit code")
        expect(locator).to_be_visible(timeout=TIMEOUT_IN_MS)

        logger.warning(f"Username {EMAIL} needs to enter 6-digit code")

        page.pause()
        """
        NB: There are 2 ways to solve this problem:
        1.Manually (quick but time consuming). We ask account owner to check its email and give us the code (1h deadline).
            We press 'Resume' button in the page overlay or call playwright.resume() in the DevTools console.
        2.Automation (long to do for the first time but quick to re-use).
            2.1. via API - call API of email provider and get the code (REST/IMAP protocol)
            2.2. via UI - get code from inbox as User would do it (HTML):
        Create separate context, login to User email, find specific and newest inbox email, parse and grab the code.
        """
    except Error as exc:
        logger.error(exc)
        ic(f"Page terminated abnormally.\n{exc.message}, {exc.name}, {exc.stack}")
    except AssertionError:
        logger.debug("'Entering 6-digit code' step was not displayed")
        pass

    # On successful login we should be redirected to https://www.upwork.com/nx/find-work/best-matches

    # 6. [OPTIONAL] Close modal about "completing profile to 100%"
    try:
        page.locator("xpath=//div[@role='dialog']//button[contains(text(),'Close')]").click(timeout=TIMEOUT_IN_MS)
    except PlaywrightTimeoutError:
        logger.debug("'Complete your profile to 100%' popup was not displayed")
        pass

    # ------------------- Task Level 1 -------------------
    # 1. [x] Wait for/listen for specific API requests and grab JSON responses -> dump into .json file
    # 2. Collect data 'manually' by clicking on interesting elements
    # 3. Parse HTML page with BeautifulSoup / Parcel

    # Alias for better readability
    fwh: dict = profile_fwh_details
    results_level_1_data_fwh = {
        "id": fwh.get("identity").get("uid") or fwh.get("personUid"),
        "job_title": fwh.get("title"),
        "picture_url": fwh.get("portrait").get("smallPortrait"),
        "metadata": {
            "recno": fwh.get("identity").get("recno"),
            "interviews": fwh.get("interviews"),
            "offers": fwh.get("offers"),
            "activeProposals": fwh.get("activeProposals"),
            "visibility": fwh.get("visibility"),
            "locked": fwh.get("locked"),
            "skills": fwh.get("skills"),
            "contractToHire": fwh.get("contractToHire"),
        },
    }

    cpci = completeness_pci_details
    results_level_1_data_cpci = {
        "created_at": cpci.get("pci").get("createdTs"),
        "updated_at": cpci.get("pci").get("updatedTs"),
    }

    results_level_1_data_full = {
        **results_level_1_data_fwh,
        **results_level_1_data_cpci,
    }

    results_file_path_1 = create_directory_with_file(RESULTS_DIR_NAME, task_level_1_file_name)

    with open(results_file_path_1, "w") as f:
        json.dump(results_level_1_data_full, f)

    # ------------------- Task Level 2 -------------------

    def handle_device_reauth(page) -> None:
        try:
            expect(page.get_by_role("heading", name="Device authorization")).to_be_visible()
            # page.locator("#deviceAuth_remember").set_checked(True)
            page.get_by_text("Keep me logged in on this device").click()
            page.get_by_label("Your first pet's name").fill(SECRET_ANSWER)
            page.get_by_role("button", name="Authorize").click()
        except AssertionError:
            logger.debug("'Device authorization' step was not displayed")
            pass

    def handle_re_enter_password(page) -> None:
        try:
            expect(page.get_by_role("heading", name="Re-enter password")).to_be_visible()
            page.get_by_label("Password").fill(PASSWORD)
            page.get_by_role("button", name="Continue")
        except AssertionError:
            logger.debug("'Re-enter password' step was not displayed")
            pass

    with page.expect_response(UPWORK_API_V1["contact_info"]) as contact_info_response:
        page.goto(SETTINGS_URLS["contact"])
        # ... or via UI
        # page.get_by_role("button", name="Account Settings").click()  # top-right avatar
        # page.get_by_role("link", name="Settings", exact=True).click()  # in dropdown card

        handle_device_reauth(page)
        handle_re_enter_password(page)

    # Short alias for better readability
    ci = contact_info_response.value.json()
    results_level_2_data_ci = {
        "first_name": ci.get("freelancer").get("firstName"),
        "last_name": ci.get("freelancer").get("lastName"),
        "full_name": f"{ci.get('freelancer').get('firstName')} {ci.get('freelancer').get('lastName')}",
        "address": {
            "city": ci.get("freelancer").get("address").get("city"),
            "line1": ci.get("freelancer").get("address").get("street"),
            "line2": ci.get("freelancer").get("address").get("additionalInfo"),
            "state": ci.get("freelancer").get("address").get("state"),
            "country": ci.get("freelancer").get("address").get("country"),
            "postal_code": ci.get("freelancer").get("address").get("zip"),
        },
        "email": ci.get("freelancer").get("email").get("address"),
        # just in case, as backup for phone number we can use:
        # https://www.upwork.com/freelancers/settings/api/v1/profile/get/phone
        "phone_number": ci.get("phone"),
        "platform_ids": {
            "employee_id": ci.get("freelancer").get("rid"),
            "position_id": ci.get("freelancer").get("nid"),
            "platform_user_id": ci.get("freelancer").get("userRid"),
        },
    }

    with page.expect_response(UPWORK_API_V1["profile_settings"]) as profile_settings_response:
        page.goto(SETTINGS_URLS["profileSettings"])

    ps = profile_settings_response.value.json()
    results_level_2_data_ps = {
        "account": ps.get("profile").get("identity").get("userId"),
        "employment_type": ps.get("profile").get("availability").get("capacity").get("nid"),
        # OR: "employment_status": "inactive" if ps.profile.profile.isDisabled else "active",
        "employment_status": ("inactive" if ps.get("profile").get("stats").get("activeAssignments") > 0 else "active"),
        "hire_date": convert_iso_to_date_string(ps.get("profile").get("stats").get("lastWorkedOn")),
    }

    def get_organization_id(browser_context) -> str:
        cookies = browser_context.cookies()
        filtered_cookies = list(filter(lambda cookie: cookie["name"] == "current_organization_uid", cookies))
        return filtered_cookies[0].get("value")

    organization_id = get_organization_id(context)

    with page.expect_response(
        UPWORK_API_V1["tax_info_status"].format(organization_id=organization_id)
    ) as tax_info_response:
        page.goto(SETTINGS_URLS["taxInfo"])

    txi = tax_info_response.value.json()
    results_level_2_data_txi = {
        "birth_date": convert_iso_to_date_string(txi.get("taxInfo").get("dateOfBirth")),
        "ssn": txi.get("ssnLast4Digits"),
        "marital_status": None,
        "gender": None,
        "termination_date": None,
        "termination_reason": None,
        "employer": None,
        "base_pay": {},
    }

    with page.expect_response(
        UPWORK_API_V1["disbursement_methods"].format(organization_id=organization_id)
    ) as disbursement_methods_response:
        page.goto(SETTINGS_URLS["withdrawalMethods"])

    dm = disbursement_methods_response.value.json()
    results_level_2_data_dm = {
        "pay_cycle": get_pay_cycle(dm.get("schedule")),
    }

    results_level_2_data_full = {
        **results_level_1_data_full,
        **results_level_2_data_ci,
        **results_level_2_data_ps,
        **results_level_2_data_txi,
        **results_level_2_data_dm,
    }

    results_file_path_2 = create_directory_with_file(RESULTS_DIR_NAME, task_level_2_file_name)

    with open(results_file_path_2, "w") as f:
        json.dump(results_level_2_data_full, f)

    # Collected data which we "feed" into Pydantic model
    logger.info(results_level_2_data_full)

    # address = Address(**results_level_2_data_full["address"])

    # identity = IndentityArgyleComposite(
    #     results_level_2_data_full.get("id"),
    # )

    profile_object_lvl_2 = create_identity(**results_level_2_data_full)  # noqa

    # NOTE:
    # 1. At the moment I've created identity class as composite - with enum fields and nested dicts as separate classes.
    # This way we have full control over all fields types and values, but we must create smaller classes and combine them into identity class.
    # That's why we can see nice red logs of Pydantic validation errors - elegant way to handle missing fields and communicate it via response.
    # I explored Argyle API docs about Identity object and can say that 100% mapping of Upwork freelancer profile data to identity class
    # is out of scope for this task - many fields requires domain knowledge, e.g. there is no typical long UUID in Upwork fields comparing to "id" in Argyle object.
    # I did my best to show my understanding of Pydantic usage for data validation in short and scoped task.
    # 2. "Quick and dirty" way is to create 'flat' IdentityArgyle and dump all data as is with non-required fields, e.g. str | None.

    # [x] Task Level 3 - Handle possible errors, add retry if the scanning fails.
    # What was done:
    # 1. Login steps that have extra auth actions covered with try/catch and checks/autofill of required fields
    # 2. In order to collect data faster we visit pages but actual data we take from "catched" API responses.
    # It was was encountered many times (during regular usage) that if user stays longer than 15 minutes on one page in profile settings
    # and then go to another settings pages (e.g. taxes, disbursement methods) Upwork forces to re-enter password.
    # Data scraping takes much less than 15 min and could be enough for our purposes if we had smaller amount of fields to fill.
    # But working with JSON responses is more convenient and API responses contains much more data.

    # 3. As a suggestion/example for the future:
    # We can wrap core scanner navigation and data collection in a loop and add versioning to file names.
    # def retry_failed_requests(page, max_retries=3):
    #     for _ in range(max_retries):
    #         try:
    #             with page.expect_request("**/*") as request_info:
    #                 page.goto(""https://www.upwork.com/ab/account-security/login")
    #                 ... all logic with data collection ...
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
