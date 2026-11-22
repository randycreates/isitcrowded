"""Flask entry point for the Is It Crowded web app."""
from flask import Flask, render_template, request
from isitcrowded import count_events, max_search_date, min_search_date


# Create a Flask application instance
app = Flask(__name__)


# Define a route and its handler function
@app.route("/", methods=["GET", "POST"])
def is_it():
    """Render the search form, or run the search and show results."""
    if request.method == "POST":
        city = request.form["city"]
        date = request.form["date"]

        try:
            counts = count_events(city, date)
        except ValueError as e:
            # Process the data here
            return render_template(
                "index.html",
                error=str(e),
                max_date=max_search_date(),
                min_date=min_search_date(),
            )
        return render_template("results.html", **counts)

    return render_template(
        "index.html", max_date=max_search_date(), min_date=min_search_date()
    )


# Run the application if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)
