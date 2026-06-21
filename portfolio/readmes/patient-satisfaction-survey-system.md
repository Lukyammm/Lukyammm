# Patient Satisfaction Survey System

A web app to **collect, organize, and analyze patient feedback** in a hospital.
It captures surveys, classifies manifestations (suggestions, complaints,
comments, compliments) by service block, and turns raw responses into
satisfaction and **NPS** metrics — with CSV export. Google Apps Script + Sheets.

## Overview

Patient feedback is only useful if it becomes a number a manager can act on.
This system standardizes how feedback is captured across service blocks
(Acolhimento, Assistência, Serviços), then computes satisfaction and NPS so
quality teams can see where to act — replacing manual tallying with a live,
filterable dashboard.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Overview | Charts | Manifestations |
|---|---|---|
| ![Overview](docs/assets/01-home.png) | ![Charts](docs/assets/02-dashboard.png) | ![Manifestations](docs/assets/03-feature-main.png) |

## Features

- **Overview** with summary cards and **satisfaction / NPS** indicators.
- **New survey** entry and a **records** browser.
- **Manifestations per block** — suggestions, complaints, comments, compliments.
- **Registrations (cadastros)** and **exits (saídas)** management with batch save.
- **Reports** and **CSV export** for downstream analysis.
- **Responsive design**.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (~2.3k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~720 lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App; pairs with Looker Studio

## What I implemented

I built the capture UI, the analytics layer, and the data plumbing. The
interesting work is in turning messy human input into trustworthy metrics:

- **NPS classification** (`classifyNps_`) and **satisfaction scoring**
  (`satisfaction_`, `countRating_`) computed server-side.
- **Sector canonicalization** — a fuzzy-matching pipeline
  (`buildSectorCanonicalMap_`, `canonicalSector_`, `sectorNameScore_`) that
  merges differently-spelled department names into one canonical sector, plus
  **deduplication** of records.
- **Manifestations-by-block model** with a one-time, self-guarding **migration**
  (`migrateToBlockManifestations`) that backs up before rewriting existing data.
- **CSV export** with proper cell escaping.

## Technical decisions

- **Canonical sectors over free text:** real survey data has the same department
  written ten ways. Normalizing it is what makes the analytics honest — so I built
  a scoring-based canonical map instead of trusting raw input.
- **Compute metrics on the server:** NPS and satisfaction are derived in
  `Code.gs`, so every view shows the same numbers and the client stays thin.
- **Safe migration with automatic backup:** restructuring live data is risky, so
  the migration backs up the sheet first and refuses to run twice.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet.
2. **Extensions → Apps Script**, paste `Code.gs` and `index.html`.
3. Deploy as a Web app and open the `/exec` URL.
4. If upgrading an instance with data, run `migrateToBlockManifestations` once.

## Future improvements

- Trend lines over time per sector.
- Automatic alerts when a sector's NPS drops below a threshold.
- Embed the charts in a shared Looker Studio board.

## What this project shows

It shows I can do real **data engineering**, not just CRUD: fuzzy matching,
deduplication, derived metrics, and safe migrations. It's the project that best
demonstrates I can turn unreliable input into decisions managers can trust.
