import argparse
import json
import math
import os
from dataclasses import asdict, dataclass
from random import random
from typing import List

from pxr import Gf, Usd, UsdGeom
from shapely.affinity import translate
from shapely.geometry import Point, Polygon
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.wrapper import StreamWrapper
# from devtools import debug
from specklepy.objects import Base
from specklepy.objects.geometry import Box, Line, Mesh, Plane, Point
from specklepy.objects.other import RenderMaterial
from specklepy.transports.server import ServerTransport



def strip_numbers_from_string(s):
    # Use a list comprehension to filter out digits
    return ''.join([char for char in s if not char.isdigit()])

def usdz_to_speckle(usdz_file):
    # Open the USDZ file
    stage = Usd.Stage.Open(usdz_file)
    features = []
    

    # Define the eight corners of a unit cube centered at the origin
    unit_cube_corners = [
        Gf.Vec3f(-0.5, -0.5, -0.5),
        Gf.Vec3f(0.5, -0.5, -0.5),
        Gf.Vec3f(-0.5, 0.5, -0.5),
        Gf.Vec3f(0.5, 0.5, -0.5),
        Gf.Vec3f(-0.5, -0.5, 0.5),
        Gf.Vec3f(0.5, -0.5, 0.5),
        Gf.Vec3f(-0.5, 0.5, 0.5),
        Gf.Vec3f(0.5, 0.5, 0.5),
    ]
    

    # Iterate through all prims in the USDZ file
    for prim in stage.Traverse():
        # Check if the prim is a Cube
        prim_name = prim.GetName().lower()
        type = strip_numbers_from_string(str(prim.GetPath().name).lower())
        
        if prim.GetTypeName() == 'Cube'  :
        
            xformable = UsdGeom.Xformable(prim)
            if not xformable:
                continue
            
            # Get the local-to-world transformation matrix
            transform = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())

            transformed_corners = [transform.Transform(point) for point in unit_cube_corners]
            
            features.append((transformed_corners, type))



    return features


# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="Path to the input USDZ file")
args = parser.parse_args()

usdz_features_collection = usdz_to_speckle(args.input)

##### Speckle #####


def order_cube_vertices(vertices):

    center = [sum(coord) / len(vertices) for coord in zip(*vertices)]
    
    # First, separate the vertices into bottom and top groups based on the y-value
    bottom_vertices = [v for v in vertices if v[1] < center[1]]
    top_vertices = [v for v in vertices if v[1] >= center[1]]
    
    # Define a function to calculate the angle for sorting in counterclockwise order
    def angle_for_sorting(v, face_center):
        # Calculate angle from center to vertex
        dx = v[0] - face_center[0]
        dz = v[2] - face_center[2]
        return math.atan2(dz, dx)

    # Calculate centers for the bottom and top faces for angle calculations
    bottom_center = [sum(coord) / len(bottom_vertices) for coord in zip(*bottom_vertices)]
    top_center = [sum(coord) / len(top_vertices) for coord in zip(*top_vertices)]

    # Sort vertices within each group in counterclockwise order when viewed from above/below
    bottom_vertices.sort(key=lambda v: angle_for_sorting(v, bottom_center))
    top_vertices.sort(key=lambda v: angle_for_sorting(v, top_center))

    sorted_vertices = bottom_vertices + top_vertices
    
    # The sorted list should now match the cubePoints structure:
    # Bottom-face vertices first, then top-face vertices, each group sorted from left to right, back to front.
    return [
        sorted_vertices[0], sorted_vertices[1], sorted_vertices[2], sorted_vertices[3],  # Bottom face
        sorted_vertices[4], sorted_vertices[5], sorted_vertices[6], sorted_vertices[7]   # Top face
    ]


def create_mesh(usdz_feature, type):
    sorted_corners_3d = order_cube_vertices(usdz_feature)

    # usdz_feature is a list of 8 Gf.Vec3f object
    # vertices = [] floats 24
    vertices = [component for vec in sorted_corners_3d for component in (vec[2], vec[0], vec[1])]

    faces = [
        4, 0, 1, 5, 4,  # back face
        4, 0, 3, 7, 4,  # left face 
        4, 4, 5, 6, 7,  # front face
        4, 1, 2, 6, 5,  # right face
        4, 0, 0, 0, 0,  # top face
        4, 0, 1, 2, 3   # bottom face
        ]


    return Mesh(vertices=vertices, faces=faces, type=type)


# Initialize the Speckle client
client = SpeckleClient(host="https://app.speckle.systems")

# Get the API token from environment variables
api_token = os.getenv("SPECKLE_API_TOKEN")
if not api_token:
    raise ValueError("API token not found in environment variables")

client.authenticate_with_token(token=api_token)  # Authenticate using the API token
stream_id = "0cbda26868" 

# trnsform the features into speckle objects
speckle_collection_of_mesh = [
    create_mesh(f,j)
    for f,j in usdz_features_collection
]
# create a commit object
commit_obj = Base()
commit_obj["Custom Elements from Python"] = speckle_collection_of_mesh


try:
    # next create a server transport - this is the vehicle through which you will send and receive
    transport = ServerTransport(client=client, stream_id=stream_id)

    # this serialises the block and sends it to the transport
    hash = operations.send(base=commit_obj, transports=[transport])

    # you can now create a commit on your stream with this object
    commid_id = client.commit.create(
        stream_id=stream_id, 
        object_id=hash, 
        message="Imported from USDZ file",
        )
    
except Exception as e:
    print(f"Failed to create the wall: {e}")    