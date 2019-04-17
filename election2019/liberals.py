import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from election2019.main import search_page_links

logger = logging.getLogger("election2019")

driver = webdriver.Firefox()
driver.get("https://www.liberal.org.au/our-team")
total_candidate_count = 0
candidate_count = 1
while candidate_count > total_candidate_count:
    total_candidate_count = candidate_count
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    candidate_count = driver.execute_script(
        "return document.getElementsByClassName('member-profile').length")

page_html = driver.execute_script("return document.documentElement.outerHTML")
driver.close()


def parse_html(candidates):
    page_soup = BeautifulSoup(page_html, "html.parser")
    for candidate_cell in page_soup.find_all("article",
                                             class_="member-profile"):
        candidate_name_span = candidate_cell.div.h1.span
        [br.replace_with(" ") for br in candidate_name_span.find_all("br")]
        candidate_name = candidate_name_span.text
        logger.info(f"\n{candidate_name}")

        if candidate_name not in candidates.index:
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, candidates,
                          candidate_cell.select("li a"))
