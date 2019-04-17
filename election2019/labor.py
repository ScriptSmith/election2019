import logging
from time import sleep
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests
from tqdm import tqdm_notebook

from election2019.main import search_page_links

logger = logging.getLogger("election2019")

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
        sleep(5)

        candidate_name = candidate_page_soup.h1.text.strip()
        logger.info(f"\n{candidate_name}")

        if candidate_name not in candidates.index:
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, candidates,
                          candidate_page_soup.select(
                              ".page-grid-item__col-1-description a"))
