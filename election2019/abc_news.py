import logging
from collections import OrderedDict
from urllib.parse import urlparse, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook

from .main import set_candidate, state_abbr, is_ignored, verify_all, \
    verify_twitter, verify_facebook, verify_instagram, search_page_links, \
    candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching abc")

root_url = "https://www.abc.net.au/news/elections/federal/2019/guide/"
root_domain = urlparse(root_url).netloc

candidates_url = urljoin(root_url, "candidates")
candidates_soup = BeautifulSoup(requests.get(candidates_url).text,
                                "html.parser")
candidates_cells = candidates_soup.find_all("td", class_="candidate")

electorates_url = urljoin(root_url, "electorates-by-state")
electorates_soup = BeautifulSoup(requests.get(electorates_url).text,
                                 "html.parser")
electorates_cells = electorates_soup.find_all("td", class_="electorate")


def build_candidates(candidates):
    for candidate_cell in candidates_cells:
        contents = candidate_cell.contents
        siblings = list(candidate_cell.next_siblings)

        first_name = str(contents[0].string).strip()
        family_name = str(contents[1].string)
        full_name = f"{first_name} {family_name}"
        electorate = siblings[3].a.string.replace("Senate - ", "").replace(
            " (*)", "").replace("A.C.T.", "Australian Capital Territory")

        # Identify if sitting
        set_candidate(candidates, full_name, electorate, "sitting",
                      len(contents) == 4)


def build_electorates():
    electorates_data = {}

    for electorate in electorates_cells:
        siblings = list(electorate.next_siblings)
        parent_siblings = list(electorate
                               .parent.parent.parent.previous_siblings)
        state = parent_siblings[1].text
        electorate_url = urljoin(f"https://{root_domain}",
                                 electorate.a['href'])

        electorate_name = electorate.a.text

        electorates_data[electorate_name] = OrderedDict({
            "name": electorate_name,
            "state": state_abbr[state],
            "url": electorate_url,
            "party": siblings[1].text,
            "margin": float(siblings[3].text)
        })

    return pd.DataFrame.from_dict(electorates_data, orient='index')


def scrape_candidate_websites(electorates, candidates):
    rows = list(electorates.iterrows())
    for index, electorate in tqdm_notebook(rows, total=len(rows)):
        electorate_soup = BeautifulSoup(requests.get(electorate["url"]).text,
                                        "html.parser")
        electorate_name = electorate_soup.h1.text.replace(" (Key Seat)", "")

        electorate_candidate_cells = \
            electorate_soup.find_all("div", class_="eg-electorate-bio")

        for candidate_cell in electorate_candidate_cells:
            candidate_name = candidate_cell.h3.text
            logger.info(f"\n{candidate_name}")

            if not candidate_cell.find("a"):
                logger.info("Couldn't find website")
                continue

            candidate_website = candidate_cell.a['href']

            if not candidate_exists(candidates, candidate_name,
                                    electorate_name):
                logger.error(f"Couldn't find candidate {candidate_name}")
                continue
            elif is_ignored(candidate_website) or verify_all(candidate_website):
                logger.info(f"Ignoring {candidate_website}")
                continue

            set_candidate(candidates, candidate_name, electorate_name,
                          "website", candidate_website)
            set_candidate(candidates, candidate_name, electorate_name,
                          "twitter", verify_twitter(candidate_website))
            set_candidate(candidates, candidate_name, electorate_name,
                          "facebook", verify_facebook(candidate_website))
            set_candidate(candidates, candidate_name, electorate_name,
                          "instagram", verify_instagram(candidate_website))

            try:
                candidate_website_raw = requests.get(candidate_website)
            except requests.RequestException as e:
                logger.error(
                    f"Failed to visit {candidate_website}")
                logger.error(e)
                continue

            candidate_website_soup = BeautifulSoup(candidate_website_raw.text,
                                                   "html.parser")
            links = candidate_website_soup.find_all("a")
            search_page_links(candidate_name, electorate_name, candidates,
                              links)
