import datetime
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from forticlient import main as connect_to_vpn

EAGLE_EYE_URL = os.getenv("EAGLE_EYE_URL")
PAYODA_USERNAME = os.getenv("PAYODA_USERNAME")
PAYODA_LDAP_PASSWORD = os.getenv("PAYODA_LDAP_PASSWORD")


class EagleEye:
    def __init__(self, browser):
        self.browser = browser

    def login_and_navigate_to_timesheet_page(self):
        """Login to eagle eye and navigate to the create new timesheet page"""

        print("Loading Eagle Eye......")
        self.browser.get(EAGLE_EYE_URL + "/login")
        print("Eagle Eye Loaded")

        elem_username = self.browser.find_element_by_id("username")
        elem_password = self.browser.find_element_by_id("password")
        elem_username.clear()
        elem_password.clear()
        elem_username.send_keys(PAYODA_USERNAME)
        elem_password.send_keys(PAYODA_LDAP_PASSWORD)
        elem_username.send_keys(Keys.RETURN)
        print("Logged in to eagle-eye!")

        link_timesheet = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Timesheet"))
        )
        link_timesheet.click()
        print("On Timesheet Page!")
        link_new_timesheet = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "New Timesheet"))
        )

        link_new_timesheet.click()
        print("On Create Timesheet Page!")
        elem_start_date = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "startday"))
        )

        elem_start_date.clear()
        elem_start_date.send_keys(findLastSundayDate())
        self.browser.find_element_by_id("wktime_add").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "issueTable"))
        )

    def update_and_submit_timesheet_table(self):
        """update and submit the timesheet table"""
        print("Updating Timesheet!")
        for td in range(10, 15):
            elem = self.browser.find_element_by_xpath(
                f"/html/body/div[1]/div/div[1]/div[3]/div[2]/form/div[3]/table/tbody/tr/td[{td}]/input[1]"
            )
            elem.send_keys("8")
            elem.send_keys(Keys.TAB)
        self.browser.find_element_by_id("wktime_submit").click()

        WebDriverWait(self.browser, 3).until(
            EC.alert_is_present(), "Timed out waiting for confirmation popup to appear."
        )

        # fully submit the timesheet
        alert = self.browser.switch_to.alert
        alert.accept()

        # To just save the new timesheet
        # elem.send_keys(Keys.RETURN)

    def check_if_timesheet_is_submitted(self):
        """check if the timesheet we just added was submitted"""
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "New Timesheet"))
            )
            print("Timesheet Submission Succesfull!")
        except Exception as e:
            print("Timesheet Submission not Succesfull!")


def findLastSundayDate():
    """find last sunday date , this is not needed but just for its fun"""

    today = datetime.date.today()
    sun = today - datetime.timedelta(today.weekday() + 1)
    return "{:%Y-%m-%d}".format(sun)


if __name__ == "__main__":

    if connect_to_vpn():
        try:
            # # healdess firefox configuration
            # firefox_options = Options()
            # firefox_options.headless = True
            # browser = webdriver.Firefox(options=firefox_options)

            # uncomment below line and comment above 3 lines to run using firfox UI
            browser = webdriver.Firefox()
            eagle_eye = EagleEye(browser)
            eagle_eye.login_and_navigate_to_timesheet_page()
            eagle_eye.update_and_submit_timesheet_table()
            eagle_eye.check_if_timesheet_is_submitted()

        finally:
            try:
                browser.quit()
                # pass
            except Exception as e:
                print(e)
