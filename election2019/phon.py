import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

from election2019.main import search_page_links

logger = logging.getLogger("election2019")

driver = webdriver.Firefox()
driver.get("https://www.onenation.org.au/our-team/")

# Wait for human captcha input
sleep(120)

page_html = driver.execute_script("return document.documentElement.outerHTML")
driver.close()
page_soup = BeautifulSoup(page_html, "html.parser")


def scrape_candidates_page(candidates):
    for candidate in page_soup.find_all("section", class_="avia-team-member"):
        candidate_name = candidate.h3.text
        logger.info(f"\n{candidate_name}")

        if candidate_name not in candidates.index:
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, candidates,
                          candidate.select(".avia-team-icon"))
