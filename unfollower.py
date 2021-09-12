from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

driver: webdriver.Chrome = None


def init_driver(headless=True):
    global driver

    options = Options()

    options.add_argument("--mute-audio")

    if headless:
        options.add_argument("--headless")

        # disable image loading
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.set_capability('unhandledPromptBehavior', 'dismiss')

    # Page load strategy none doesnt wait for the page to fully load before continuing
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options, desired_capabilities=caps)


def wait_until_found(sel, timeout, multiple=False, display=True):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        try:
            WebDriverWait(driver, timeout).until(element_present)
        except AttributeError:
            return None

        if multiple:
            return driver.find_elements_by_css_selector(sel)
        return driver.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        if display:
            print(f"Timeout waiting for element. ({sel})")
        return None


def main():
    init_driver(headless=False)

    driver.get("https://www.twitch.tv/directory/following/channels")

    input("Press Enter when logged in")

    cnt = 0
    while 1:
        user_cards = wait_until_found(".channel-follow-listing--card", 30, multiple=True)
        if user_cards is None or len(user_cards) == 0:
            break
        user_card = user_cards[0]

        user_detail_card = user_card.find_element_by_css_selector("div>.user-card")
        username = user_detail_card.find_element_by_css_selector(".info>a").get_attribute("aria-label")
        unfollow_button = user_detail_card.find_element_by_css_selector("button[data-a-target='unfollow-button']")

        try:
            driver.execute_script("arguments[0].click();", unfollow_button)
        except exceptions.JavascriptException:
            continue

        confirm_unfollow_button = wait_until_found("button[data-a-target='modal-unfollow-button']", 3)
        if confirm_unfollow_button is None:
            continue

        confirm_unfollow_button.click()

        print(f"Unfollowed: {username}")

        try:
            driver.execute_script("arguments[0].remove();", user_card)
        except exceptions.JavascriptException:
            continue

        if cnt % 5 == 0:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", user_cards[-1])
            except exceptions.JavascriptException:
                continue

        cnt += 1
    pass


if __name__ == '__main__':
    main()
