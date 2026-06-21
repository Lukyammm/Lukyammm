# Hospital Reporting Dashboard (CRP / CRO)

A configurable **analytics and reporting engine** for care-record quality and
death-review (óbitos) management in a hospital. It reads operational data,
computes conformity indicators, and renders an analytical report with admin-side
configuration and a data-review/correction workflow. Google Apps Script +
Sheets + Looker Studio.

## Overview

Quality committees need a clear, current picture of how compliant care records
are, and a controlled way to review deaths (CRO). This app produces an
**analytical report** — conformity by indicator, period filters, charts — from a
spreadsheet base, and lets authorized users edit the report configuration and
correct data without touching raw sheets.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Report overview | Conformity charts | Death-review management |
|---|---|---|
| ![Report](docs/assets/01-home.png) | ![Charts](docs/assets/02-dashboard.png) | ![CRO](docs/assets/03-feature-main.png) |

## Features

- **Analytical report** of care-record quality ("Relatório Analítico da CRP").
- **Conformity indicators** (conforme / não conforme) with period filters
  (month/year).
- **Death-review (CRO) management** — classification and analysis of óbitos.
- **Configurable indicators** stored and edited through the app.
- **Admin editing** with permission checks.
- **Data-review & correction** tooling.
- **Looker Studio** pairing for shared dashboards.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (~2.6k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~1.1k lines)
- **Data:** Google Sheets
- **Visualization:** Looker Studio
- **Platform:** Google Workspace Web App

## What I implemented

I built the reporting engine and its configuration system. The core idea is that
the report is **driven by configuration**, not hard-coded:

- **Config store with caching** — indicator definitions live in a config sheet,
  mirrored to Script Properties, cached, and lock-guarded
  (`obterConfigRel`, `obterCacheConfigRel`, `executarComLockConfigRel`).
- **Permission model** — only listed admins can edit the configuration
  (`usuarioPodeEditarRel`, `listaAdminsRel`).
- **Structure validation** (`validarEstruturaCRP`) so a malformed base fails
  loudly instead of producing wrong numbers.
- **JSON routing** (`executarRota`, `responderJson`) with structured error
  payloads and error logging.

## Technical decisions

- **Configuration-driven reports:** indicators are data, not code, so the
  committee can change what's measured without a redeploy.
- **Cache + properties mirror:** config is cached and mirrored to Script
  Properties to stay fast and resilient to Sheet read limits.
- **Validate before report:** the base structure is checked first, because a
  silent wrong number is worse than a clear error in a compliance report.
- **Looker Studio for sharing:** the heavy interactive dashboards live in Looker,
  while the app owns capture, configuration, and review.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet with the report base.
2. **Extensions → Apps Script**, paste `Code.gs` and `index.html`.
3. Deploy as a Web app and open the `/exec` URL.
4. Configure indicators from the admin area (as a listed admin).

## Future improvements

- Versioned configuration history.
- Scheduled snapshot emails to the committee.
- Drill-down from a conformity number to the underlying records.

## What this project shows

It shows I can build **flexible, configuration-driven software** with the
guardrails a compliance context needs — permissions, validation, caching, and
clear errors. It's the project that best demonstrates I design for change and
correctness, not just a fixed report.
