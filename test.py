import os
from dataclasses import dataclass, asdict
from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.objects.geometry import Point
from specklepy.objects.geometry import Mesh

from random import random
from typing import List
# from devtools import debug
from specklepy.objects import Base
from specklepy.objects.geometry import Box, Line, Point, Plane
from specklepy.api.wrapper import StreamWrapper
from specklepy.api import operations
from specklepy.objects.other import RenderMaterial


    
def create_mesh(length, height, thickness):
    
    half = 2
    vertices = [
        -half, -half, -half,  # vertex 0: left-bottom-back
        half, -half, -half,   # vertex 1: right-bottom-back
        half, half, -half,    # vertex 2: right-top-back
        -half, half, -half,   # vertex 3: left-top-back
        -half, -half, half,   # vertex 4: left-bottom-front
        half, -half, half,    # vertex 5: right-bottom-front
        half, half, half,     # vertex 6: right-top-front
        -half, half, half     # vertex 7: left-top-front
    ]

    # format:  4, v, v, v,
    faces = [
        4, 0, 1, 5, 4,  # back face
        4, 0, 3, 7, 4,  # left face 
        4, 4, 5, 6, 7,  # front face
        4, 1, 2, 6, 5,  # right face
        4, 3, 2, 6, 7,  # top face
        4, 0, 1, 2, 3   # bottom face
    ]


    return Mesh(vertices=vertices, faces=faces)





# Initialize the Speckle client
client = SpeckleClient(host="https://app.speckle.systems")

# Get the API token from environment variables
api_token = os.getenv("SPECKLE_API_TOKEN")
if not api_token:
    raise ValueError("API token not found in environment variables")

client.authenticate_with_token(token=api_token)  # Authenticate using the API token
stream_id = "0cbda26868" 


elements = [
    create_mesh(1,1,1)
]
# create a commit object
commit_obj = Base()
commit_obj["Custom Elements from Python"] = elements


try:

    # next create a server transport - this is the vehicle through which you will send and receive
    transport = ServerTransport(client=client, stream_id=stream_id)

    # this serialises the block and sends it to the transport
    hash = operations.send(base=commit_obj, transports=[transport])

    # you can now create a commit on your stream with this object
    commid_id = client.commit.create(
        stream_id=stream_id, 
        object_id=hash, 
        message="Test Pablo",
        )
    
except Exception as e:
    print(f"Failed to create the cube: {e}")

