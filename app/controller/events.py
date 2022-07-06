import json

import requests
from bs4 import BeautifulSoup

from app.controller.utils import get_today
from app.controller import date_parser
from app.config import get_settings


settings = get_settings()
MLH_URL = lambda year: f"https://mlh.io/seasons/{year}/events"  # noqa


def event_happened(date_month, date_day) -> bool:
    """
    Check if event happened in the past
    """
    TODAY = get_today()
    if date_month < TODAY.month:
        return True
    if date_month == TODAY.month and date_day < TODAY.day:
        return True
    return False


# Queries NorthAmerican MLH events from the MLH events page
# and outputs sorted results to a JSON file
def query_mlh_events(NUMBER_OF_EVENTS=100) -> list:
    print("Start querying")

    TODAY = get_today()

    # Current year
    year = str(TODAY.year)
    # MLH url
    url = f"https://mlh.io/seasons/{year}/events"
    # Get HTML page
    response = requests.get(url)

    # Parse into content tree with bs4
    content_tree = BeautifulSoup(response.content, settings.MLH_EVENT_PARSER)
    events = []

    # Find events container
    raw_events = content_tree.find_all(
        "div", {"itemtype": "http://schema.org/Event"}
    )  # noqa

    event_counter = 0

    # Loop through event elements and parse into JSON objects
    # that are placed in a list
    for raw_event in raw_events:

        if event_counter >= NUMBER_OF_EVENTS:
            break

        event = {}
        link = raw_event.find("a", {"class": "event-link"})

        # Skip event if no links found
        if link is None:
            continue

        # Get name and link to website
        event["name"] = link["title"]
        event["website"] = link["href"]

        text_date_wrapper = link.find("p", {"class": "event-date"})
        text_date = text_date_wrapper.text

        start_date, end_date = date_parser.convertToDateTuple(text_date)
        if end_date is None:
            date_month, date_day = start_date
        else:
            date_month, date_day = end_date

        # Ignore event if it ended in the past
        if event_happened(date_month, date_day):
            continue

        # Create date object
        date = {}
        date["start"] = date_parser.dateTupleToString(year, start_date)
        if end_date is not None:
            date["end"] = date_parser.dateTupleToString(year, end_date)
        else:
            # There was no end date
            date["end"] = ""
        event["date"] = date

        # Event image
        image_wrapper = link.find("div", {"class": "image-wrap"})
        image = image_wrapper.img
        if image is not None:
            event["image"] = {"src": image["src"], "alt": image["alt"]}

        # Event logo
        logo_wrapper = link.find("div", {"class": "event-logo"})
        logo = logo_wrapper.img
        if logo is not None:
            event["logo"] = {"src": logo["src"], "alt": logo["alt"]}

        # Event address
        address = {}
        city = link.find("span", {"itemprop": "city"})
        address["locality"] = city.text
        state = link.find("span", {"itemprop": "state"})
        address["region"] = state.text
        event["address"] = address

        # Append event to the list
        events.append(event)

        # Only count the event if successfully got the resource
        event_counter += 1

    return events


def start_harvest_thread():
    file_io_mode = "w"
    indent = 2

    queried_events = query_mlh_events()

    sorted_events = date_parser.sortEvents(queried_events)
    with open(settings.MLH_EVENT_STORAGE_FILE_PATH, file_io_mode) as outfile:
        json.dump(sorted_events, outfile, indent=indent)
