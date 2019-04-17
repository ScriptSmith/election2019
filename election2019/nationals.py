import logging

import requests
from bs4 import BeautifulSoup

from election2019.main import search_page_links

logger = logging.getLogger("election2019")

candidates_page_soup = BeautifulSoup(
    requests.get("http://nationals.org.au/our-team/candidates").text, "html.parser")

member_page_soup = BeautifulSoup(
    requests.get("http://nationals.org.au/our-team/").text, "html.parser")


def scrape_candidates_page(candidates):
    candidate_cells = candidates_page_soup.select(
        ".wpb_column.vc_column_container.vc_col-sm-4")

    for candidate in candidate_cells:
        if not candidate.find("h1"):
            continue
        candidate_name = candidate.h1.text.strip()

        if candidate_name not in candidates.index:
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, candidates, candidate.select("a"))


def scrape_members_page(candidates):
    for candidate in member_page_soup.find_all("div", class_="vc_column-inner"):
        if not candidate.find("h1"):
            continue
        candidate_name = candidate.h1.text\
            .replace("The Hon. ", "")\
            .replace("Mr ", "")\
            .replace("Mrs ", "")\
            .replace("Senator ", "")\
            .replace("the Hon. ", "")\
            .replace(" MP", "")\
            .strip()
        logger.info(f"\n{candidate_name}")

        if candidate_name not in candidates.index:
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, candidates, candidate.select("a"))
