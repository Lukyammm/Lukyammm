# Hospital Process Management System (SIGEP-HUC)

An internal **process and KPI management system** for a university hospital:
register processes, track follow-up actions, monitor indicators on a dashboard,
and manage everything through a permission-controlled admin area — built on
Google Apps Script and Google Sheets.

## Overview

Operational teams need to know *which processes exist, who owns them, what the
indicators say, and what's pending.* SIGEP brings that together: structured
process records, follow-up tracking, KPI monitoring with dashboard snapshots, and
process mapping — replacing a pile of disconnected spreadsheets with one governed
system.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| KPI dashboard | Processes | Follow-up |
|---|---|---|
| ![Indicators](docs/assets/02-dashboard.png) | ![Processes](docs/assets/03-feature-main.png) | ![Follow-up](docs/assets/04-result.png) |

## Features

- **Indicators (KPI) view** with dashboard data and periodic **snapshots**.
- **Processes** module — create, edit, and organize operational processes.
- **Follow-up (acompanhamento)** — track status and actions per item.
- **Process mapping** with a default template to bootstrap new areas.
- **Managers (gestores)** registry and linking to processes.
- **Admin area** — users, sectors, configuration, and data-review tooling.
- **Role-based permissions** (write vs. admin) enforced server-side.
- **Audit history** per record.
- **Batch updates** and **saved advanced filters**.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (multi-view single-page app)
- **Backend:** Google Apps Script (`Code.gs`, ~2.5k lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App, with time-driven triggers

## What I implemented

I built the full system: the data layer, the server API, and the multi-view UI
(`processos`, `acompanhamento`, `indicadores`, `mapeamento`, `admin`). Notable
pieces:

- **Scheduled jobs** — dashboard snapshot generation, a base health check, and a
  daily operational guard (`runDashboardSnapshotJob`, `runBasesHealthCheckJob`,
  `runDailyOperationalGuardJob`).
- **Schema migrations** (`runSchemaMigrations`) so the data structure can evolve
  without breaking existing sheets.
- **Permission wrappers** (`withWritePermission_`, `withAdminPermission_`) that
  gate every mutating action.
- **Data-review tooling** to detect and apply corrections in bulk.

## Technical decisions

- **Server-enforced permissions:** access control lives in the backend, not the
  UI, so the rules can't be bypassed from the client.
- **Snapshots over live recompute:** KPI dashboards read pre-computed snapshots,
  keeping the dashboard fast even as the underlying data grows.
- **Migrations as code:** schema changes are scripted and idempotent, so deploying
  an update to an instance that already has data is safe.
- **Paged data loads** (`getProcessosPage`, `getAcompanhamentoPage`) to avoid
  pulling entire sheets into the client.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet.
2. **Extensions → Apps Script**, paste `Code.gs` and `index.html`.
3. Run the setup/migration function once to build the structure.
4. **Deploy → New deployment → Web app** and open the `/exec` URL.

## Future improvements

- Surface the KPI snapshots in an embedded Looker Studio board.
- Add notification rules when an indicator crosses a threshold.
- Unit-test the permission and migration helpers.

## What this project shows

It shows I think in terms of **products, not scripts**: scheduled jobs,
migrations, role-based access, paging, and audit history are the things that make
internal software maintainable. This is the project that best demonstrates
architecture and ownership over time.
