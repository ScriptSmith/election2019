import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from election2019.main import search_page_links

logger = logging.getLogger("election2019")

root_url = "https://greens.org.au/candidates"
page_soup = BeautifulSoup(requests.get(root_url).text, "html.parser")


def scrape_candidates_pages(candidates):
    global page_soup

    while True:
        next_page = page_soup.find("li", class_="pager__item--next")
        for candidate in page_soup.select(".person-box"):
            candidate_soup = BeautifulSoup(
                requests.get(urljoin(root_url, candidate["href"])).text,
                "html.parser")

            candidate_name = candidate_soup.title.text\
                .split(",")[0]\
                .split(" |")[0]

            logger.info(f"\n{candidate_name}")

            if candidate_name not in candidates.index:
                logger.error(f"Couldn't find candidate {candidate_name}")
                continue

            search_page_links(candidate_name, candidates, candidate_soup.select(
                ".person-contact__social-item"))

        if not next_page:
            break

        page_soup = BeautifulSoup(
            requests.get(urljoin(root_url, next_page.a["href"])).text,
            "html.parser")