import logging
from time import sleep
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests
from tqdm import tqdm_notebook

from election2019.main import search_page_links, candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching labor")

root_url = "https://www.alp.org.au"

page_soup = BeautifulSoup(
    requests.get(urljoin(root_url, "/our-people/our-people/")).text,
    "html.parser")


def scrape_candidates_pages(candidates):
    links = set(
        link["href"] for link in page_soup.select(".ml-card .ml-card__link"))
    for candidate_link in tqdm_notebook(links, total=len(links)):
        candidate_page_soup = BeautifulSoup(
            requests.get(urljoin(root_url, candidate_link)).text,
            "html.parser")
        sleep(1)

        candidate_name = candidate_page_soup.h1.text.strip()
        electorate_name = ""

        electorate_ids = ["Member for ",
                          "Senator for ",
                          "Senate Candidate for ",
                          "Candidate for "]
        headings = []
        headings.extend(candidate_page_soup.findAll("h2"))
        headings.extend(candidate_page_soup.findAll("h3"))
        headings.extend(candidate_page_soup.findAll("h4"))
        for heading in headings:
            if heading:
                text = heading.text
                for identifier in electorate_ids:
                    if identifier in text:
                        electorate_name = text.replace(identifier, "").strip()
                        break

        logger.info(f"\n{candidate_name}")

        if not candidate_exists(candidates, candidate_name, electorate_name):
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, electorate_name, candidates,
                          candidate_page_soup.select(
                              ".page-grid-item__col-1-description a"))
