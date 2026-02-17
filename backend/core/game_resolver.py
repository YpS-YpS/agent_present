"""Resolve executable names from PresentMon logs to friendly game names.

The Application column in PresentMon CSV files contains the raw .exe name
(e.g. "dota2.exe"). This module maps those to human-readable game/app names.
"""

from __future__ import annotations

import re

# Map of lowercase exe names (without .exe) → friendly game name.
# Add more entries as needed.
_EXE_TO_GAME: dict[str, str] = {
    # Valve
    "dota2": "Dota 2",
    "csgo": "Counter-Strike: Global Offensive",
    "cs2": "Counter-Strike 2",
    "hl2": "Half-Life 2",
    "hlalyx": "Half-Life: Alyx",
    "portal2": "Portal 2",
    "left4dead2": "Left 4 Dead 2",
    "tf_win64": "Team Fortress 2",

    # Epic / Unreal
    "fortniteclient-win64-shipping": "Fortnite",
    "fortniteclient-win64-shipping_be": "Fortnite",
    "rocketleague": "Rocket League",

    # Riot
    "league of legends": "League of Legends",
    "valorant-win64-shipping": "Valorant",
    "valorant": "Valorant",

    # Blizzard
    "overwatch": "Overwatch 2",
    "wow": "World of Warcraft",
    "diablo iv": "Diablo IV",
    "diabloimmortal": "Diablo Immortal",
    "hearthstone": "Hearthstone",
    "starcraft ii": "StarCraft II",

    # EA
    "apex_legends": "Apex Legends",
    "r5apex": "Apex Legends",
    "bf2042": "Battlefield 2042",
    "fifa23": "EA FC / FIFA 23",
    "nfs-heat": "Need for Speed: Heat",
    "needforspeedunbound": "Need for Speed Unbound",

    # Ubisoft
    "rainbowsix": "Rainbow Six Siege",
    "rainbowsix_be": "Rainbow Six Siege",
    "acvalhalla": "Assassin's Creed Valhalla",
    "acmirage": "Assassin's Creed Mirage",
    "farcry6": "Far Cry 6",

    # CD Projekt
    "cyberpunk2077": "Cyberpunk 2077",
    "witcher3": "The Witcher 3",

    # Rockstar
    "gta5": "Grand Theft Auto V",
    "gtav": "Grand Theft Auto V",
    "rdr2": "Red Dead Redemption 2",

    # Indie / Popular
    "minecraft": "Minecraft",
    "javaw": "Minecraft (Java)",
    "eldenring": "Elden Ring",
    "darksoulsiii": "Dark Souls III",
    "sekiro": "Sekiro: Shadows Die Twice",
    "baldursgate3": "Baldur's Gate 3",
    "bg3": "Baldur's Gate 3",
    "bg3_dx11": "Baldur's Gate 3",
    "starfield": "Starfield",
    "hogwartslegacy": "Hogwarts Legacy",
    "palworld-win64-shipping": "Palworld",
    "enshrouded": "Enshrouded",
    "helldivers2": "Helldivers 2",

    # Benchmarks
    "3dmark": "3DMark",
    "timespy": "3DMark Time Spy",
    "firestrike": "3DMark Fire Strike",
    "heaven": "Unigine Heaven",
    "valley": "Unigine Valley",
    "superposition": "Unigine Superposition",
    "furmark": "FurMark",
    "cinebench": "Cinebench",

    # Microsoft / System
    "dwm": "Desktop Window Manager",
    "explorer": "Windows Explorer",
    "chrome": "Google Chrome",
    "firefox": "Mozilla Firefox",
    "msedge": "Microsoft Edge",

    # Other popular games
    "destiny2": "Destiny 2",
    "halo infinite": "Halo Infinite",
    "haloinfinite": "Halo Infinite",
    "cod": "Call of Duty",
    "modernwarfare": "Call of Duty: Modern Warfare",
    "blackops6": "Call of Duty: Black Ops 6",
    "warzone": "Call of Duty: Warzone",
    "pubg": "PUBG: Battlegrounds",
    "tslgame": "PUBG: Battlegrounds",
    "amongus": "Among Us",
    "genshinimpact": "Genshin Impact",
    "yuanshen": "Genshin Impact",
    "starrail": "Honkai: Star Rail",
    "warframe_x64": "Warframe",
    "warframe": "Warframe",
    "pathofexile": "Path of Exile",
    "pathofexile_x64": "Path of Exile",
    "arma3_x64": "Arma 3",
    "rust": "Rust",
    "rustclient": "Rust",
    "terraria": "Terraria",
    "stardewvalley": "Stardew Valley",
    "factorio": "Factorio",
    "satisfactory": "Satisfactory",
    "msfs": "Microsoft Flight Simulator",
    "flightsimulator": "Microsoft Flight Simulator",
    "total war": "Total War",

    # VR
    "hl:alyx": "Half-Life: Alyx",
    "boneworks": "Boneworks",
    "beatsaber": "Beat Saber",
    "vrcompositor": "SteamVR Compositor",
    "oculusclient": "Oculus Client",
}


def resolve_game_name(exe_name: str) -> str:
    """Convert an executable name to a friendly game/app name.

    Args:
        exe_name: Raw executable name from PresentMon (e.g. "dota2.exe")

    Returns:
        Friendly game name (e.g. "Dota 2") or cleaned-up exe name if unknown.
    """
    if not exe_name:
        return "Unknown"

    # Strip .exe extension and lowercase for lookup
    clean = exe_name.strip()
    base = re.sub(r"\.exe$", "", clean, flags=re.IGNORECASE)
    key = base.lower().strip()

    # Direct match
    if key in _EXE_TO_GAME:
        return _EXE_TO_GAME[key]

    # Try without trailing numbers/underscores (e.g. "dota2" → "dota")
    stripped = re.sub(r"[_\-\s]*\d+$", "", key)
    if stripped and stripped in _EXE_TO_GAME:
        return _EXE_TO_GAME[stripped]

    # Try partial match (for things like "fortniteclient-win64-shipping_be")
    for exe_key, game_name in _EXE_TO_GAME.items():
        if exe_key in key or key in exe_key:
            return game_name

    # Fallback: clean up the exe name as a title
    # "my_game_app" → "My Game App"
    fallback = re.sub(r"[-_]+", " ", base)
    fallback = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", fallback)  # camelCase split
    return fallback.title().strip() or exe_name
