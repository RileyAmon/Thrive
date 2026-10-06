# Thrive 7

Private, offline money planner. No build step, no server, no accounts.

## Deploy (GitHub Pages)
Replace the old files in your repo with ALL files in this folder (keep them in the same folder, no `icons/` subfolder):
`index.html, sw.js, manifest.webmanifest, icon.svg, icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png`

Your existing data is migrated automatically (the old `thrive_6` data is kept untouched as a backup).

## What's new
Daily "left to spend" hero with pace track, wallets (cash/MoMo/bank) and transfers, repeating bills and income, budget cycles starting on any day, category and wallet management, goals with history and weekly targets, insights charts and Thrive score, alerts, undo on every delete, search + filters, CSV/JSON export and import, app lock (PIN), hide amounts, command palette (Ctrl K), sample data, themes/accents/card styles/density/text size, motion controls.

## Fixed
Pages never refreshed after saving (stale render), unescaped HTML in user text, service worker failing to install (wrong icon paths), non-working density setting.

Tip: Settings > Back up. Your data lives only on this device.
