# https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
# TODO: see modding tools: cod2map.exe -info
import enum

from .. import shared


FILE_MAGIC = b"IBSP"

BSP_VERSION = 22

GAME_PATHS = ["Call of Duty 4: Modern Warfare"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


# NOTE: lumps are given ids and headers reference these ids in order
class LUMP(enum.Enum):
    SHADERS = 0x00
    LIGHTMAPS = 0x01
    LIGHT_GRID_POINTS = 0x02
    LIGHT_GRID_COLOURS = 0x03
    PLANES = 0x04
    BRUSH_SIDES = 0x05
    UNKNOWN_6 = 0x06
    UNKNOWN_7 = 0x07
    BRUSHES = 0x08
    LAYERED_TRIANGLE_SOUPS = 0x09
    LAYERED_VERTICES = 0x0A
    LAYERED_INDICES = 0x0B
    PORTAL_VERTICES = 0x13
    LAYERED_AABB_TREE = 0x18
    CELLS = 0x19
    PORTALS = 0x1A
    NODES = 0x1B
    LEAVES = 0x1C
    LEAF_BRUSHES = 0x1D
    LEAF_SURFACES = 0x1E  # unused?
    COLLISION_VERTICES = 0x1F
    COLLISION_TRIANGLES = 0x20
    COLLISION_EDGE_WALK = 0x21
    COLLISION_BORDERS = 0x22
    COLLISION_PARTS = 0x23
    COLLISION_AABBS = 0x24
    MODELS = 0x25
    ENTITIES = 0x27
    PATHS = 0x28
    REFLECTION_PROBES = 0x29  # textures? pretty huge
    LAYERED_DATA = 0x2A
    PRIMARY_LIGHTS = 0x2B
    LIGHT_GRID_HEADER = 0x2C
    LIGHT_GRID_ROWS = 0x2D
    SIMPLE_TRIANGLE_SOUPS = 0x2F
    SIMPLE_VERTICES = 0x30
    SIMPLE_INDICES = 0x31
    SIMPLE_AABB_TREE = 0x33
    LIGHT_REGIONS = 0x34
    LIGHT_REGION_HULLS = 0x35
    LIGHT_REGION_AXES = 0x36


# Known lump changes from Call of Duty 2 -> Call of Duty 4:
# New:
#   LIGHT_GRID_HASHES -> LIGHT_GRID_POINTS
#   LIGHT_GRID_VALUES -> LIGHT_GRID_COLOURS
#   UNKNOWN_6
#   UNKNOWN_7
#   TRIANGLE_SOUPS -> LAYERED_TRIANGLE_SOUPS & SIMPLE_TRIANGLE_SOUPS
#   VERTICES -> LAYERED_VERTICES & SIMPLE_VERTICES
#   TRIANGLES -> LAYERED_INDICES & SIMPLE_INDICES ?
#   AABB_TREE -> LAYERED_AABB_TREE & SIMPLE_AABB_TREE
#   COLLISION_EDGES -> COLLISION_EDGE_WALK ?
#   REFLECTION_PROBES
#   LAYERED_DATA
#   PRIMARY_LIGHTS
#   LIGHT_GRID_HEADER
#   LIGHT_GRID_ROWS
#   LIGHT_REGIONS
#   LIGHT_REGION_HULLS
#   LIGHT_REGION_AXES
# Deprecated:
#   CULL_GROUPS
#   CULL_GROUP_INDICES  # NOTE: func_cull_group is still present...

# TODO: a rough map of the relationships between lumps:


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {"LIGHT_GRID_POINTS": shared.UnsignedInts,
                      "LIGHT_REGIONS":     shared.UnsignedBytes}

LUMP_CLASSES = {}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}


methods = [shared.worldspawn_volume]
