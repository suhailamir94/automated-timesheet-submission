
import email
import imaplib
import time
import os

import requests
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput.mouse import Controller as mouseController
from pynput.keyboard import Controller as keybordController

mouse = mouseController()
keyboard = keybordController()

PAYODA_USERNAME = os.getenv('PAYODA_USERNAME')
EMAIL_ACCOUNT = PAYODA_USERNAME+"@payoda.com"
EMAIL_PASSWORD = os.getenv('PAYODA_GMAIL_PASSWORD')
PAYODA_LDAP_PASSWORD = os.getenv('PAYODA_LDAP_PASSWORD')
PAYODA_GMAIL_PASSWORD = os.getenv('PAYODA_GMAIL_PASSWORD')
EAGLE_EYE_URL = os.getenv('EAGLE_EYE_URL')
ARISTA_GITLAB_URL = os.getenv('ARISTA_GITLAB_URL')
ARISTA_VPN_ICON_LOCATION = (1185.953125, 13.1953125)
ARISTA_VPN__DISABLE_OPTION_MENU_LOCATION = (1284.578125, 58.75) #(1290.359375, 57.42578125)
ARISTA_VPN__DISABLE_OPTION_LOCATION =  (1364.5234375, 153.80859375)
PAYODA_VPN_ICON_LOCATION = (1209.94921875, 7.8984375) #(1203.34765625, 12.015625)
PAYODA_VPN_ICON_CONNECT_LOCATION = (1231.8828125, 66.625)



class Mailbox:
    def __init__(
        self, server="imap.gmail.com", username=EMAIL_ACCOUNT, password=EMAIL_PASSWORD
    ):
        self.server = server
        self.username = username
        self.password = password
        self.login()

    def login(self):
        '''Login to payoda gmail'''

        self.mailbox = imaplib.IMAP4_SSL(self.server)
        rc, data = self.mailbox.login(self.username, self.password)

    def logout(self):
        '''logout from payoda gmail'''
        try:
            self.mailbox.close()
        except:
            pass
        self.mailbox.logout()

    def find_forticlient_auth_code(self, folder="INBOX"):
        '''get new forticlient token'''

        rv, data = self.mailbox.select(folder)
        if rv == "OK":
            rv, data = self.mailbox.search(None, "UNSEEN", "SUBJECT", '"AuthCode"')
            print(len(data))
            if rv == "OK" and data[0]:
                num = data[0].split()[-1]
                rv, data = self.mailbox.fetch(num, "(RFC822)")
                if rv == "OK":
                    msg = email.message_from_bytes(data[0][1])
                    subject = str(msg["Subject"])
                    print(f"Subject: {subject}")
                    code = subject.strip().split()[-1]
                    print(f"code: {code}")
                    return code
                else:
                    print("fetch failed!")
            else:
                print("No new authcode found!")
        else:
            print("select INBOX  failed!")
        self.logout()


def check_if_connected_to_vpn(url):
    '''check if connected to arista or payoda vpn'''

    try:
        request = requests.get(url,timeout=10)
        if request.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False


def disconnect_arista_vpn():
    '''Disconnect from Arista VPN'''
    try:
        mouse.position = ARISTA_VPN_ICON_LOCATION  # (1203.34765625, 12.015625)
        time.sleep(1)
        mouse.click(Button.left, 1)
        mouse.position = ARISTA_VPN__DISABLE_OPTION_MENU_LOCATION
        time.sleep(3)
        mouse.click(Button.left, 1)
        mouse.position = ARISTA_VPN__DISABLE_OPTION_LOCATION
        time.sleep(1)
        mouse.click(Button.left, 1)
        time.sleep(1)
        mouse.click(Button.left, 1)
        time.sleep(3)
        return not check_if_connected_to_vpn(ARISTA_GITLAB_URL)
    except Exception as e:
        return False


def connect_to_payoda_vpn():
    '''Connect to Payoda VPN'''

    try:
        mouse.position = PAYODA_VPN_ICON_LOCATION
        time.sleep(1)
        mouse.click(Button.left, 1)
        time.sleep(1)
        mouse.position = PAYODA_VPN_ICON_CONNECT_LOCATION
        time.sleep(1)
        mouse.click(Button.right, 1)
        time.sleep(2)
        keyboard.type(PAYODA_USERNAME)
        keyboard.press(Key.tab)
        keyboard.type(PAYODA_LDAP_PASSWORD)
        keyboard.press(Key.enter)
        time.sleep(10)
        mailboxobj = Mailbox()
        keyboard.type(mailboxobj.find_forticlient_auth_code())
        keyboard.press(Key.enter)
        time.sleep(30)
        return check_if_connected_to_vpn(EAGLE_EYE_URL)
    except Exception as e:
        return False


def main():
    """Script Starting point"""
    
    arista_connect = True
    payoda_connect = False

    print('Checking if already connected to Payoda....')
    if not check_if_connected_to_vpn(EAGLE_EYE_URL):
        print('Not Connected to Payoda!')
        print('Checking if connected to Arista....')
        connected_to_arista = check_if_connected_to_vpn(ARISTA_GITLAB_URL)
        if connected_to_arista:
            print('Disconnecting from Arista VPN......')
            if disconnect_arista_vpn():
                print("Disconnected from Arista VPN!")
                arista_connect = False
            else:
                print("Disconnecting from Arista VPN Failed!")
        else:
            arista_connect = False

        if not arista_connect: 
            print('Connecting to Payoda VPN......')
            connected_to_payoda = connect_to_payoda_vpn()
            if connected_to_payoda:
                print('Connected to Payoda VPN!')
                payoda_connect = True
            else:
                print('Connecting to Payoda VPN Failed!')
                payoda_connect = False
    else:
        print('Already Connected to Payoda VPN!')
        payoda_connect = True
    return payoda_connect


if __name__ == "__main__":
    main()
