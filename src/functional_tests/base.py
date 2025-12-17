from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from .container_commands import reset_database

MAX_WAIT = 2

def wait(fn):
  def modified_fn(*args, **kwargs):
    start_time = time.time()
    while True:
      try:
        return fn(*args, **kwargs)
      except (AssertionError, WebDriverException) as e:
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_WAIT:
          raise e
        time.sleep(0.5)

  return modified_fn

class FunctionalTest(StaticLiveServerTestCase):

  def setUp(self):
    geckodriver_path = "/snap/bin/geckodriver"
    driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
    self.browser = webdriver.Firefox(service=driver_service)
    self.test_server = os.environ.get('TEST_SERVER')
    if self.test_server:
      self.live_server_url = "http://" + self.test_server
      reset_database(self.test_server)

  def tearDown(self):
    self.browser.quit()

  def get_item_input_box(self):
    return self.browser.find_element(By.ID, 'id-text')
  
  @wait
  def wait_for(self, fn):
    return fn()

  @wait
  def wait_for_row(self, row_text):
    rows = self.browser.find_elements(By.CSS_SELECTOR, '#id_list_table tr')
    items = [row.text for row in rows]
    self.assertIn(row_text, items)

  @wait
  def wait_to_be_logged_in(self, email):
    self.browser.find_element(By.CSS_SELECTOR, '#id-logout')
    navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
    self.assertIn(email, navbar.text)

  @wait
  def wait_to_be_logged_out(self, email):
    self.browser.find_element(By.CSS_SELECTOR, 'input[name=email]')
    navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
    self.assertNotIn(email, navbar.text)


