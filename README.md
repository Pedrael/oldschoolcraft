# OldSchoolCraft

Monorepo for the OldSchoolCraft project.

## Layout

| Folder | What |
|--------|------|
| [`website/`](website/) | Marketing/info site (React + TypeScript + Vite) |
| [`game/`](game/) | Minecraft 1.7.10 modpack — client & server modlists, configs, scripts |

## Website

```bash
cd website
npm install
npm run dev     # http://localhost:8888
npm run build
```

> If this repo is connected to a host (Vercel/Netlify/Cloudflare Pages), set the
> project root/base directory to `website/`.

## Game

See [`game/README.md`](game/README.md). Minecraft 1.7.10, Forge `10.13.4.1614`, Java 8.
Mod jars are not committed (license + size) — `modlist.txt` files are the source of truth.
