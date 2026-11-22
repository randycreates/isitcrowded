# Is It Crowded

Is It Crowded is a Python tool that connects to Ticketmaster's Discovery API and provides a categorized breakdown of events in a given city for any seven-day period. It's built for hospitality professionals who need to gauge activity before making decisions about staffing, pricing, and programming. A city with a heavy event week looks very different from a quiet one and that difference matters when you're planning for the people who'll be there.

This version expands the original command-line tool into a web application with a graphical interface, and adds a genre summary to the category breakdown. The command-line version is still included and still runs.

## Overview

The purpose of Is It Crowded is to give hospitality professionals a quick read on how busy a city will be in a given week based on Ticketmaster events. It's meant to serve as a supplemental signal, not a replacement for demand forecasting.

The user enters a city and a start date. The program calculates a seven-day window starting from that date, connects to Ticketmaster's Discovery API and pulls the event listings for that window. It then counts the events by category and displays a summary: total events, plus a breakdown for Sports, Music, Arts & Theatre, Family and Film, with genres listed under each category. If no API key is available, the program runs on demo data so the tool can still be tested without live access.

**Main features:**

- Connects to Ticketmaster's Discovery API to pull live event data (when an API key is available)
- Falls back to demo data when no API key is present
- Web interface for entering a city and start date, with a results page showing the breakdown
- Command-line version included and still runnable
- Calculates a seven-day window from the start date
- Provides a summary by category: Music, Sports, Arts & Theatre, Family, Film
- Breaks each category down by genre
- Validates input: date format, past dates, future cap (2 years), and zero-result handling

## Prerequisites

- **Python 3** (standard library includes `datetime` and `os`)
- **Flask** — for the web application
- **requests** — for making HTTP calls to the API
- **python-dotenv** — for loading the API key from a `.env` file
- **A Ticketmaster Discovery API key** (free — see Installation Instructions). Optional; without it, the program runs on demo data.
- A terminal (Command Prompt, Terminal, or similar)
- Internet connection (for live data; demo mode works offline)

## Installation Instructions

1. **Confirm Python 3 is installed.**
   Open your terminal and type:
   ```
   python3 --version
   ```
   If it prints `Python 3.x.x`, you're good. If not, download Python 3 from [python.org](https://www.python.org/).

2. **Get the project files.**
   Choose one of these options:
   - **a. Clone the repository (recommended if you have Git):**
   Open your terminal and run:
   ```
   git clone https://github.com/randycreates/isitcrowded.git
   cd isitcrowded
   ```
- **b. Download the ZIP:**
Click the green **Code** button on the repository page, then select **Download ZIP**.
Unzip the file into a folder of your choice.

3. **Confirm the files are in the same folder.**
Whether you cloned or unzipped, `isitcrowded.py` and `app.py` should be in a folder you can find from the terminal.

4. **Install dependencies.**
In your terminal type:
   ```
   pip install -r requirements.txt
   ```
This installs Flask, requests, and python-dotenv.

5. **Get a free Ticketmaster API key. (Optional)**
Visit [developer.ticketmaster.com](https://developer.ticketmaster.com/) and sign up for a free developer account. You'll get an API key. If you skip this step, the program runs on demo data.

6. **Create a `.env` file. (Skip this step if not using an API key)**
In the same folder as `isitcrowded.py`, create a file called `.env` (note the leading dot). Add this line to your file:
   ```
   TICKETMASTER_API_KEY=your_key_here
   ```
Replace `your_key_here` with your actual key. Save and close.

**Note:** Files starting with a dot are hidden by default on macOS. Use `Cmd + Shift + .` to show them in Finder.

**Platform Notes**

- **Windows:** Paths use backslashes (`\`) instead of forward slashes (`/`). The `cd` command works the same way.
- **macOS and Linux:** The instructions work as written.

## How to Run the Program

### Web App

1. Open your terminal.
2. Navigate to the folder containing `app.py`:
   ```
   cd path/to/your/folder
   ```
3. Start the app:
   ```
   flask --app app run
   ```
4. Open a browser and go to `http://127.0.0.1:5000`.


### Command Line

1. Open your terminal.
2. Navigate to the folder containing `isitcrowded.py`:
   ```
   cd path/to/your/folder
   ```
3. Run the program:
   ```
   python3 isitcrowded.py
   ``` 
4. The program will prompt you for a city and a start date.

## Usage Instructions

### Web App

The web app opens on a form with two fields:

1. **City** — enter the city name (e.g., `Las Vegas`, `New Orleans`, `Miami`).
2. **Start date** — pick a date from the calendar, or type one in. The date must be today or later, and within the next two years.

Click **Submit**. The results page shows:

- **Week of / City** — the date range searched and the city entered.
- **Total events** — how many events were counted in that week.
- **Daily Breakdown** — each day of the week with its date, weekday, and event count.
- **Event Category Breakdown** — each category that had events, with its total, followed by the genres within that category and how many of each. Genres are listed alphabetically, and "Unclassified" appears last.

If no events are found for the city and date range, the page shows a message suggesting you check the city spelling, try a nearby city, or try a different date. A **Search again** link returns you to the form.

If no API key is set, the results page shows a notice that demo data is being used so the app can still be tested.

### Command Line

After launching the program, you'll be prompted for two inputs:

1. **City** — enter the city name (e.g., `Las Vegas`, `New Orleans`, `Miami`).
2. **Start date** — enter a date in `YYYY-MM-DD` format (e.g., `2026-12-20`). The program uses this as the first day of a seven-day window.

If the input is valid, the program displays a summary like this:

```
Week of 2026-12-20 to 2026-12-26
City: New Orleans

Total events: 77

Breakdown:
Sports: 4
Music: 57
Arts & Theatre: 16
Family: 0
Film: 0
```

If the date is in the past, too far in the future (more than two years out), or formatted incorrectly, the program prints a message explaining the issue and exits. If no events are found for the city and date range, it prints a message suggesting you check the city spelling, try a nearby city, or try a different date.

## Known Limitations

- **Counts reflect event listings, not unique events.** A concert with two performances will appear as two listings. The tool does not remove duplicates.
- **Miscellaneous events are excluded.** Events classified by Ticketmaster as "Miscellaneous" — which can include tours, upgrades and some standalone shows — are not counted. The total reflects only Sports, Music, Arts & Theatre, Family, and Film.
- **Only events with a category and a date are counted.** Events with a category but no genre are grouped under "Unclassified." Events Ticketmaster labels with the genre "Undefined" are grouped the same way. Events missing a category or a date are not counted at all.
- **Date range is capped at two years.** Dates more than two years in the future are rejected as a sanity check. This is not a reflection of Ticketmaster's actual data horizon.
- **No city validation.** The tool relies on the API to match the city name. A typo returns zero results, which triggers the "no events found" message.

## License

This project is not licensed. All rights reserved.

## Acknowledgements

- **Ticketmaster Discovery API** — for providing live event data and a free developer tier.
- **Flask** — for the web application framework.
- **`requests`** — for making HTTP requests to the API.
- **`python-dotenv`** — for loading the API key from a `.env` file.
- **`datetime`** — Python's standard library, used for date parsing and calculation.
- **AI tools** — used for guidance, debugging, documentation assistance and feature development.