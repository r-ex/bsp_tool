from __future__ import annotations
import enum
import io
import struct
from typing import List

from ... import lumps
from ...utils import vector
from .. import base
from .. import colour
from ..valve import source
from . import titanfall


FILE_MAGIC = b"rBSP"

BSP_VERSION = 37

GAME_PATHS = {"Titanfall 2 Tech Test": "Titanfall2_tech_test",
              "Titanfall 2": "Titanfall2"}

GAME_VERSIONS = {"Titanfall 2 Tech Test": 36,
                 "Titanfall 2": 37}


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXTURE_DATA = 0x0002
    VERTICES = 0x0003
    LIGHTPROBE_PARENT_INFOS = 0x0004
    SHADOW_ENVIRONMENTS = 0x0005
    LIGHTPROBE_BSP_NODES = 0x0006
    LIGHTPROBE_BSP_REF_IDS = 0x0007  # indexes? (Mod_LoadLightProbeBSPRefIdxs)
    UNUSED_8 = 0x0008
    UNUSED_9 = 0x0009
    UNUSED_10 = 0x000A
    UNUSED_11 = 0x000B
    UNUSED_12 = 0x000C
    UNUSED_13 = 0x000D
    MODELS = 0x000E
    UNUSED_15 = 0x000F
    UNUSED_16 = 0x0010
    UNUSED_17 = 0x0011
    UNUSED_18 = 0x0012
    UNUSED_19 = 0x0013
    UNUSED_20 = 0x0014
    UNUSED_21 = 0x0015
    UNUSED_22 = 0x0016
    UNUSED_23 = 0x0017
    ENTITY_PARTITIONS = 0x0018
    UNUSED_25 = 0x0019
    UNUSED_26 = 0x001A
    UNUSED_27 = 0x001B
    UNUSED_28 = 0x001C
    PHYSICS_COLLIDE = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    LEAF_WATER_DATA = 0x0024
    UNUSED_37 = 0x0025
    UNUSED_38 = 0x0026
    UNUSED_39 = 0x0027
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    TEXTURE_DATA_STRING_DATA = 0x002B
    TEXTURE_DATA_STRING_TABLE = 0x002C
    UNUSED_45 = 0x002D
    UNUSED_46 = 0x002E
    UNUSED_47 = 0x002F
    UNUSED_48 = 0x0030
    UNUSED_49 = 0x0031
    UNUSED_50 = 0x0032
    UNUSED_51 = 0x0033
    UNUSED_52 = 0x0034
    UNUSED_53 = 0x0035
    WORLD_LIGHTS = 0x0036  # versions 1 - 3 supported (0 might cause a crash, idk)
    WORLD_LIGHT_PARENT_INFOS = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    UNUSED_62 = 0x003E
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIANGLES = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    UNUSED_70 = 0x0046
    VERTEX_UNLIT = 0x0047        # VERTEX_RESERVED_0
    VERTEX_LIT_FLAT = 0x0048     # VERTEX_RESERVED_1
    VERTEX_LIT_BUMP = 0x0049     # VERTEX_RESERVED_2
    VERTEX_UNLIT_TS = 0x004A     # VERTEX_RESERVED_3
    VERTEX_BLINN_PHONG = 0x004B  # VERTEX_RESERVED_4
    VERTEX_RESERVED_5 = 0x004C
    VERTEX_RESERVED_6 = 0x004D
    VERTEX_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORTS = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    UNUSED_84 = 0x0054
    CM_GRID = 0x0055
    CM_GRID_CELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMITIVES = 0x0059
    CM_PRIMITIVE_BOUNDS = 0x005A
    CM_UNIQUE_CONTENTS = 0x005B
    CM_BRUSHES = 0x005C
    CM_BRUSH_SIDE_PLANE_OFFSETS = 0x005D
    CM_BRUSH_SIDE_PROPERTIES = 0x005E
    CM_BRUSH_SIDE_TEXTURE_VECTORS = 0x005F
    TRICOLL_BEVEL_STARTS = 0x0060
    TRICOLL_BEVEL_INDICES = 0x0061
    LIGHTMAP_DATA_SKY = 0x0062
    CSM_AABB_NODES = 0x0063
    CSM_OBJ_REFERENCES = 0x0064
    LIGHTPROBES = 0x0065
    STATIC_PROP_LIGHTPROBE_INDICES = 0x0066
    LIGHTPROBE_TREE = 0x0067
    LIGHTPROBE_REFERENCES = 0x0068
    LIGHTMAP_DATA_REAL_TIME_LIGHTS = 0x0069
    CELL_BSP_NODES = 0x006A
    CELLS = 0x006B
    PORTALS = 0x006C
    PORTAL_VERTICES = 0x006D
    PORTAL_EDGES = 0x006E
    PORTAL_VERTEX_EDGES = 0x006F
    PORTAL_VERTEX_REFERENCES = 0x0070
    PORTAL_EDGE_REFERENCES = 0x0071
    PORTAL_EDGE_INTERSECT_AT_EDGE = 0x0072
    PORTAL_EDGE_INTERSECT_AT_VERTEX = 0x0073
    PORTAL_EDGE_INTERSECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTICES = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFERENCES = 0x0078
    OBJ_REFERENCE_BOUNDS = 0x0079
    LIGHTMAP_DATA_RTL_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESHES = 0x007F


