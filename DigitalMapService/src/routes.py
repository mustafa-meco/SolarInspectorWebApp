from flask import render_template, request, jsonify
import datetime
from src import config,app
from flask import Blueprint

# main blueprint to be registered with application
api = Blueprint('api', __name__)

@app.route('/')
@app.route('/processDataFromServiceB', methods=['GET'])
def process_data_from_service_b():
    import requests

    # Make a GET request to Service B's API endpoint
    response = requests.get('http://localhost:5000/getSatelliteData')  # Assuming Service B is running locally on port 5000

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        # Process the retrieved data as needed
        print(data)  # For example, print the data
        # Return the processed data as a response to the client or do further processing
        return "Data processed successfully"
    else:
        # Handle error
        return "Failed to retrieve data from Service B"

