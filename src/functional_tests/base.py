from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 2

class FunctionalTest(StaticLiveServerTestCase):

  def setUp(self):
    geckodriver_path = "/snap/bin/geckodriver"
    driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
    self.browser = webdriver.Firefox(service=driver_service)
    if "TEST_SERVER" in os.environ:
      self.live_server_url = "http://" + os.environ["TEST_SERVER"]

  def tearDown(self):
    self.browser.quit()

  def wait_for_row(self, text):
    start_time = time.time()
    while True:
      try:
        table = self.browser.find_element(By.ID, 'id_list_table')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        items = [row.text for row in rows]
        self.assertIn(text, items)
        return
      except (AssertionError, WebDriverException):
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_WAIT:
          raise
        time.sleep(0.5)