LumpHeader = source.LumpHeader


# known lump changes from Titanfall -> Titanfall 2:
# new:
# UNUSED_4 -> LIGHTPROBE_PARENT_INFOS
# UNUSED_5 -> SHADOW_ENVIRONMENTS
# UNUSED_6 -> LIGHTPROBE_BSP_NODES
# UNUSED_7 -> LIGHTPROBE_BSP_REF_IDS
# UNUSED_55 -> WORLD_LIGHT_PARENT_INFOS
# UNUSED_122 -> LIGHTMAP_DATA_RTL_PAGE
# deprecated:
# LEAF_WATER_DATA
# PHYSICS_LEVEL
# PHYSICS_TRIANGLES

# Rough map of the relationships between lumps:
#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
#             \--> .flags (VertexReservedX)     \--> VertexNormal
#              \-> VertexReservedX               \-> .uv
# MeshBounds & Mesh are parallel
# NOTE: parallel means each entry is paired with an entry of the same index in the parallel lump
# -- this means you can collect only the data you need, but increases the chance of storing redundant data

# ShadowEnvironment -> ShadowMesh -> ShadowMeshIndices -> ShadowMeshOpaqueVertex
#                                                    \-?> ShadowMeshAlphaVertex
# ShadowEnvironments are indexed by entities (light_environment(_volume) w/ lightEnvironmentIndex key)

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# PORTAL LUMPS
# Portal -?> PortalEdge -> PortalVertex
# PortalEdgeRef -> PortalEdge
# PortalVertRef -> PortalVertex
# PortalEdgeIntersect -> PortalEdge?
#                    \-> PortalVertex

# PortalEdgeIntersectHeader -> ???
# PortalEdgeIntersectHeader is parallel w/ PortalEdge
# NOTE: titanfall 2 only seems to care about PortalEdgeIntersectHeader & ignores all other lumps
# -- though this is a code branch that seems to be triggered by something about r1 maps, maybe a flags lump?
# NOTE: there are also always as many vert refs as edge refs
# PortalEdgeRef is parallel w/ PortalVertRef (both 2 bytes per entry, so not 2 verts per edge?)

# ??? WorldLight <-?-> WorldLightParentInfo -?> Model / Entity?

# CM_* LUMPS
# GM_GRID holds world bounds & other metadata

# Cell -?> Primitive | PrimitiveBounds
#     \-?> GeoSet | GeoSetBounds

# Brush -> BrushSidePlane -> Plane
#      \-> BrushSideProperties | BrushSideTextureVector

# BrushSideProps is parallel w/ BrushTexVecs
# Primitives is parallel w/ PrimitiveBounds
# GeoSets is parallel w/ GeoSetBounds
# PrimitiveBounds & GeoSetBounds use the same type (loaded w/ the same function in engine.dll)

