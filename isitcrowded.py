import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Reads the .env file to import API key
load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

# Demo data set used when no API key is used
DEMO_DATA = {
    "page": {
        "totalPages": 1
    },
    "_embedded": {
        "events": [
            {"classifications": [{"segment": {"name": "Sports"}}]},
            {"classifications": [{"segment": {"name": "Sports"}}]},
            {"classifications": [{"segment": {"name": "Music"}}]},
            {"classifications": [{"segment": {"name": "Music"}}]},
            {"classifications": [{"segment": {"name": "Music"}}]},
            {"classifications": [{"segment": {"name": "Arts & Theatre"}}]},
            {"classifications": [{"segment": {"name": "Family"}}]},
            {"classifications": [{"segment": {"name": "Film"}}]}
            ]
    }
}


def dates(startdate_input):
    """Converts user input start date to ISO format and calculates
    end date of 7 day period"""
    try:
        # Parse user input date to a datetime object
        start_date = datetime.strptime(
            startdate_input + " 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
    # Check for properly formatted start date YYYY-MM-DD
    except ValueError:
        raise ValueError("Invalid date format! Please use YYYY-MM-DD "
              "(e.g., 2026-10-25).")

    # Check start date must be today or in future (up to 2 years)
    if start_date.date() < datetime.now().date():
        raise ValueError("Start date must be today or within 2 years out!")

    if start_date.date() > datetime.now().date() + timedelta(days=730):
        raise ValueError("Date is too far in advance! Please enter a "
              "date within 2 years")

    # Converts start datetime object to end date
    end_date = start_date + timedelta(days=7)

    # Converts start & end date to ISO format for params dictionary
    start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    return start_iso, end_iso, end_date


def data_set(page_number, filters):
    """API connection and call to pull data. If no API_KEY used program will
    run on demo data"""

    filters["page"] = page_number
    if not API_KEY:
        print("\nNo API key found. Running in demo mode with sample data.")
        print("To use live data, see instructions in README.")
        data = DEMO_DATA

    else:
        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            # Using get method to set endpoint(url) and shape data with filters
            response = requests.get(url, params=filters, timeout=10)
            # Checking status code value to see if pull sucessful
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            # If success, returned in JSON and converted to dictionary below
            data = response.json()
        except Exception as e:
            print(f"\nError connecting to API: {e}.")
            print("Using demo mode")
            data = DEMO_DATA

    return data


while True:
    # Initialize with user city input and start date
    city_input = input("Enter your city:").strip().title()
    startdate_input = input("Enter the start date (use: YYYY-MM-DD): ")

    # Call dates function and catch failure if due to improper date input
    try:
        start_iso, end_iso, end_date = dates(startdate_input)
    except ValueError as e:
        print(e)
        continue

    # Filters to be used in key word arguments
    filters = {
        "apikey": API_KEY,
        "city": city_input,
        "startDateTime": start_iso,
        "endDateTime": end_iso,
        "size": 200,
        "page": 0
    }

    # Pagination use page 0 to get totalPages, then loop through remaining
    all_events = []
    page = 0
    page_data = data_set(page, filters)
    # Read how many pages exist from response page block
    total_pages = page_data["page"]["totalPages"]
    # Add page 0's events into all_events
    if "_embedded" in page_data:
        all_events.extend(page_data["_embedded"]["events"])

    # Looping through pages from 1 to last page (exclusive)
    for page in range(1, total_pages):
        page_data = data_set(page, filters)
        # Add events into all_events (holds every event from every page)
        if "_embedded" in page_data:
            all_events.extend(page_data["_embedded"]["events"])

    # Using all_events to break down event type
    sports = 0
    music = 0
    arts = 0
    family = 0
    film = 0

    for event in all_events:
        # Extracting segment type by assigning to variable segment
        try:
            segment = event["classifications"][0]["segment"]["name"]
        except (KeyError, IndexError):
            continue  # Skip events with no classification

        if segment == "Sports":
            sports = sports + 1
        if segment == "Music":
            music = music + 1
        if segment == "Arts & Theatre":
            arts = arts + 1
        if segment == "Family":
            family = family + 1
        if segment == "Film":
            film = film + 1

    # Formatting outputs & converting datetime object to string
    total = sports + music + arts + family + film
    end_d = end_date - timedelta(days=1)
    format_end_d = end_d.strftime("%Y-%m-%d")

    if total == 0:
        print(f"No events found for '{city_input}' in that date range. "
              "Check city spelling. If correct, try a nearby city or "
              "a different start date.")
    else:
        print(f"\nWeek of {startdate_input} to {format_end_d}")
        print(f"City: {city_input}\n")

        print(f"Total events: {total}\n")

        print("Breakdown:")
        print(f"Sports: {sports}")
        print(f"Music: {music}")
        print(f"Arts & Theatre: {arts}")
        print(f"Family: {family}")
        print(f"Film: {film}")

    # Again lets user repeat program by inputting y/n
    again = input("Search again? (y/n): ")
    if again.lower() != "y":
        break
