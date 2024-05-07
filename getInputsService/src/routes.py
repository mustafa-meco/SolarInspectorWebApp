from flask import render_template, request, jsonify
from src.lib.CADUtils import *
import datetime
from src import app, config
from flask import Blueprint

# main blueprint to be registered with application
api = Blueprint('api', __name__)

@app.route('/t')
def index():
    return render_template('index.html')

@app.route('/uploadCAD', methods=['POST'])
def uploadCAD():
    dxf_file = request.files['file']
    dxf_file.save(f'src/dxf/{dxf_file.filename}')
    return render_template('choose_dxf.html')

@app.route('/processCAD', methods=['POST'])
def processCAD():
    dxf_filename = request.form['filename']
    # print(dxf_filename)
    layer_name = request.form['layer_name']
    modelspace = read_dxf_file(f"src/dxf/{dxf_filename}")
    lwpolylines = extract_lwpolylines_from_layer(modelspace, layer_name)
    current_time = datetime.datetime.now()
    day_and_time = current_time.strftime("%A_%H_%M")
    save_lwpolylines_to_json(lwpolylines, f"src/jsons/lwpolylines-{day_and_time}.json")
    return jsonify(extract_lwpolylines_from_layer(modelspace, layer_name))

@app.route('/processCADweb', methods=['POST'])
def processCADweb():
    dxf_filename = request.form['filename']
    # print(dxf_filename)
    layer_name = request.form['layer_name']
    modelspace = read_dxf_file(f"src/dxf/{dxf_filename}")
    lwpolylines = extract_lwpolylines_from_layer(modelspace, layer_name)
    current_time = datetime.datetime.now()
    day_and_time = current_time.strftime("%A_%H_%M")
    save_lwpolylines_to_json(lwpolylines, f"src/jsons/lwpolylines-{day_and_time}.json")
    return render_template('choose_json.html')

@app.route('/getDxfFiles', methods=['GET'])
def getDxfFiles():
    return jsonify(get_dxf_files())

@app.route('/getJsonFiles', methods=['GET'])
def getJSONFiles():
    print(get_json_files())
    return jsonify(get_json_files())

@app.route('/choose_dxf', methods=['GET'])
def choose_dxf():
    return render_template('choose_dxf.html')

@app.route('/choose_json', methods=['GET'])
def choose_json():
    return render_template('choose_json.html')

@app.route('/plotlyfile', methods=['POST'])
def plotlyfile():
    json_file = request.form['json_file']
    f = open(f"src/jsons/{json_file}", 'r')
    data = json.load(f)
    f.close()
    with open('data.json', 'w') as f2:
        json.dump(data, f2)
    
    return render_template('plotly_page.html')

# route to return json file based on its name
@app.route('/getJsonFile', methods=['POST'])
def getJsonFile():
    print(request.data)
    json_file = "data.json"
    with open(json_file, 'r') as f:
        data = json.load(f)
    return jsonify(data)

# get json file by name endpoint
@app.route('/getJsonFileByName', methods=['POST'])
def getJsonFileByName():
    json_file = request.get_json()['filename']
    print(json_file)
    print(json_file)
    with open(f"src/jsons/{json_file}", 'r') as f:
        data = json.load(f)
    return jsonify(data)


# Define a route for the web page
@app.route('/')
def upload_image_page():
    return render_template('satellite_input.html')

# Define a route to handle form submission
import json

@app.route('/uploadImage', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        # Retrieve data from the form
        image_file = request.files['imageFile']
        latitude_upper_left = request.form['latitude']
        longitude_upper_left = request.form['longitude']
        latitude_lower_right = request.form['latitudeLower']
        longitude_lower_right = request.form['longitudeLower']

        # Create a dictionary to store the data
        data = {
            'image_file': image_file.filename,
            'latitude_upper_left': latitude_upper_left,
            'longitude_upper_left': longitude_upper_left,
            'latitude_lower_right': latitude_lower_right,
            'longitude_lower_right': longitude_lower_right
        }

        # Print the data for verification
        print('Data:', data)

        # Save the data to a JSON file
        file_path = os.path.join('src', 'jsons', 'satellite_data.json')
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)

        # Here you can save the image and its details to a database or perform any other necessary actions

        return 'Image uploaded successfully!'

@app.route('/getSatelliteData', methods=['GET'])
def getSatelliteData():
    json_file_path = 'src/jsons/satellite_data.json'
    if os.path.exists(json_file_path):
        # Read the contents of the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        return jsonify(data)
    else:
        return 'JSON file not found', 404
