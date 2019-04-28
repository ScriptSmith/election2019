from election2019.main import abbr_state

from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

root_url = "https://www.aec.gov.au/election/"

downloads_soup = BeautifulSoup(
    requests.get(urljoin(root_url, "downloads.htm")).text,
    "html.parser")

candidate_link = downloads_soup.find("ul", class_="linkList").a['href']


def scrape_candidates():
    # Read data
    candidates = pd.read_csv(urljoin(root_url, candidate_link))

    # Organise columns
    candidates = candidates[
        ["ballot_given_nm", "surname", "div_nm", "state_ab", "nom_ty",
         "party_ballot_nm"]]
    candidates = candidates.rename(columns={
        "ballot_given_nm": "first_name",
        "surname": "last_name",
        "div_nm": "electorate",
        "state_ab": "state",
        "nom_ty": "type",
        "party_ballot_nm": "party",
    })
    candidates['sitting'] = False
    candidates['website'] = ""
    candidates['twitter'] = ""
    candidates['twitter_id'] = ""
    candidates['facebook'] = ""
    candidates['instagram'] = ""

    # Add electorate for senators
    for index, candidate in candidates.iterrows():
        if candidate['type'] == 'S':
            candidates.at[index, 'electorate'] = abbr_state[candidate['state']]

    new_index = []
    for _, candidate in candidates.iterrows():
        fname = candidate['first_name'].upper()
        lname = candidate['last_name'].upper()
        ename = candidate['electorate']
        new_index.append(f"{fname} {lname} ({ename})")

    candidates.index = new_index
    return candidates
