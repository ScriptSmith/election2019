import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook

from election2019.main import search_page_links, candidate_exists

logger = logging.getLogger("election2019")
logger.info("Searching uap")

candidate_data = requests.get(
    "https://www.unitedaustraliaparty.org.au/wp-admin/admin-ajax.php?action="
    "wp_ajax_ninja_tables_public_action&table_id=45728&target_action=get-all-"
    "data&default_sorting=old_first&skip_rows=0&limit_rows=0").json()


def scrape_candidates_pages(candidates):
    for candidate in tqdm_notebook(candidate_data, total=len(candidate_data)):
        link_soup = BeautifulSoup(candidate["value"]["candidatenameandbio"],
                                  "html.parser")

        if not link_soup.find("a"):
            continue

        candidate_soup = BeautifulSoup(requests.get(link_soup.a["href"]).text,
                                       "html.parser")

        candidate_name = candidate_soup.h1.text
        logger.info(f"\n{candidate_name}")

        electorate = candidate['value']['electoraldivision']

        if not candidate_exists(candidates, candidate_name, electorate):
            logger.error(f"Couldn't find candidate {candidate_name}")
            continue

        search_page_links(candidate_name, electorate, candidates,
                          candidate_soup.select(".c_social a"))
