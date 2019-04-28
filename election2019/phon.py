import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

from election2019.main import search_page_links, candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching phon")

driver = webdriver.Firefox()
driver.get("https://www.onenation.org.au/our-team/")

# Wait for human captcha input
sleep(10)

page_html = driver.execute_script("return document.documentElement.outerHTML")
driver.close()
page_soup = BeautifulSoup(page_html, "html.parser")


def scrape_candidates_page(candidates):
    candidate_soup = page_soup.find_all("section", class_="avia-team-member")
    print(len(candidate_soup))
    for candidate in candidate_soup:
        candidate_name = candidate.h3.text
        logger.info(f"\n{candidate_name}")

        electorate = candidate.find("div", class_="team-member-job-title") \
            .text \
            .split("for ")[-1]

        if candidate_exists(candidates, candidate_name, electorate):
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, electorate, candidates,
                          candidate.select(".avia-team-icon"))
