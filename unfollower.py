from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

driver: webdriver.Chrome = None


def init_driver():
    global driver

    options = Options()

    options.add_argument("--mute-audio")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.set_capability('unhandledPromptBehavior', 'dismiss')

    # Page load strategy none doesn't wait for the page to fully load before continuing
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    driver = uc.Chrome(chrome_options=options, desired_capabilities=caps)


def wait_until_found(sel, timeout, multiple=False, display=True):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        try:
            WebDriverWait(driver, timeout).until(element_present)
        except AttributeError:
            return None

        if multiple:
            return driver.find_elements(By.CSS_SELECTOR, sel)
        return driver.find_element(By.CSS_SELECTOR, sel)
    except exceptions.TimeoutException:
        if display:
            print(f"Timeout waiting for element. ({sel})")
        return None


def main():
    init_driver()

    driver.get("https://www.twitch.tv/directory/following/channels")

    input("Press Enter when logged in")

    cnt = 0
    while 1:
        user_cards = wait_until_found(".channel-follow-listing--card", 30, multiple=True)
        if user_cards is None or len(user_cards) == 0:
            break
        user_card = user_cards[0]

        user_detail_card = user_card.find_element(By.CSS_SELECTOR, "div>.user-card")
        username = user_detail_card.find_element(By.CSS_SELECTOR, ".info>a").get_attribute("aria-label")
        unfollow_button = user_detail_card.find_element(By.CSS_SELECTOR, "button[data-a-target='unfollow-button']")

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
