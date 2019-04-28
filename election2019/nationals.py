import logging

import requests
from bs4 import BeautifulSoup

from election2019.main import search_page_links, candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching nationals")

candidates_page_soup = BeautifulSoup(
    requests.get("http://nationals.org.au/our-team/candidates").text,
    "html.parser")

member_page_soup = BeautifulSoup(
    requests.get("http://nationals.org.au/our-team/").text, "html.parser")


def scrape_members_page(candidates):
    for candidate in member_page_soup.find_all("div", class_="vc_column-inner"):
        if not candidate.find("h1"):
            continue
        candidate_name = candidate.h1.text \
            .replace("The Hon. ", "") \
            .replace("Mr ", "") \
            .replace("Mrs ", "") \
            .replace("Senator ", "") \
            .replace("the Hon. ", "") \
            .replace(" MP", "") \
            .strip()
        electorate_name = candidate.h3.text.split("for ")[-1].replace("the ",
                                                                      "")
        logger.info(f"\n{candidate_name}")

        if not candidate_exists(candidates, candidate_name, electorate_name):
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, electorate_name, candidates,
                          candidate.select("a"))
