from flask import render_template, request, jsonify
from src.lib.CADUtils import *
import datetime
from src import app, config
from flask import Blueprint

# main blueprint to be registered with application
api = Blueprint('api', __name__)

@app.route('/')
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