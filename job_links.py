from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time
from random import randint
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv

ua = UserAgent()
user_agent = ua.random
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome(options=options)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)
search_field = input("Enter the job title you want to search for: ")
url = f"https://www.indeed.com/jobs?q={search_field}&l="

driver.get(url)
# print("Please solve the captcha on the website and press Enter")
# input()

job_titles = []
job_links = []

min_interval = 2  # minimum interval between requests
max_requests_per_minute = 30  # request limit per minute
element_search_timeout = 10  # seconds
max_pages = 4
current_page = 1

while True:
    # check the request limit per minute

    time.sleep(randint(3, 7))  # random pause

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(randint(2, 5))

    try:
        job_elems = WebDriverWait(driver, element_search_timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".slider_item"))
        )

        for job in job_elems:
            title = job.find_element(By.TAG_NAME, "a").text
            link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
            job_titles.append(title)
            job_links.append(link)

        print("Collected", len(job_links), "links")
        print("Moving to the next page...")

        try:
            next_button = WebDriverWait(driver, element_search_timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[aria-label='Next Page']")
                )
            )
            if current_page >= max_pages:
                print("Reached max pages limit, stopping scrape")
                break

            next_button.click()

            current_page += 1

            time.sleep(randint(3, 10))
        except TimeoutException:
            print(
                "Could not find the 'Next Page' button. Please solve the captcha on the website and press Enter"
            )
            input()

    except TimeoutException:
        print(
            "Could not find elements on the page. Please solve the captcha on the website and press Enter"
        )
        input()

    # Check if we have reached the last page
    if not driver.find_element(By.CSS_SELECTOR, "[aria-label='Next Page']"):
        print("No more pages")
        break


driver.quit()

print("Total links:", len(job_links))

with open("jobs.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Job Title", "Link"])
    for title, link in zip(job_titles, job_links):
        writer.writerow([title, link])
