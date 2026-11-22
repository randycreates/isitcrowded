"""Is It Crowded - a tool that counts events by category & genre
for a given city and a seven-day period"""

import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# Reads the .env file to import API key
load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

# Demo data set used when no API key is used
# Dates are overwritten at runtime in demo mode
DEMO_DATA = {
    "page": {"totalPages": 1},
    "_embedded": {
        "events": [
            {
                "classifications": [{"segment": {"name": "Sports"}}],
                "dates": {"start": {"localDate": "2027-01-04"}},
            },
            {
                "classifications": [
                    {"segment": {"name": "Sports"}, "genre": {"name": "Basketball"}}
                ],
                "dates": {"start": {"localDate": "2027-01-05"}},
            },
            {
                "classifications": [{"segment": {"name": "Music"}}],
                "dates": {"start": {"localDate": "2027-01-06"}},
            },
            {
                "classifications": [
                    {"segment": {"name": "Music"}, "genre": {"name": "Rock"}}
                ],
                "dates": {"start": {"localDate": "2027-01-07"}},
            },
            {
                "classifications": [
                    {"segment": {"name": "Music"}, "genre": {"name": "Hip-Hop/Rap"}}
                ],
                "dates": {"start": {"localDate": "2027-01-08"}},
            },
            {
                "classifications": [
                    {
                        "segment": {"name": "Arts & Theatre"},
                        "genre": {"name": "Theatre"},
                    }
                ],
                "dates": {"start": {"localDate": "2027-01-09"}},
            },
            {
                "classifications": [{"segment": {"name": "Family"}}],
                "dates": {"start": {"localDate": "2027-01-10"}},
            },
            {
                "classifications": [
                    {"segment": {"name": "Film"}, "genre": {"name": "Horror"}}
                ],
                "dates": {"start": {"localDate": "2027-01-04"}},
            },
        ]
    },
}


def dates(date_string):
    """Converts user input start date to ISO format and calculates
    end date of 7 day period"""
    try:
        # Parse user input date to a datetime object
        start_date = datetime.strptime(date_string + " 00:00:00", "%Y-%m-%d %H:%M:%S")

    # Check for properly formatted start date YYYY-MM-DD
    except ValueError as exc:
        raise ValueError(
            "Invalid date format! Please use YYYY-MM-DD (e.g., 2026-10-25)."
        ) from exc

    # Check start date must be today or in future (up to 2 years)
    if start_date.date() < datetime.now().date():
        raise ValueError("Start date must be today or within 2 years out!")

    if start_date.date() > datetime.now().date() + timedelta(days=730):
        raise ValueError(
            "Date is too far in advance! Please enter a date within 2 years"
        )

    # Converts start datetime object to end date
    calculated_end = start_date + timedelta(days=7)

    # Converts start & end date to ISO format for params dictionary
    start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = calculated_end.strftime("%Y-%m-%dT%H:%M:%SZ")

    return start_iso, end_iso, calculated_end


