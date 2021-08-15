__all__ = ["id_software", "infinity_ward", "nexon", "respawn", "valve",
           "by_magic", "by_name", "by_version"]

from . import id_software
from . import infinity_ward
from . import nexon
from . import respawn
from . import valve


__doc__ = """Index of developers of bsp format variants"""

FILE_MAGIC_developer = {b"IBSP": [id_software, infinity_ward],
                        b"rBSP": respawn,
                        b"VBSP": [nexon, valve]}

# NOTE: bsp_tool/__init__.py: load_bsp can be fed a string to select the relevant branch script
# by_name is searched with a lowercase, numbers & letters only version of that string
# NOTE: some (but not all!) games are listed here have multiple valid names (including internal mod names)
# TODO: generate from branch.GAMES (folder names)
by_name = {
    # Id Software - Id Tech 2
    "quake": id_software.quake,
    # TODO: test QuakeWorld
    # TODO: figure out which source ports are supported
    # Id Software - Id Tech 3
    "quake3": id_software.quake3,
    "quakeiii": id_software.quake3,
    # TODO: Quake Live
    # Infinity Ward - IW Engine(s)
    "callofduty": infinity_ward.call_of_duty1,
    "cod": infinity_ward.call_of_duty1,
    # NEXON - Source Engine
    "counterstrikeonline2": nexon.cso2,
    "cso2": nexon.cso2,
    "csonline2": nexon.cso2,
    "mabinogi": nexon.vindictus,
    "mabinogiheroes": nexon.vindictus,
    "vindictus": nexon.vindictus,
    # Respawn Entertainment - Source Engine
    "apex": respawn.apex_legends,
    "apexlegends": respawn.apex_legends,
    "r1": respawn.titanfall,
    "r2": respawn.titanfall2,
    "r5": respawn.apex_legends,
    "titanfall": respawn.titanfall,
    "titanfall2": respawn.titanfall2,
    # NOTE: "tf|2" (Titanfall 2) is converted to "tf2" (Team Fortress 2)
    # Valve Software - Source Engine
    "csgo": valve.cs_go,  # untested
    "css": valve.cs_source,  # untested
    "cssource": valve.cs_source,
    "globaloffensive": valve.cs_go,
    # Valve Software - Source Engine: Orange Box
    "orangebox": valve.orange_box,
    "teamfortress2": valve.orange_box,
    "tf2": valve.orange_box,
    # TODO: test the following: (+ more mods @ https://half-life.fandom.com/wiki/Mods)
    "episode1": valve.orange_box,
    "episode2": valve.orange_box,
    "halflife2": valve.orange_box,
    "halflife2ep1": valve.orange_box,
    "halflife2ep2": valve.orange_box,
    "halflife2episode1": valve.orange_box,
    "halflife2episode2": valve.orange_box,
    "hl2": valve.orange_box,
    "hl2ep1": valve.orange_box,
    "hl2ep2": valve.orange_box,
    "portal": valve.orange_box,
    # NOTE: probably not orange_box:
    "l4d": valve.orange_box,
    "l4d2": valve.orange_box,
    "left4dead": valve.orange_box,
    "left4dead2": valve.orange_box,
    "portal2": valve.orange_box,
    # Valve Software - GoldSrc Engine
    "goldsrc": valve.goldsrc,
    "halflife": valve.goldsrc,
    # TODO: test the following: (+ more mods @ https://half-life.fandom.com/wiki/Mods)
    "007nightfire": valve.goldsrc,
    "blueshift": valve.goldsrc,
    "counterstrike": valve.goldsrc,  # CS 1.6
    "counterstrikeconditionzero": valve.goldsrc,
    "counterstrikeneo": valve.goldsrc,  # obscure
    "counterstrikeonline": valve.goldsrc,  # obscure
    "cs": valve.goldsrc,  # CS 1.6
    "cscz": valve.goldsrc,
    "csn": valve.goldsrc,  # obscure
    "cso": valve.goldsrc,  # obscure
    "dayofdefeat": valve.goldsrc,
    "deathmatchclassic": valve.goldsrc,
    "dmc": valve.goldsrc,
    "dod": valve.goldsrc,
    "gunmanchronicles": valve.goldsrc,
    "halflifeblueshift": valve.goldsrc,
    "halflifeopposingforce": valve.goldsrc,
    "hlblueshift": valve.goldsrc,
    "hlopposingforce": valve.goldsrc,
    "jamesbond007nightfire": valve.goldsrc,
    "nightfire": valve.goldsrc,
    "opposingforce": valve.goldsrc,
    "ricochet": valve.goldsrc,
    "teamfortressclassic": valve.goldsrc,
    "tfc": valve.goldsrc
          }

