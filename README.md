# LiDARtoBIM

#BeyondTheSpeckleverse Project 🚀👾

## Project Description  
Our project leverages the powerful LiDAR technology available on smartphone (such as iPhone) to perform accurate 3D scans of real-world environments. These scans are exported as USDZ files and uploaded to Speckle using a custom connector written in Python.  
Once the scanned model lives in Speckle, we can transform the model's geometries into Revit objects using Speckle Dynamo nodes, facilitating seamless integration into BIM workflows.

## How it works

### Technical Stack

- **Hardware:** Phone with LiDAR capability. (We used an iPhone 15 Pro)  
- **Software:**  
    - Python for uploading USDZ files to Speckle.  
    - Speckle platform for data storage and management.  
    - Dynamo for Revit to process and convert Speckle data into Revit objects.  
    - Revit for final BIM model integration.

### Workflow:
1. **Scanning:**  
    - Use a phone that counts with LiDAR technology to scan the environment and export the 3D model in USDZ format.  

2. **Uploading to Speckle:**  
    - Run our custom connector written in Python to push the scanned geometries (USDZ file) to Speckle.  
    - Example Python code snippet for uploading to Speckle: 

       Required ENV vars:

            export SPECKLE_API_TOKEN="############"

        Setup:

            pip install specklepy

        Run:

            python ./test.py

4. **Conversion to Revit:**  
    - Copy stream link from Speckle project and Paste into Dynamo Script. (It can be run using Dynamo Player)  
    - The Dynamo script uses Speckle nodes to fetch the geometries from Speckle and convert them into Revit objects.  
    - Example Dynamo script - Wall components:  
        - `**sample gif**`  
    - Perform any necessary adjustments and validations within Revit.
 
# Links
- Youtube presentation
- Speckle Project

# Team  
- [Agustina Aboy](https://github.com/agusaboy) // Architect & BIM Specialist ![ContactTina](https://img.shields.io/badge/Contact%20Tina-2a9190?link=https%3A%2F%2Flinktr.ee%2Fagusaboy)
- [Emilio Bartolini](https://github.com/emiliobmhm) // Geometry Geek
- [Martin Daguerre](https://github.com/mdaguerre)// Lagarsoft  
- [Pablo Gancharov](https://github.com/PabloGancharov) // Lagarsoft  
- [Julio Sarachaga](https://github.com/julillosamaral) // Lagarsoft 

![Lagarsoft web](https://img.shields.io/badge/Lagarsoft%20web-2a2d6f?link=https%3A%2F%2Fwww.lagarsoft.com%2F)

