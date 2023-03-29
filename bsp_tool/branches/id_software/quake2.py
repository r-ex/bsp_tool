# https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
# https://github.com/id-Software/Quake-2/blob/master/qcommon/qfiles.h#L214
import enum
import io
import itertools
import struct
from typing import List

from . import quake
from .. import base
from .. import shared


FILE_MAGIC = b"IBSP"

BSP_VERSION = 38

GAME_PATHS = {"Anachronox": "Anachronox", "Quake II": "Quake 2", "Heretic II": "Heretic II",
              "D-Day Normandy": "D-Day_ Normandy/dday"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    VERTICES = 2
    VISIBILITY = 3
    NODES = 4
    TEXTURE_INFO = 5
    FACES = 6
    LIGHTMAPS = 7
    LEAVES = 8
    LEAF_FACES = 9
    LEAF_BRUSHES = 10
    EDGES = 11
    SURFEDGES = 12
    MODELS = 13
    BRUSHES = 14
    BRUSH_SIDES = 15
    POP = 16  # QuakeII/pak1 only (multiplayer / deathmatch?)
    AREAS = 17
    AREA_PORTALS = 18


LumpHeader = quake.LumpHeader


# known lump changes from Quake 2 -> Quake 3:
# new:
#   LEAF_BRUSHES
#   BRUSHES
#   BRUSH_SIDES
#   POP
#   AREAS
#   AREA_PORTALS
# deprecated:
#   MIP_TEXTURES
#   CLIP_NODES


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                                \-> LeafBrush -> Brush

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#     /-> Plane
# Face -> SurfEdge -> Edge -> Vertex
#    \--> TextureInfo
#     \-> Lightmap

# POP appears to only be used in Deathmatch maps & is always 256 bytes, cannot find use in source code
# POP seems to be the last lump written and is always null bytes in every map which has this lump


# engine limits:
class MAX(enum.Enum):
    # lumps
    AREAS = 256
    AREA_PORTALS = 1024
    BRUSHES = 8192
    BRUSH_SIDES = 65536
    EDGES = 128000
    ENTITIES = 2048
    FACES = 65536
    LEAF_BRUSHES = 65536
    LEAF_FACES = 65536
    LEAVES = 65536
    LIGHTMAPS_SIZE = 0x200000  # bytesize
    MODELS = 1024
    NODES = 65536
    PLANES = 65536
    # NOTE: no POP limit
    SURFEDGES = 256000
    TEXTURE_INFO = 8192
    VERTICES = 65535
    VISIBILITY_SIZE = 0x100000  # bytesize
    # other
    ENTITY_KEY = 32
    ENTITY_VALUE = 1024


# flag enums:
class Contents(enum.IntFlag):
    """https://github.com/xonotic/darkplaces/blob/master/bspfile.h"""
    SOLID = 0x00000001  # opaque & transparent
    WINDOW = 0x00000002
    AUX = 0x00000004
    LAVA = 0x00000008
    SLIME = 0x00000010
    WATER = 0x00000020
    MIST = 0x00000040  # FOG?
    AREA_PORTAL = 0x00008000
    PLAYER_CLIP = 0x00010000
    MONSTER_CLIP = 0x00020000
    # bot hints
    CURRENT_0 = 0x00040000
    CURRENT_90 = 0x00080000
    CURRENT_180 = 0x00100000
    CURRENT_270 = 0x00200000
    CURRENT_UP = 0x00400000
    CURRENT_DOWN = 0x00800000
    # end bot hints
    ORIGIN = 0x01000000  # removed during compile
    MONSTER = 0x02000000
    DEAD_MONSTER = 0x04000000
    DETAIL = 0x08000000
    TRANSLUCENT = 0x10000000  # vis splitting brushes
    LADDER = 0x20000000


class Surface(enum.IntFlag):  # qcommon/qfiles.h
    """TextureInfo flags"""  # NOTE: vbsp sets these in src/utils/vbsp/textures.cpp
    LIGHT = 0x0001  # "value will hold the light strength"
    SLICK = 0x0002  # affects game physics (spelt "effects in source")
    SKY = 0x0004  # don't draw, but add to skybox
    WARP = 0x0008  # turbulent water warp
    TRANS33 = 0x0010  # 1/3 transparency?
    TRANS66 = 0x0020  # 2/3 transparency?
    FLOWING = 0x0040  # "scroll towards angle"
    NO_DRAW = 0x0080  # "don't bother referencing the texture"


# classes for lumps, in alphabetical order:
class Brush(base.MappedArray):  # LUMP 14
    first_side: int
    num_sides: int
    contents: int
    _mapping = ["first_side", "num_sides", "contents"]
    _format = "3i"


class BrushSide(base.MappedArray):  # LUMP 15
    plane: int
    texture_info: int
    _format = "Hh"


class Leaf(base.Struct):  # LUMP 10
    type: int  # see LeafType enum
    cluster: int  # index into the VISIBILITY lump
    area: int
    bounds: List[int]
    first_leaf_face: int  # index to this Leaf's first LeafFace
    num_leaf_faces: int  # the number of LeafFaces after first_face in this Leaf
    first_leaf_brush: int  # index to this Leaf's first LeafBrush
    num_leaf_brushes: int  # the number of LeafBrushes after first_brush in this Leaf
    __slots__ = ["type", "cluster", "area", "bounds", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes"]
    _format = "I12H"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


class Model(base.Struct):  # LUMP 13
    bounds: List[float]  # mins & maxs
    origin: List[float]
    first_node: int  # first node in NODES lumps
    first_face: int
    num_faces: int
    __slots__ = ["bounds", "origin", "first_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"]}


class Node(base.Struct):  # LUMP 4
    plane_index: int
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 0) is a dummy leaf & terminates tree searches
    bounds: List[int]
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int
    num_faces: int
    _format = "I2i8h"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


