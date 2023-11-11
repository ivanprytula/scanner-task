from bs4 import BeautifulSoup
from icecream import ic
from playwright.sync_api import Playwright, sync_playwright
from selectolax.lexbor import LexborHTMLParser

# Quick config for console and file logging
# config = {
#     "handlers": [
#         {"sink": sys.stderr, "format": "{time} - {level} - {message}"},
#         {"sink": "scanner.log", "serialize": True},
#     ],
#     # "extra": {"user": "someone"},
# }
# logger.configure(**config)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # def log_and_continue_request(route, request):
    #     ic(request.url, request.method, request.redirected_from)
    #     route.continue_()
    # # Log and continue all network requests
    # context.route("**/*", log_and_continue_request)

    # Subscribe to "request" and "response" events.
    # def print_request_sent(request):
    #     ic(dir(request.response().status))
    # if request.url == "https://demo.playwright.dev/todomvc/js/director.js":
    # if request.url == "https://demo.playwright.dev/todomvc/js/director.js":
    # logger.debug(request.url)
    # logger.info(request.url)
    # logger.warning(request.url)
    # logger.error(request.url)
    # logger.exception(request.url)
    # logger.critical('NOOOOOOO!!')

    def on_main_portal_page_load(response):
        # if response.request.url == "https://demo.playwright.dev/todomvc/" and response.request.header_value("content-type") == "text/html":
        if response.request.url == "https://demo.playwright.dev/todomvc/" and response.header_value(
            "content-type"
        ).startswith("text/html"):
            soup = BeautifulSoup(response.body(), "lxml")
            selectolax_parser = LexborHTMLParser(html=response.text())

            ic(soup.title.string)

            if title_node := selectolax_parser.css_first("title"):
                ic(title_node.text())

            # ic(response.request)
            # ic(response.all_headers())
            # ic(response.json())
            # ic(response.text())

    # page.on("request", print_request_sent)
    # page.on("requestfinished", print_request_sent)
    page.on("response", on_main_portal_page_load)

    page.goto("https://demo.playwright.dev/todomvc")

    # page.pause()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
