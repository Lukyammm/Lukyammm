# Boletim COSEP — Patient Safety Dashboard

A web dashboard that turns a patient-safety operational base into an **executive
panel**: care indicators, compliance by institutional goal, notification
analysis, and **automated email alerts** for critical pending items. Google Apps
Script + Google Sheets.

## Overview

Patient-safety data sits in spreadsheets that are hard to read at a glance.
Boletim COSEP transforms that base into a fast, filterable executive view —
indicators, goal compliance, and notification analysis — and proactively emails
the team when critical notifications are still pending, so nothing important goes
unnoticed.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Executive panel | Indicators & filters | Alerts |
|---|---|---|
| ![Panel](docs/assets/01-home.png) | ![Indicators](docs/assets/02-dashboard.png) | ![Alerts](docs/assets/04-result.png) |

## Features

- **Executive panel** for quick reading of safety indicators.
- **Compliance by institutional goal** with smart filters.
- **Notification analysis** to support decision-making.
- **Automated critical-notification email alerts** (`enviarAlertasCosep`).
- **Configurable** indicators and admin list, with a config-change log.
- **Responsive design**.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (`Index.html`, ~6.4k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~1.7k lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App with time-driven triggers

## What I implemented

I built the dashboard and the alerting system end to end:

- **Config-driven dashboard** with a config store, admin permissions, and a
  change log (`obterConfig`, `salvarConfigCosep`, `registrarLogConfig`).
- **Automated alerts** — a job collects pending critical notifications, builds a
  summary email, and sends it (`coletarNotificacoesCriticasPendentes`,
  `montarEmailAlertas`, `enviarAlertasCosep`).
- **Server-side HTML escaping** and a structured config/restore flow.

## Technical decisions

- **Push, don't wait:** the most valuable feature isn't the dashboard, it's the
  alert — so critical pending items are emailed automatically instead of relying
  on someone to check.
- **Configuration as data** with an audit log, so changes are traceable.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet.
2. **Extensions → Apps Script**, paste `Code.gs` and `Index.html`.
3. Deploy as a Web app; set a time-driven trigger for the alert job.
4. Open the `/exec` URL.

## Future improvements

- In-app acknowledgement of alerts.
- Trend charts per indicator over time.

## What this project shows

It shows I build tools that **act**, not just display — combining a clear
dashboard with proactive automation that changes team behavior.
