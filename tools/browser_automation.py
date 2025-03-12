from playwright.sync_api import sync_playwright

class BrowserAutomation:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def navigate(self, url):
        self.page.goto(url)

    def click(self, selector):
        self.page.click(selector)

    def type(self, selector, text):
        self.page.fill(selector, text)

    def extract_data(self, selector):
        return self.page.inner_text(selector)

    def close(self):
        self.browser.close()
        self.playwright.stop()
