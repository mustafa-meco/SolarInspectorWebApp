import ezdxf
import json
import os

def extract_lwpolylines_from_layer(modelspace, layer_name):
    lwpolylines = []
    for entity in modelspace:
        if entity.dxftype() == 'LWPOLYLINE' and entity.dxf.layer == layer_name:
            # Extract points from LWPolyline
            points = [(vertex[0], vertex[1]) for vertex in entity.get_points('xy')]
            # Sort points by Y then X values
            sorted_points = sorted(points, key=lambda p: (p[1], p[0]))
            lwpolylines.append(sorted_points)

    return lwpolylines

def read_dxf_file(dxf_file):
    doc = ezdxf.readfile(dxf_file)
    modelspace = doc.modelspace()
    return modelspace

def get_entities(modelspace, layer_name):
    entities = []
    for entity in modelspace:
        if entity.dxf.layer == layer_name:
            entities.append(entity.dxf.__dict__)
    return entities


def get_dxf_files():
    return [f for f in os.listdir('src/dxf') if f.endswith('.dxf')]
def get_json_files():
    return [f for f in os.listdir('src/jsons') if f.endswith('.json')]

# Function to save LWPOLYLINE points to JSON file
def save_lwpolylines_to_json(lwpolylines, output_file):
    print(output_file)
    with open(output_file, 'w') as f:
        json.dump(lwpolylines, f, indent=4)

# Function to map points from the minimum point to (0,0) and other points respectively
def map_points(lwpolylines):
    min_x = min(point[0] for polyline in lwpolylines for point in polyline)
    min_y = min(point[1] for polyline in lwpolylines for point in polyline)

    mapped_lwpolylines = []
    for polyline in lwpolylines:
        mapped_polyline = [(point[0] - min_x, point[1] - min_y) for point in polyline]
        mapped_lwpolylines.append(mapped_polyline)

    return mapped_lwpolylines


