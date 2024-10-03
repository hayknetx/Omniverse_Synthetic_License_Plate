# DT SCENE DIRECTORY
DT_SCENE_DIRECTORY = "usd_scene/Collected_scene/scene.usd"

# Camera Resolution
RESOLUTION = (1080, 720)  # 1080P Resolution default

# Number of Samples Per Pixel for PathTracing
SPP = 1024 # default: 1024

# Framerate of vehicles; switch this to 60 once new anims are imported
FPS = 24.0 # default: 24.0

# Number of Samples to Generate
SDG_SAMPLES = 5000 # default: 5000

# Length of Video (in minutes)
SDG_RECORD_LENGTH = 5 # default: 5

# How to render the scene (RayTracedLighting VS PathTracing)
RENDERMODE = "PathTracing"  # default: "PathTracing"

# LATITUDE of DT Location
LAT = 35.915170377962724

# LONGITUDE of DT Location
LON = 14.495216967442692

# List of Vehicle prims
VEHICLES_PATH = "/Root/World/Vehicles_Xform"

# List of Camera prims
CAM_PATH = "/Root/Cameras_ALPR"

# All light objects in the scene
LIGHTS_PATH = "/Root/World/Lights_Xform"

# Path to Materials in the scene
MATERIALS_PATH = "/Root/World/Plate_Materials/"

# Path to available fonts
FONT_PATH = "scene_utils/fonts"

# Indian Regions Data Path
RTO_DATA_PATH = "scene_utils/regions.txt"

# Generated License Plate Texture paths
PLATE_TEX_PATH = "scene_utils/generated/"

# Some defaults for plate damage
DEFAULT_SCRATCH_VALUE = 0.05 # default: 0.05
DEFAULT_DIRT_VALUE = 0.1 # default: 0.1

# Save Directory
SAVE_DIR = "synth_out/"

# Instructions on how to format date/time
STRF_DATE = "%d-%m-%Y"
STRF_DATETIME = "%d-%m-%Y_%H-%M-%S"