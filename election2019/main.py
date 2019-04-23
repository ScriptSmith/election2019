from urllib.parse import urlparse
import logging
import sys
import time

logger = logging.getLogger("election2019")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(f"logs/{int(time.time())}.log"))
# logger.addHandler(logging.StreamHandler(sys.stdout))

state_lookup = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "Western Australia": "WA",
    "South Australia": "SA",
    "Tasmania": "TA",
    "Australian Capital Territory": "ACT",
    "Northern Territory": "NT"
}

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
        if "photos" in account_split or "photos" in account_split:
            return ""

        account = account_split[-2] if not account_split[-1] else account_split[
            -1]
        if account not in ignored_accounts:
            return account
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


def search_page_links(candidate_name, candidates, links):
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
            candidates.at[candidate_name, "twitter"] = twitter_account

        if facebook_account and not facebook:
            facebook = True
            logger.info(
                f"Found {candidate_name}'s facebook: {facebook_account}")
            candidates.at[candidate_name, "facebook"] = facebook_account

        if instagram_account and not instagram:
            instagram = True
            logger.info(
                f"Found {candidate_name}'s instagram: {instagram_account}")
            candidates.at[candidate_name, "instagram"] = instagram_account
