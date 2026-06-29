# OldSchoolCraft — Game (Minecraft 1.7.10 modpack)

This folder holds the modpack definition for the OldSchoolCraft server and client.

- **Minecraft:** 1.7.10
- **Forge:** `10.13.4.1614` (download `forge-1.7.10-10.13.4.1614-*-universal.jar` / installer)
- **Java:** 8 (e.g. 1.8.0_202)

## Why no `.jar` files here

Most 1.7.10 mods forbid redistribution, and jars are large. We version-control the
**modlists** and **configs/scripts** only. Jars are `.gitignore`d. The modlist files
are the source of truth — download each listed jar into the matching `mods/` folder.

## Layout

```
game/
  client/
    modlist.txt        # 167 mods — full client set
    config/            # client configs
    scripts/           # CraftTweaker / ModTweaker recipe scripts
  server/
    modlist.txt        # 130 mods — client-only mods stripped
    config/            # server configs (kept in sync with client)
    scripts/           # MUST match client scripts (recipe parity)
    server.properties  # template
  client-only-mods.txt # 37 mods removed for the server build
```

## Setup

### Client
1. Create a MultiMC/Prism instance: MC 1.7.10 + Forge `10.13.4.1614`.
2. Drop every jar from `client/modlist.txt` into the instance `mods/`.
3. Copy `client/config/` and `client/scripts/` into the instance.

### Server
1. Install Forge `10.13.4.1614` (universal/installer) on Java 8.
2. Drop every jar from `server/modlist.txt` into `mods/`.
3. Copy `server/config/` and `server/scripts/` next to the server jar.
4. Copy `server/server.properties`, set `eula=true` in `eula.txt`, then launch.

## Keeping client and server in sync

`config/` and `scripts/` are duplicated per side so each is self-contained.
When you change a recipe or config, update **both** sides (especially `scripts/` —
recipe mismatches between client and server cause desyncs). Any content mod
(blocks/items) must exist on both sides at the **same version**.
