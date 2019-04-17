import logging
from collections import OrderedDict
from urllib.parse import urlparse, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook

from .main import state_lookup, is_ignored, verify_all, \
    verify_twitter, verify_facebook, verify_instagram, search_page_links

logger = logging.getLogger("election2019")

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


def build_candidates():
    candidates_data = {}
    candidate_names = []

    for candidate in candidates_cells:
        contents = candidate.contents
        siblings = list(candidate.next_siblings)

        first_name = str(contents[0].string).strip()
        family_name = str(contents[1].string)
        full_name = f"{first_name} {family_name}"
        candidate_names.append(full_name)

        candidates_data[full_name] = OrderedDict({
            "first_name": first_name,
            "family_name": family_name,
            "party": siblings[1].span.string,
            "electorate": siblings[3].a.string,
            "sitting": len(contents) == 4,
            "website": "",
            "twitter": "",
            "facebook": "",
            "instagram": ""
        })

    assert len(candidate_names) == len(set(candidate_names))
    return pd.DataFrame.from_dict(candidates_data, orient="index")


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
            "state": state_lookup[state],
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
        electorate_candidate_cells = \
            electorate_soup.find_all("div", class_="eg-electorate-bio")

        for candidate_cell in electorate_candidate_cells:
            candidate_name = candidate_cell.h3.text
            logger.info(f"\n{candidate_name}")

            if not candidate_cell.find("a"):
                logger.info("Couldn't find website")
                continue

            candidate_website = candidate_cell.a['href']

            if candidate_name not in candidates.index:
                logger.error(f"Couldn't find candidate {candidate_name}")
                continue
            elif is_ignored(candidate_website) or verify_all(candidate_website):
                logger.info(f"Ignoring {candidate_website}")
                continue

            candidates.at[candidate_name, "website"] = candidate_website
            candidates.at[candidate_name, "twitter"] = verify_twitter(
                candidate_website)
            candidates.at[candidate_name, "facebook"] = verify_facebook(
                candidate_website)
            candidates.at[candidate_name, "instagram"] = verify_instagram(
                candidate_website)

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
            search_page_links(candidate_name, candidates, links)
