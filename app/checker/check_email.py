import json
import random

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException as timeout

from pyvirtualdisplay import Display


class MailRu:
    def __init__(self, email, proxy, user_agent):
        def check(mail, p, ua):
            url = "https://account.mail.ru/api/v1/user/password/restore"
            headers = {
                            "accept": "application/json, text/javascript, */*; q=0.01",
                            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "sec-ch-ua-mobile": "?0",
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-origin",
                            "x-requested-with": "XMLHttpRequest",
                            "User-Agent": ua
                        }

            data = dict(email=mail)

            proxy_dict = {"http": f"http://username:password@{p}"}

            r = requests.post(url, headers=headers, data=data, proxies=proxy_dict).text

            response = json.loads(r)
            if response["status"] == 200:
                return True
            elif response["status"] == 400:
                return False
            else:
                return response

        self.check = check(email, proxy, user_agent)


class Yahoo:
    def __init__(self, email, proxy, user_agent):
        def create_proxyauth_extension(
                proxy_host,
                proxy_port,
                proxy_username,
                proxy_password,
                scheme="http",
                plugin_path=None,
        ):
            import string
            import zipfile

            if plugin_path is None:
                plugin_path = "/tmp/vimm_chrome_proxyauth_plugin.zip"

            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

            background_js = string.Template(
                """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com"]
                    }
                  };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """
            ).substitute(
                host=proxy_host,
                port=proxy_port,
                username=proxy_username,
                password=proxy_password,
                scheme=scheme,
            )
            with zipfile.ZipFile(plugin_path, "w") as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)

            return plugin_path

        def random_size():
            width = random.randint(1200, 1920)
            height = width // 1.5

            return dict(width=width, height=height)

        def accept_cookies():
            try:
                accept_btn = WebDriverWait(browser, 1).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "primary"))
                )
                accept_btn.click()
                return True
            except timeout:
                return False

        def move_to_restore_page():
            try:
                forgot_link = WebDriverWait(browser, 5).until(
                    ec.presence_of_element_located((By.ID, "mbr-forgot-link"))
                )
            except timeout:
                with open("./forgot_login_link_debug.txt", "w+") as text_file:
                    text_file.write(
                        browser.find_element_by_tag_name("html").get_attribute("innerHTML")
                    )
                browser.save_screenshot("forgot_login_link.png")
                print(
                    "FAILURE! Can't locate element! Check forgot_login_link_debug.txt and screenshot!"
                )
                return False

            forgot_link.click()
            return True

        def check_email(mail):
            try:
                input_field = WebDriverWait(browser, 5).until(
                    ec.presence_of_element_located((By.ID, "username"))
                )
            except timeout:
                with open("./input_field_debug.txt", "w+") as text_file:
                    text_file.write(
                        browser.find_element_by_tag_name("html").get_attribute("innerHTML")
                    )
                browser.save_screenshot("input_field.png")
                return "FAILURE! Can't locate email input field! Check input_field_debug.txt and screenshot!"

            input_field.send_keys(mail)
            input_field.send_keys(Keys.ENTER)
            try:
                WebDriverWait(browser, 1).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "error-msg"))
                )
                return False
            except timeout:
                return True

        proxy_string = proxy
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxy_string.split(":", 1)[0],
            proxy_port=proxy_string.split(":", 1)[1],
            proxy_username="",
            proxy_password="",
        )

        display = Display(visible=False)
        display.start()
        window = random_size()
        options = Options()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_extension(proxyauth_plugin_path)
        browser = webdriver.Chrome(executable_path="webdriver/chromedriver", options=options)
        browser.set_window_size(width=window["width"], height=window["height"])

        browser.get("https://yahoo.com/login")
        # accept_cookies()  # Закомментировать, если используем русские прокси.
        if move_to_restore_page() is True:
            result = check_email(email.replace("@yahoo.com", ""))
        else:
            result = "Error while opening restore account page!"
        browser.quit()
        display.stop()
        self.check = result
