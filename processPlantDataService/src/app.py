from flask import Flask, render_template, request, jsonify
from lib.CADUtils import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploadCAD', methods=['POST'])
def uploadCAD():
    dxf_file = request.files['file']
    layer_name = request.form['layer_name']
    output_json_file = request.form['output_json_file']
    if not output_json_file.endswith('.json'):
        output_json_file += '.json'

    dxf_file.save(dxf_file.filename)
    lwpolylines = extract_lwpolylines_from_layer(dxf_file.filename, layer_name)
    save_lwpolylines_to_json(lwpolylines, output_json_file)

    return render_template('plotly_page.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the DXF file data from the request body
        dxf_data = request.data

        # Save the DXF data to a temporary file
        with open('temp.dxf', 'wb') as f:
            f.write(dxf_data)

        layer_name = request.args.get('layer_name')  # Assuming layer_name is provided as a query parameter

        # Extract LWPOLYLINE entities from the specified layer
        lwpolylines = extract_lwpolylines_from_layer('temp.dxf', layer_name)

        # Clean up the temporary DXF file
        os.remove('temp.dxf')

        # Convert LWPOLYLINE entities to JSON
        json_data = lwpolylines_to_json(lwpolylines)

        return jsonify(json_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
