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
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

LOGIN_URL = "https://www.netflix.com/login"
CHANGE_PLAN_URL = "https://www.netflix.com/ChangePlan"
ACCOUNT_URL = "https://www.netflix.com/YourAccount"

# TODO: create this folder in Dockerfile
PROFILES_DIR = "/tmp/shareflix/profiles/"


class Plan(Enum):
    BASIC = 0
    STANDARD = 1
    PREMIUM = 2


class AccountInformation:
    plan: Plan = None
    balance = 0.0
    paidUntil = None
    nextPlan: Plan = None
    planChangeDate = None


class ShareflixDriver:
    driver = None
    username = None
    password = None
    account: AccountInformation = AccountInformation()

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def profile_path(self):
        return PROFILES_DIR + base64.b64encode(self.username.encode()).decode()

    def start_webdriver(self):
        options = Options()
        # TODO: uncomment for production
        # options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1200")
        logger.info("Starting Chrome driver")
        self.driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver started")
        self.driver.implicitly_wait(3)

    def login(self):
        logger.info("Proceeding to login to {}".format(LOGIN_URL))
        # Visit login page of netflix
        self.driver.get(LOGIN_URL)

        # Enter user credentials
        user_el = self.driver.find_element(By.ID, "id_userLoginId")
        user_el.send_keys(self.username)
        pass_el = self.driver.find_element(By.ID, "id_password")
        pass_el.send_keys(self.password)

        # Wait a few seconds before logging in to avoid botlike behavior
        sleep(1)

        # Click sign-in
        signin_el = self.driver.find_element(By.XPATH, "//button[@class='btn login-button btn-submit btn-small']")
        signin_el.click()
        logger.info("Signin complete")

    def select_profile(self):
        logger.info("Selecting Profile")
        # Select first profile available
        profile = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='profile-icon']")))
        profile.click()
        logger.info("Profile selected")

    def fetch_account_information(self):
        # switch to Account page
        if self.driver.current_url.casefold() != ACCOUNT_URL.casefold():
            self.driver.get(ACCOUNT_URL)

        plan_name = self.driver.find_element(By.XPATH, '//div[@data-uia="plan-label"]/b').text
        self.account.plan = plan_name

        next_plan_items = self.driver.find_elements(By.XPATH, '//span[@id="automation-NextPlanItem"]/b')
        self.account.nextPlan = next_plan_items[0].text

        self.account.planChangeDate = next_plan_items[1].text

        self.account.balance = self.driver.find_element(By.XPATH,
                                                        '//div[@data-uia="gift-credit-content-headline"]').text

        self.account.paidUntil = self.driver.find_element(By.XPATH,
                                                          '//div[@data-uia="gift-credit-content-subhead"]').text

    def change_plan(self, plan: Plan = Plan.PREMIUM):
        logger.info("Changing plan to {}".format(plan.name))
        self.driver.get(CHANGE_PLAN_URL)
        try:
            self.driver.find_elements(By.CLASS_NAME,
                                      "stacked-large-selection-list-item")[plan.value].click()
            sleep(1)
            self.driver.find_element(By.CLASS_NAME, "save-plan-button").click()
            self.driver.find_element(By.CLASS_NAME, "modal-action-button").click()
        except (IndexError, NoSuchElementException):
            logger.info("Could not find change plan elements. Probably {} is already selected".format(plan.name))

    def quit(self):
        self.driver.quit()
        self.driver = None
