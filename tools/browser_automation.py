from playwright.sync_api import sync_playwright

class BrowserAutomation:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()
        self.sessions = {}

    def navigate(self, url):
        self.page.goto(url)

    def click(self, selector):
        self.page.click(selector)

    def type(self, selector, text):
        self.page.fill(selector, text)

    def extract_data(self, selector):
        return self.page.inner_text(selector)

    def start_session(self, session_name):
        if session_name not in self.sessions:
            self.sessions[session_name] = self.browser.new_context()
        return self.sessions[session_name]

    def switch_session(self, session_name):
        if session_name in self.sessions:
            self.page = self.sessions[session_name].new_page()

    def close_session(self, session_name):
        if session_name in self.sessions:
            self.sessions[session_name].close()
            del self.sessions[session_name]

    def close(self):
        self.browser.close()
        self.playwright.stop()
