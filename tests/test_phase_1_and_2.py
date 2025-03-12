import os
import sys
import unittest
import asyncio
import logging
from playwright.async_api import async_playwright
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.data_processing import DataProcessing
from tools.api_connectors import APIConnectors

logging.basicConfig(level=logging.INFO)

class TestPhase1And2(unittest.TestCase):

    def setUp(self):
        self.data_processing = DataProcessing()
        self.api_connectors = APIConnectors()

    def tearDown(self):
        pass

    async def async_setUp(self):
        logging.info("Starting Playwright")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.page = await self.browser.new_page()

    async def async_tearDown(self):
        logging.info("Stopping Playwright")
        await self.browser.close()
        await self.playwright.stop()

    async def test_browser_automation(self):
        logging.info("Navigating to http://example.com")
        await self.page.goto('http://example.com')
        logging.info("Clicking selector")
        await self.page.wait_for_selector('selector')
await self.page.click('selector')
        logging.info("Filling selector with text")
        await self.page.fill('selector', 'text')
        logging.info("Extracting data from selector")
        data = await self.page.inner_text('selector')
        self.assertIn('text', data)

    def test_data_processing(self):
        logging.info("Testing data processing")
        csv_data = self.data_processing.parse_csv('/path/to/csvfile.csv')
        self.assertIsNotNone(csv_data)

        excel_data = self.data_processing.parse_excel('/path/to/excelfile.xlsx')
        self.assertIsNotNone(excel_data)

        pdf_text = self.data_processing.extract_pdf_text('/path/to/pdffile.pdf')
        self.assertIsNotNone(pdf_text)

        nlp_result = self.data_processing.basic_nlp('This is a sample text.')
        self.assertIsNotNone(nlp_result)

    def test_api_connectors(self):
        logging.info("Testing API connectors")
        response = self.api_connectors.generic_rest_client('http://example.com/api')
        self.assertEqual(response['status'], 'success')

        github = self.api_connectors.github_connector('your_github_token')
        self.assertIsNotNone(github)

        google = self.api_connectors.google_connector('youtube', 'v3', 'your_developer_key')
        self.assertIsNotNone(google)

        schema = self.api_connectors.infer_schema('http://example.com/api')
        self.assertIsNotNone(schema)

    def run(self, result=None):
        asyncio.run(self._run(result))

    async def _run(self, result=None):
        await self.async_setUp()
        try:
            await self.test_browser_automation()
            self.test_data_processing()
            self.test_api_connectors()
        finally:
            await self.async_tearDown()

if __name__ == '__main__':
    unittest.main()
