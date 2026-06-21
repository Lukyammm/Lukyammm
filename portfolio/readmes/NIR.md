# NIR — Internal Regulation Center

A web app for a hospital's **Internal Regulation Center**: structured **shift
handover**, bed/regulation records, and **daily reports** generated from filters
— so each shift starts with a clear, current picture instead of a verbal recap.
Google Apps Script + Google Sheets.

## Overview

Shift changes are where information gets lost. NIR structures the handover:
open a shift, register regulations, beds/UIB, external procedures, ICU
discharges, blocks, and pending items, then generate the daily report from
filters. The next shift inherits a complete, written record instead of notes on
paper.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Start shift | Active records | Daily report |
|---|---|---|
| ![Shift](docs/assets/01-home.png) | ![Records](docs/assets/02-dashboard.png) | ![Report](docs/assets/04-result.png) |

## Features

- **Shift lifecycle** — start, update, and close a shift (`startShift`,
  `updateShift`, `closeShift`).
- **Structured records** for regulations, beds/UIB, external procedures, ICU
  discharges, blocks, and pending items.
- **Daily report generation** from filters (`generateReport`).
- **Activity log** and **archive / restore** of records.
- **Demo data seeding** for safe testing (`seedDemoDataNIR`).
- **Responsive design**.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (~3.3k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~1k lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App

## What I implemented

I built the full handover model and reporting:

- A clear **shift state machine** (start / update / close) with an app-state
  endpoint that drives the UI (`getAppState`).
- **CRUD with archive/restore** so nothing is hard-deleted — important for an
  operational record.
- **Filter-driven report generation** that assembles the daily handover document.
- **Structure bootstrap** (`criarEstruturaNIR`) and **demo seeding** so the app
  is easy to stand up and review.

## Technical decisions

- **Soft delete (archive/restore)** instead of destructive deletes, because an
  operational log should be recoverable.
- **State-driven UI:** a single `getAppState` call hydrates the interface, keeping
  client logic simple and consistent.
- **Designed from the real flow:** the data model mirrors the actual handover and
  regulation worksheet the team already used.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet.
2. **Extensions → Apps Script**, paste `Code.gs` and `index.html`.
3. Run `criarEstruturaNIR` once, optionally `seedDemoDataNIR`.
4. Deploy as a Web app and open the `/exec` URL.

## Future improvements

- PDF export of the daily report.
- Per-unit dashboards on top of the records.

## What this project shows

It shows I can model a **real operational process** faithfully and protect its
data (soft delete, archive/restore, audit log) — turning an informal routine into
reliable software.