# TODO: TRICOLL_* LUMPS
# TODO: LIGHTPROBES
# LightProbeTree -?> LightProbeRef -> LightProbe
# -?> STATIC_PROP_LIGHTPROBE_INDICES


# engine limits:
class MAX(enum.Enum):
    ENTITY_PARTITIONS = 16  # 32 chars per partition name
    MODELS = 1024
    STATIC_PROPS = 57343
    TEXTURES = 2048
    WORLD_LIGHTS = 16352


# flags enums
class GeoSetFlags(enum.IntFlag):
    """Identified by Fifty"""
    BRUSH = 0x00
    TRICOLL = 0x40


# classes for lumps, in alphabetical order::
class GeoSet(base.Struct):  # LUMP 87 (0057)
    unknown: List[int]  # uint16_t[2]
    child: base.BitField  # struct { uint32_t type: 8, index: 16, unknown: 8; };
    # child.unknown: int  # may not be relevant to child
    # child.index: int  # index of Brush / TriCollHeader?
    # child.type: GeoSetFlags  # Brush or TriColl
    __slots__ = ["unknown", "child"]
    _format = "2HI"
    _arrays = {"unknown": 2}
    _bitfields = {"child": {"unknown": 8, "index": 16, "type": 8}}
    _classes = {"child.type": GeoSetFlags}


class LightmapPage(base.Struct):  # LUMP 122 (007A)
    data: bytes
    _format = "128s"
    __slots__ = ["data"]


class LightProbeRef(base.Struct):  # LUMP 104 (0068)
    origin: List[float]  # coords of LightProbe
    lightprobe: int  # index of this LightProbeRef's LightProbe
    unknown: int
    __slots__ = ["origin", "lightprobe", "unknown"]
    _format = "3fIi"
    _arrays = {"origin": [*"xyz"]}


class WorldLightv2(base.Struct):  # LUMP 54 (0036)
    origin: List[float]
    __slots__ = ["origin", "unknown"]
    _format = "3f24I"  # 108 bytes
    _arrays = {"origin": [*"xyz"], "unknown": 24}


class WorldLightv3(base.Struct):  # LUMP 54 (0036)
    origin: List[float]
    unknown: List[int]
    # BobTheBob checked out the v1 -> v3 converter
    # -- it appends (0, 0x3BA3D70A, 0x3F800000) to the tail
    __slots__ = ["origin", "unknown"]
    _format = "3f25I"  # 112 bytes
    _arrays = {"origin": [*"xyz"], "unknown": 25}


class ShadowEnvironment(base.Struct):
    """Identified w/ BobTheBob; appears linked to dynamic shadows and optimisation"""
    # making modifications caused severe framerate drops (2fps)
    unknown_1: List[int]  # likely indices into other lumps (vistree? nodes?) [first_]
    first_shadow_mesh: int  # first ShadowMesh in this ShadowEnvironment
    unknown_2: List[int]  # likely indices into other lumps (vistree? nodes?) [num_]
    num_shadow_meshes: int  # number of ShadowMeshes in this ShadowEnvironment after first_shadow_mesh
    sun_normal: vector.vec3  # represents angle of last light_environment
    __slots__ = ["unknown_1", "first_shadow_mesh", "unknown_2", "num_shadow_meshes", "sun_normal"]
    _format = "6i3f"
    _arrays = {"unknown_1": 2, "unknown_2": 2, "sun_normal": [*"xyz"]}
    _classes = {"sun_normal": vector.vec3}