class TextureInfo(base.Struct):  # LUMP 5
    U: List[float]
    V: List[float]
    flags: int  # "miptex flags & overrides"
    value: int  # "light emission etc."
    name: bytes  # texture name
    next_frame: int  # index into TextureInfo lump for animations (-1 = last frame)
    __slots__ = ["U", "V", "flags", "value", "name", "next_frame"]
    _format = "8f2I32sI"
    _arrays = {"U": [*"xyzw"], "V": [*"xyzw"]}


# special lump classes, in alphabetical order:
class Visibility:
    """Developed with maxdup"""
    # https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
    # NOTE: cluster index comes from Leaf.cluster
    # -- https://github.com/ericwa/ericw-tools/blob/master/vis/vis.cc
    # -- https://github.com/ericwa/ericw-tools/blob/master/common/bspfile.cc#L4378-L4439
    # -- not RLE encoded in Source Engine branches?
    pvs: List[bytes]  # Potential Visible Set
    pas: List[bytes]  # Potential Audible Set
    # TODO: List[bool] -> bytes
    # -- sum([2 ** i if b else 0 for i, b in enumerate(x)]).to_bytes(len(x) // 8 + 1 if len(x) % 8 != 0 else 0, "big")
    # TODO: bytes -> List[bool]
    # -- [b == "1" for b in f"{int.from_bytes(x, 'big'):b}"[::-1]]

    def __init__(self, pvs_table: List[List[bool]] = tuple(), pas_table: List[List[bool]] = tuple()):
        self.pvs = pvs_table
        self.pas = pas_table

    @classmethod
    def from_bytes(cls, raw_lump: bytes):
        _buffer = io.BytesIO(raw_lump)
        num_clusters = int.from_bytes(_buffer.read(4), "little")
        offsets = list(struct.iter_unpack("2I", _buffer.read(8 * num_clusters)))
        pvs, pas = list(), list()
        for pvs_offset, pas_offset in offsets:
            _buffer.seek(pvs_offset)
            pvs.append(cls.run_length_decode(_buffer, num_clusters))
            _buffer.seek(pas_offset)
            pas.append(cls.run_length_decode(_buffer, num_clusters))
            # TODO: treat bytes as List[bool]
        return cls(pvs, pas)

    @staticmethod
    def run_length_decode(stream: io.BytesIO, num_clusters: int) -> bytes:
        # https://github.com/ericwa/ericw-tools/blob/master/common/bspfile.cc#L4412-L4439
        out = list()
        out_size = num_clusters // 8 + 1 if num_clusters % 8 else 0
        while(len(out) < out_size):
            byte = stream.read(1)
            if byte != 0:
                out.append(byte)
                continue
            count = stream.read(1)
            assert count != 0, "stream is not compressed"
            out.extend([0] * count)
        return b"".join(out)

    @staticmethod
    def run_length_encode(data: bytes) -> bytes:
        # https://github.com/ericwa/ericw-tools/blob/master/common/bspfile.cc#L4382-L4404
        out = list()
        i = 0
        while (i < len(data)):
            byte = data[i]
            i += 1
            if byte != 0:
                out.append(byte)
                continue
            count = 1
            while data[i] == 0 and count < 255 and i < len(data):
                count += 1
                i += 1
            out.extend([0, count])
        return bytes(out)

    def as_bytes(self) -> bytes:
        # TODO: test
        # TODO: reduce pvs & pas to a set of each unique flag sequence
        # -- then index that fixed list of pvs/pas flags for extra compression
        assert len(self.PVS) == len(self.PAS)
        num_clusters = len(self.PVS)
        compressed_pvs = [self.run_length_encode(d) for d in self.PVS]
        compressed_pas = [self.run_length_encode(d) for d in self.PAS]
        pvs_offsets = [4 + sum(map(len, compressed_pvs[:i])) for i in range(num_clusters)]
        offset = pvs_offsets[-1] + len(compressed_pvs[-1])
        pas_offsets = [offset + sum(map(len, compressed_pas[:i])) for i in range(num_clusters)]
        header = [num_clusters, *itertools.chain(*zip(pvs_offsets, pas_offsets))]
        data = list(itertools.chain(*zip(compressed_pvs, compressed_pas)))
        return b"".join([*[x.to_bytes(4, "little") for x in header], *data])


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {"LEAF_FACES": shared.Shorts,
                      "SURFEDGES":  shared.Ints}

LUMP_CLASSES = {"BRUSHES":      Brush,
                "BRUSH_SIDES":  BrushSide,
                "EDGES":        quake.Edge,
                "FACES":        quake.Face,
                "LEAVES":       Leaf,
                "MODELS":       Model,
                "NODES":        Node,
                "PLANES":       quake.Plane,
                "TEXTURE_INFO": TextureInfo,
                "VERTICES":     quake.Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES":   shared.Entities,
                        "VISIBILITY": Visibility}


methods = [shared.worldspawn_volume]
