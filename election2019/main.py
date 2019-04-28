from urllib.parse import urlparse
import logging
import time
import sys

logger = logging.getLogger("election2019")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(f"logs/{int(time.time())}.log"))
logger.addHandler(logging.StreamHandler(sys.stdout))

abbr_state = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "WA": "Western Australia",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "TA": "Tasmania",
    "ACT": "Australian Capital Territory",
    "A.C.T.": "Australian Capital Territory",
    "NT": "Northern Territory",
}

state_abbr = {v: k for k, v in abbr_state.items()}

ignored_accounts = ["australianlabor", "liberalaus", "greens",
                    "australianlabor", "laborconnect", "palmerutdparty",
                    "unitedausparty", "australian.greens", "share",
                    "victoriangreens", "the.greens.nsw", "greensnsw",
                    "centre_alliance", "centrealliance", "the_nationals",
                    "thenationalsaus", "greenssa",
                    "actgreens", "greensact", "ausprogressive",
                    "pglaborconnectvideos", "sciencepartyaus",
                    "liberalpartyaustralia", "queenslandgreens", "qldgreens",
                    "auschrist", "australianchristians",
                    "tasmaniangreens", "auschrist", "liberalnsw",
                    "libralvictoria", "nswgreens", "australiangreens",
                    "thegreenssa", "katterausparty", "kattersausparty",
                    "kapteam", "votesustainable", "tweet",
                    "liberalpartynsw", "liberalvictoria",
                    "youngliberalnationalparty", "countrylibs", "wagreens",
                    "thegreenswa", "sharer.php", "vic_socialists",
                    "realbobkatter", "vicsocialists", "vic_socialists",
                    "westernaustraliapartywa", "westausparty",
                    "westernaustraliaparty", "austfirstparty",
                    "animaljusticeau", "animaljusticepartyofficial",
                    "animaljusticeparty"]

with open("ignored_websites", 'r') as f:
    ignored_websites = [line.strip() for line in f.readlines()]


def is_ignored(url: str):
    return url.replace("www.", ""). \
               replace("http://", ""). \
               replace("https://", ""). \
               replace("/", "") in ignored_websites


def filter_domain(domain: str):
    return domain.replace("www.", "").replace("m.", "")


def verify_url(base_url: str, test_url: str):
    base_domain = filter_domain(urlparse(base_url).netloc)
    test_domain = filter_domain(urlparse(test_url).netloc)

    if base_domain == test_domain:
        account_split = urlparse(test_url).path.lower().split("/")

        # Catch facebook post links
        if "photos" in account_split or "videos" in account_split:
            return ""

        account = account_split[-2] if not account_split[-1] else account_split[
            -1]
        if account not in ignored_accounts:
            return account.lower()
    return ""


def verify_twitter(url: str):
    return verify_url("http://twitter.com", url)


def verify_facebook(url: str):
    return verify_url("http://facebook.com",
                      url.replace("pg/", "").replace("/about/", ""))


def verify_instagram(url: str):
    return verify_url("http://instagram.com", url)


def verify_all(url: str):
    verified = [verify_twitter(url), verify_facebook(url),
                verify_instagram(url)]
    return any(verified)


def search_page_links(candidate_name, electorate, candidates, links):
    facebook = twitter = instagram = False
    for link in links:
        if not link.has_attr("href"):
            continue

        twitter_account = verify_twitter(link["href"])
        facebook_account = verify_facebook(link["href"])
        instagram_account = verify_instagram(link["href"])

        if twitter_account and not twitter:
            twitter = True
            logger.info(
                f"Found {candidate_name}'s twitter: {twitter_account}")
            set_candidate(candidates, candidate_name, electorate, "twitter",
                          twitter_account)

        if facebook_account and not facebook:
            facebook = True
            logger.info(
                f"Found {candidate_name}'s facebook: {facebook_account}")
            set_candidate(candidates, candidate_name, electorate, "facebook",
                          facebook_account)

        if instagram_account and not instagram:
            instagram = True
            logger.info(
                f"Found {candidate_name}'s instagram: {instagram_account}")
            set_candidate(candidates, candidate_name, electorate, "instagram",
                          instagram_account)


def candidate_exists(candidates, name, electorate):
    name = name.upper()
    return f"{name} ({electorate})" in candidates.index


def get_candidate(candidates, name, electorate):
    name = name.upper()
    return candidates.loc[f"{name} ({electorate})"]


def set_candidate(candidates, name, electorate, column, value):
    name = name.upper()
    if candidate_exists(candidates, name, electorate):
        candidates.at[f"{name} ({electorate})", column] = value
