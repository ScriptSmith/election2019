import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select

from election2019.main import search_page_links, candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching liberals")


def get_page(d):
    total_candidate_count = 0
    candidate_count = 1
    while candidate_count > total_candidate_count:
        total_candidate_count = candidate_count
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        candidate_count = d.execute_script(
            "return document.getElementsByClassName('member-profile').length")

    return d.execute_script("return document.documentElement.outerHTML")


pages = []

driver = webdriver.Firefox()
driver.get("https://www.liberal.org.au/our-team")
pages.append(get_page(driver))
Select(driver.find_element_by_id(
    "edit-field-mp-section-type-value")).select_by_index(3)
time.sleep(5)
pages.append(get_page(driver))
driver.close()


def parse_page(candidates, page_html):
    page_soup = BeautifulSoup(page_html, "html.parser")
    for candidate_cell in page_soup.find_all("article",
                                             class_="member-profile"):
        candidate_name_span = candidate_cell.div.h1.span
        [br.replace_with(" ") for br in candidate_name_span.find_all("br")]
        candidate_name = candidate_name_span.text
        logger.info(f"\n{candidate_name}")

        electorate_name = \
            candidate_cell.find("div", class_="bg-grad").p.text.split("for ")[
                -1]

        if not candidate_exists(candidates, candidate_name, electorate_name):
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, electorate_name, candidates,
                          candidate_cell.select("li a"))


def parse_html(candidates):
    for page in pages:
        parse_page(candidates, page)