by_version = {
    # Id Software
    id_software.quake3.BSP_VERSION: id_software.quake,  # 23
    id_software.quake3.BSP_VERSION: id_software.quake3,  # 46
    # Infinity Ward
    infinity_ward.call_of_duty1.BSP_VERSION: infinity_ward.call_of_duty1,  # 59
    # Nexon
    nexon.cso2.BSP_VERSION: nexon.cso2,  # 100?
    # skip vindictus, v20 defaults to orange_box
    # Respawn Entertainment
    respawn.titanfall.BSP_VERSION: respawn.titanfall,  # 29
    respawn.titanfall2.BSP_VERSION: respawn.titanfall2,  # 37
    respawn.apex_legends.BSP_VERSION: respawn.apex_legends,  # 47
    48: respawn.apex_legends,  # Introduced in Season 7 with Olympus
    49: respawn.apex_legends,  # Introduced in Season 8 with Canyonlands Staging
    # Valve Software - GoldSrc
    valve.goldsrc.BSP_VERSION: valve.goldsrc,
    # Valve Software - Source Engine
    valve.cs_source.BSP_VERSION: valve.cs_source,
    valve.cs_go.BSP_VERSION: valve.cs_go,
    valve.orange_box.BSP_VERSION: valve.orange_box  # 20 (many sub-variants)
    # TODO: test if any of the following games require new branch scripts
    # 17: troika.vtmb  # Vampire: The Masquerade - Bloodlines
    # 17: valve.hl2_beta
    # 18: ritual.sin_emergence
    # ??: ritual.cscz_sp  # Counter-Strike: Condition Zero - Deleted Scenes
    # ??: ritual.sin  # 1998 original, Quake 2 engine
    # ??: royal_rudius.hdtf  # Royal Rudius Entertaiment: Hunt Down the Freeman  # pls no
    # 18: valve.hl2_beta
    # 19: valve.css  # Counter-Strike: Source
    # 19: valve.dod_s  # Day of Defeat: Source
    # 19: valve.hl2
    # 19: valve.hl2_dm  # Half-Life 2: Deathmatch
    # 20: ace.zeno_clash  # ACE Team: Zeno Clash (http://www.moddb.com/games/zeno-clash/downloads/zeno-clash-sdk/)
    # 20: arkane.dark_messiah  # Arkane Studios: Dark Messiah of Might and Magic
    # 20: crowbar.black_mesa  # Crowbar Collective: Black Mesa
    # 20: nexon.vindictus
    # 20: outerlight.bloody_good_time
    # 20: outerlight.the_ship
    # 20: valve.gmod
    # 20: valve.hl2_ep1
    # 20: valve.hl2_ep2
    # 20: valve.hl2_lc  # Half-Life 2: Lost Coast
    # 20: valve.l4d  # Left 4 Dead
    # 20: valve.portal
    # 20: valve.tf2  # Team Fortress 2
    # 21: briscoe.dear_esther  # Robert Briscoe: Dear Esther
    # 21: dwraden.beginner  # Davey Wraden: The Beginner's Guide
    # 21: dwraden.stanley_parable  # 2013 SDK mod?
    # 21: new_world.insurgency  # New World Interactive: Insurgency
    # 21: valve.alien_swarm
    # 21: valve.csgo
    # 21: valve.l4d2  # Left 4 Dead 2
    # 21: valve.portal_2
    # 22: valve.dota_2  # early beta?
    # 23: valve.dota_2  # ported to Source 2 now?
    # 27: monochrome.contagion
    # ??: fix_korea.tactical_intervention  # good luck getting your hands on a copy
             }
