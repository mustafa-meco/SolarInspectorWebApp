import ezdxf
import json

# Function to extract LWPOLYLINE points from DXF file
def extract_lwpolylines_from_layer(dxf_file, layer_name):
    doc = ezdxf.readfile(dxf_file)
    modelspace = doc.modelspace()

    lwpolylines = []
    for entity in modelspace:
        if entity.dxftype() == 'LWPOLYLINE' and entity.dxf.layer == layer_name:
            # Extract points from LWPolyline
            points = [(vertex[0], vertex[1]) for vertex in entity.get_points('xy')]
            # Sort points by Y then X values
            sorted_points = sorted(points, key=lambda p: (p[1], p[0]))
            lwpolylines.append(sorted_points)

    return lwpolylines

# Function to save LWPOLYLINE points to JSON file
def save_lwpolylines_to_json(lwpolylines, output_file):
    with open(output_file, 'w') as f:
        json.dump(map_points(lwpolylines), f, indent=4)

# Function to map points from the minimum point to (0,0) and other points respectively
def map_points(lwpolylines):
    min_x = min(point[0] for polyline in lwpolylines for point in polyline)
    min_y = min(point[1] for polyline in lwpolylines for point in polyline)

    mapped_lwpolylines = []
    for polyline in lwpolylines:
        mapped_polyline = [(point[0] - min_x, point[1] - min_y) for point in polyline]
        mapped_lwpolylines.append(mapped_polyline)

    return mapped_lwpolylines

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     dxf_file = request.files['file']
#     layer_name = request.form['layer_name']
#     output_json_file = request.form['output_json_file']
#     if not output_json_file.endswith('.json'):
#         output_json_file += '.json'

#     dxf_file.save(dxf_file.filename)
#     lwpolylines = extract_lwpolylines_from_layer(dxf_file.filename, layer_name)
#     save_lwpolylines_to_json(lwpolylines, output_json_file)

#     return render_template('plotly_page.html')