def max_search_date():
    """Returns the latest searchable date as a YYYY-MM-DD string,
    Mirrors the 730-day cap enforced in dates()."""
    return (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d")


def min_search_date():
    """Returns today's date as a YYYY-MM-DD string for the date picker's min."""
    # Keep in step with the past-date check in dates().
    return datetime.now().strftime("%Y-%m-%d")


def data_set(page_number, filters):
    """API connection and call to pull data. If no API_KEY used program will
    run on demo data"""

    filters["page"] = page_number
    if not API_KEY:
        print("\nNo API key found. Running in demo mode with sample data.")
        print("To use live data, see instructions in README.")
        return DEMO_DATA, "demo"

    try:
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        # Using get method to set endpoint(url) and shape data with filters
        response = requests.get(url, params=filters, timeout=10)
        # Checking status code value to see if pull sucessful
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"API returned status {response.status_code}"
            )

        # If success, returned in JSON and converted to dictionary below
        return response.json(), "live"
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\nError connecting to API: {e}.")
        print("Using demo mode")
        return DEMO_DATA, "demo_fallback"


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def count_events(city, date_string):
    """Fetch events for a city and date range, return category counts."""
    start_iso, end_iso, end_date = dates(date_string)

    # Filters to be used in key word arguments
    filters = {
        "apikey": API_KEY,
        "city": city,
        "startDateTime": start_iso,
        "endDateTime": end_iso,
        "size": 200,
        "page": 0,
    }

    # Pagination use page 0 to get totalPages, then loop through remaining
    all_events = []
    page = 0
    page_data, data_source = data_set(page, filters)
    # Read how many pages exist from response page block
    total_pages = page_data["page"]["totalPages"]
    # Add page 0's events into all_events
    if "_embedded" in page_data:
        all_events.extend(page_data["_embedded"]["events"])

    # Looping through pages from 1 to last page (exclusive)
    for page in range(1, total_pages):
        page_data, _ = data_set(page, filters)
        # Add events into all_events (holds every event from every page)
        if "_embedded" in page_data:
            all_events.extend(page_data["_embedded"]["events"])

    if data_source != "live":
        start_dt = datetime.strptime(date_string, "%Y-%m-%d")
        for i, event in enumerate(all_events):
            rebased = start_dt + timedelta(days=i % 7)
            event["dates"]["start"]["localDate"] = rebased.strftime("%Y-%m-%d")

    # Using all_events to break down event type
    sports = 0
    music = 0
    arts = 0
    family = 0
    film = 0

    # Dictionary to compile daily counts & genre breakdown in flask version
    daily_counts = {}
    genre_counts = {}

    for event in all_events:
        # Extracting segment type by assigning to variable segment
        try:
            segment = event["classifications"][0]["segment"]["name"]
            date = event["dates"]["start"]["localDate"]
        except (KeyError, IndexError, ValueError):
            continue

        counted = False

        if segment == "Sports":
            sports = sports + 1
            counted = True
        if segment == "Music":
            music = music + 1
            counted = True
        if segment == "Arts & Theatre":
            arts = arts + 1
            counted = True
        if segment == "Family":
            family = family + 1
            counted = True
        if segment == "Film":
            film = film + 1
            counted = True

        if counted:
            if date in daily_counts:
                daily_counts[date] += 1
            else:
                daily_counts[date] = 1

        if counted:
            # Read the genre; missing or Ticketmaster's "Undefined"
            # both mean "we couldn't classify this.
            try:
                genre = event["classifications"][0]["genre"]["name"]
            except (KeyError, IndexError, TypeError):
                # "unclassified" when no genre key.
                genre = "Unclassified"
            if genre == "Undefined":
                genre = "Unclassified"
            # Nest under the segment so the template can group by category.
            if segment not in genre_counts:
                genre_counts[segment] = {}
            if genre in genre_counts[segment]:
                genre_counts[segment][genre] += 1
            # Already seen; increment the existing count
            else:
                genre_counts[segment][genre] = 1

    # Build the seven-day list in the user's order
    daily_breakdown = []
    start_dt = datetime.strptime(date_string, "%Y-%m-%d")
    for offset in range(7):
        day = start_dt + timedelta(days=offset)
        iso = day.strftime("%Y-%m-%d")
        daily_breakdown.append(
            {
                "date": iso,
                "weekday": day.strftime("%A"),
                "count": daily_counts.get(iso, 0),
            }
        )

    # Real genres alphabetically sorted
    genre_breakdown = {}
    for segment, genres in genre_counts.items():
        sorted_genres = {g: genres[g] for g in sorted(genres) if g != "Unclassified"}
        if "Unclassified" in genres:
            sorted_genres["Unclassified"] = genres["Unclassified"]
        genre_breakdown[segment] = {
            "total": sum(genres.values()),
            "genres": sorted_genres,
        }

    return {
        "data_source": data_source,
        "sports": sports,
        "music": music,
        "arts": arts,
        "family": family,
        "film": film,
        "total": sports + music + arts + family + film,
        "daily_breakdown": daily_breakdown,
        "genre_breakdown": genre_breakdown,
        "start_date": start_iso,
        "end_date": end_date,
        "display_city": city,
        "display_start": date_string,
        "display_end": (end_date - timedelta(days=1)).strftime("%Y-%m-%d"),
    }


# Command line interface
if __name__ == "__main__":
    while True:
        # Initialize with user city input and start date
        city_input = input("Enter your city:").strip().title()
        startdate_input = input("Enter the start date (use: YYYY-MM-DD): ")

        # Call count_events, catch failure if due to improper date input
        try:
            counts = count_events(city_input, startdate_input)
        except ValueError as e:
            print(e)
            continue

        if counts["total"] == 0:
            print(
                f"No events found for '{city_input}' in that date range. "
                "Check city spelling. If correct, try a nearby city or "
                "a different start date."
            )
        else:
            end_d = counts["end_date"] - timedelta(days=1)
            format_end_d = end_d.strftime("%Y-%m-%d")

            print(f"\nWeek of {startdate_input} to {format_end_d}")
            print(f"City: {city_input}\n")

            print(f"Total events: {counts['total']}\n")

            print("Breakdown-")
            print(f"Sports: {counts['sports']}")
            print(f"Music: {counts['music']}")
            print(f"Arts & Theatre: {counts['arts']}")
            print(f"Family: {counts['family']}")
            print(f"Film: {counts['film']}")

        # Again lets user repeat program by inputting y/n
        again = input("Search again? (y/n): ")
        if again.lower() != "y":
            break