# classes for special lumps, in alphabetical order:
class StaticPropv13(base.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023) [version 13]
    """Identified w/ BobTheBob"""
    origin: List[float]  # x, y, z
    angles: List[float]  # pitch, yaw, roll (Y Z X)
    scale: float  # indentified by Legion dev DTZxPorter
    model_name: int  # index into GAME_LUMP.sprp.model_names
    solid_mode: int  # bitflags
    flags: int
    unknown: List[int]
    forced_fade_scale: float
    lighting_origin: List[float]  # x, y, z
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: colour.RGBExponent
    collision_flags: List[int]  # add, remove
    # NOTE: no skin or cubemap
    __slots__ = ["origin", "angles", "scale", "model_name", "solid_mode", "flags",
                 "unknown", "forced_fade_scale", "lighting_origin", "cpu_level",
                 "gpu_level", "diffuse_modulation", "collision_flags"]
    _format = "7fH2B4b4f4b4B2H"  # 64 bytes
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "unknown": 4,
               "lighting_origin": [*"xyz"], "cpu_level": ["min", "max"],
               "gpu_level": ["min", "max"], "diffuse_modulation": [*"rgba"],
               "collision_flags": ["add", "remove"]}
    _classes = {"origin": vector.vec3, "solid_mode": titanfall.StaticPropCollision, "flags": source.StaticPropFlags,
                "lighting_origin": vector.vec3, "diffuse_modulation": colour.RGBExponent}
    # TODO: "angles": QAngle


class GameLump_SPRPv13(titanfall.GameLump_SPRPv12):  # sprp GameLump (LUMP 35) [version 13]
    StaticPropClass: object = StaticPropv13
    # little endian only
    model_names: List[str]  # filenames of all .mdl / .rmdl used
    unknown_1: int  # first_transparent?
    unknown_2: int  # first_alpha_sort?
    props: List[StaticPropv13]
    unknown_3: List[bytes]  # array of some unknown struct; sizeof() = 64

    def __init__(self):
        self.model_names = list()
        self.unknown_1 = 0
        self.unknown_2 = 0
        self.props = list()
        self.unknown_3 = list()

    @classmethod
    def from_bytes(cls, raw_lump: bytes):
        sprp_lump = io.BytesIO(raw_lump)
        out = cls()
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        out.model_names = [sprp_lump.read(128).replace(b"\0", b"").decode() for i in range(model_name_count)]
        prop_count = int.from_bytes(sprp_lump.read(4), "little")
        out.unknown_1 = int.from_bytes(sprp_lump.read(4), "little")
        out.unknown_2 = int.from_bytes(sprp_lump.read(4), "little")
        out.props = lumps.BspLump.from_count(sprp_lump, prop_count, cls.StaticPropClass)
        unknown_3_count = int.from_bytes(sprp_lump.read(4), "little")
        out.unknown_3 = [bytearray(sprp_lump.read(64)) for i in range(unknown_3_count)]
        assert all([len(u) == 64 for u in out.unknown_3]), "hit end of lump early while getting unknown_3"
        tail = sprp_lump.read()
        if len(tail) > 0:
            raise RuntimeError(f"sprp lump has a tail of {len(tail)} bytes")
        return out

    def as_bytes(self) -> bytes:
        assert all([isinstance(p, self.StaticPropClass) for p in self.props])
        assert all([len(u) == 64 for u in self.unknown_3])
        return b"".join([len(self.model_names).to_bytes(4, "little"),
                         *[struct.pack("128s", n.encode("ascii")) for n in self.model_names],
                         len(self.props).to_bytes(4, self.endianness),
                         self.unknown_1.to_bytes(4, self.endianness),
                         self.unknown_2.to_bytes(4, self.endianness),
                         *[p.as_bytes() for p in self.props],
                        len(self.unknown_3).to_bytes(4, "little"),
                        *self.unknown_3])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = titanfall.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"CM_GEO_SETS":                         {0: GeoSet},
                     "LIGHTMAP_DATA_REAL_TIME_LIGHTS_PAGE": {0: LightmapPage},
                     "LIGHTPROBE_REFERENCES":               {0: LightProbeRef},
                     "SHADOW_ENVIRONMENTS":                 {0: ShadowEnvironment},
                     "WORLD_LIGHTS":                        {1: titanfall.WorldLight,
                                                             2: WorldLightv2,
                                                             3: WorldLightv3}})

SPECIAL_LUMP_CLASSES = titanfall.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = source.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": {13: GameLump_SPRPv13}}


methods = titanfall.methods.copy()
