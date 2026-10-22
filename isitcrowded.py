import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Reads the .env file to import API key
load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

# DEMO_DATA
DEMO_DATA = {
    "page": {"totalElements": 47},
    "_embedded": {
        "events": [
            {"classifications": [{"segment": {"name": "Sports"}}]},
            ]
    }
}


# Initialize with city selection, start & end date range
city_input = input("Enter your city:").strip().title()
sunday_input = input("Enter the Sunday date (use: YYYY-MM-DD): ")


def dates(sunday_input):
    """Converts user input Sunday date to ISO format and calculates 
    end date of 7 day period"""

    # Parse user input date to a datetime object
    start_date = datetime.strptime(
        sunday_input + " 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    # Converts start datetime object to end date
    end_date = start_date + timedelta(days=7)

    # Converts start & end date to ISO format for params dictionary
    start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    return start_iso, end_iso


start_iso, end_iso = dates(sunday_input)

# Filters to be used in key word arguments
filters = {
    "apikey": API_KEY,
    "city": city_input,
    "startDateTime": start_iso,
    "endDateTime": end_iso,
    "size": 20
}


def data_set():
    """API connection to pull data. If no API_KEY used program will
    run on demo data"""

    if not API_KEY:
        print("No API key found. Running in demo mode with sample data.")
        print("To use live data, see instructions in README.")
        data = DEMO_DATA

    else:
        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            # Using get method to set enpoint(url) and shape data with filters
            response = requests.get(url, params=filters, timeout=10)
            # Checking status code value to see if pull sucessful
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            # If success, returned in JSON and converted to dictionary below
            data = response.json()
        except Exception as e:
            print(f"Error connecting to API: {e}.")
            print("Using demo mode")
            data = DEMO_DATA