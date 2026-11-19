from isitcrowded import dates, data_set, API_KEY
from flask import Flask, render_template, request

# Create a Flask application instance
app = Flask(__name__)


# Define a route and its handler function
@app.route('/', methods=['GET', 'POST'])
def is_it():
    if request.method == 'POST':
        city = request.form['city']
        date = request.form['date']

        try:
            start_iso, end_iso, end_date = dates(date)
        except ValueError as e:
            # Process the data here
            return render_template('index.html', error=str(e))

        filters = {
            "apikey": API_KEY,
            "city": city,
            "startDateTime": start_iso,
            "endDateTime": end_iso,
            "size": 200,
            "page": 0,
        }
    return render_template('index.html')


# Run the application if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)
