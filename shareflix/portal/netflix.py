import base64
import os
from datetime import datetime
from sys import exit, stdout
from time import sleep
from enum import Enum
import logging

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

LOGIN_URL = "https://www.netflix.com/login"
CHANGE_PLAN_URL = "https://www.netflix.com/ChangePlan"
ACCOUNT_URL = "https://www.netflix.com/YourAccount"

PROFILES_DIR = "/tmp/shareflix/profiles/"

def profile_path(username):
    return PROFILES_DIR + base64.b64encode(username.encode()).hex()

class Plan(Enum):
    BASIC = 0
    STANDARD = 1
    PREMIUM = 2

class Netflix:
    driver = None

    def __init__(self, debug=False, profile_dir=None):
        options = Options()
        # if not debug:
        #options.add_argument('--headless')
        if profile_dir:
            options.add_argument(f"--user-data-dir={profile_dir}")
        #options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1200")
        logger.info("starting Chrome driver")
        if debug:
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
        logger.info("chrome driver started")
        self.driver.implicitly_wait(3)

    def login(self, username, password):
        logger.info("proceeding to login to {}".format(LOGIN_URL))
        # Visit login page of netflix
        self.driver.get(LOGIN_URL)
        if self.driver.current_url.casefold().endswith("/browse"):
            logger.info("already logged in")
        else:
            logger.info("loggin in with user %s", username)
            # Enter user credentials
            user_el = self.driver.find_element(By.ID, "id_userLoginId")
            user_el.send_keys(username)
            pass_el = self.driver.find_element(By.ID, "id_password")
            pass_el.send_keys(password)

            # Wait a few seconds before logging in to avoid botlike behavior
            sleep(1)

            # Click sign-in
            signin_el = self.driver.find_element(By.XPATH, "//button[@class='btn login-button btn-submit btn-small']")
            signin_el.click()

        self._select_profile()

    def _select_profile(self):

        def is_main_view():
            try:
                self.driver.find_element(By.XPATH, '//*[@id="main-view"]')
            except NoSuchElementException:
                return False
            return True

        if is_main_view():
            logger.info("already in main view")
            return

        logger.info("Selecting Profile")
        # Select first profile available
        profile = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='profile-icon']")))
        profile.click()
        logger.info("Profile selected")

    def account_information(self):
        # switch to Account page
        if self.driver.current_url.casefold() != ACCOUNT_URL.casefold():
            self.driver.get(ACCOUNT_URL)

        plan_name = self.driver.find_element(By.XPATH, '//div[@data-uia="plan-label"]/b').text
        next_plan_items = self.driver.find_elements(By.XPATH, '//span[@id="automation-NextPlanItem"]/b')

        next_plan = next_plan_items[0].text
        next_plan_change = next_plan_items[1].text

        balance = self.driver.find_element(By.XPATH,
                                                        '//div[@data-uia="gift-credit-content-headline"]').text

        paid_until = self.driver.find_element(By.XPATH,
                                                          '//div[@data-uia="gift-credit-content-subhead"]').text

        return {
                'plan_name': plan_name,
                'next_plan': next_plan,
                'next_plan_change': next_plan_change,
                'balance': balance,
                'paid_until': paid_until
                }

    def change_plan(self, plan: Plan = Plan.PREMIUM):
        logger.info("Changing plan to {}".format(plan.name))
        if self.driver.current_url.casefold() != CHANGE_PLAN_URL.casefold():
            self.driver.get(CHANGE_PLAN_URL)

        choose_plan = self.driver.find_element(By.CLASS_NAME, "choose-plan")
        sleep(1)
        plan_label = choose_plan.find_elements(By.TAG_NAME, "label")[plan.value]

        if "choose-plan__plan--checked" in plan_label.get_attribute("class"):
            logger.info("plan %s is already selected", plan.name)
            self.driver.find_element(By.CLASS_NAME, "cancel-save-button").click()
        else:
            plan_label.click()
            logger.info("selected plan %s", plan.name)
            self.driver.find_element(By.CLASS_NAME, "save-plan-button").click()
            self.driver.find_element(By.CLASS_NAME, "modal-action-button").click()

    def quit(self):
        self.driver.quit()
        self.driver = None
