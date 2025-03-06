import os
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from webdriver_manager.chrome import ChromeDriverManager


SLACK_TOKEN = os.getenv("SLACK_TOkEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Set up Selenium WebDriver
def get_random_problem():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://neetcode.io/practice?tab=neetcode150")
        time.sleep(5)  # Wait for JavaScript to load the pagei

        section_buttons = driver.find_elements(By.CSS_SELECTOR, "button.accordion.button")
        for button in section_buttons:
            try:
                button.click()
                time.sleep(1)  # Small delay to allow content to load
            except:
                print("Skipping button (possibly already expanded)")

        time.sleep(2)  # Ensure all sections are expanded)

        problem_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/problems/']")
        problems = [
            {"title": el.text.strip(), "url": el.get_attribute("href")}
            for el in problem_elements if el.text.strip()
        ]

        driver.quit()

        if not problems:
            return "No problems found."

        problem = random.choice(problems)
        return f"*Today's Problem:* {problem['title']} - {problem['url']}"

    except Exception as e:
        driver.quit()
        return f"Error: {str(e)}"


problem = get_random_problem()

client = WebClient(token=SLACK_TOKEN)
try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text=problem
    )
except SlackApiError as e:
    assert e.response["error"]
