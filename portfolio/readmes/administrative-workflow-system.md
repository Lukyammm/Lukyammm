# Administrative Workflow System (Cosign)

A hospital access-control and asset-custody web app that replaces scattered
spreadsheets with a single, auditable system for **lockers, visitors,
companions, and responsibility terms** — built on Google Apps Script and Google
Sheets and used in daily hospital operations.

## Overview

Hospitals hand out lockers, register visitors and patient companions, and sign
responsibility terms all day long. Done on paper or loose spreadsheets, this is
slow, error-prone, and impossible to audit. **Cosign** centralizes the whole
flow in one web application: every locker, person, and movement is registered,
searchable, and logged, with images and signed terms attached to the record.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Dashboard | Locker / visitor registration | Audit logs |
|---|---|---|
| ![Dashboard](docs/assets/02-dashboard.png) | ![Registration](docs/assets/03-feature-main.png) | ![Logs](docs/assets/04-result.png) |

## Features

- **Dashboard** with locker and visitor/companion totals at a glance.
- **Locker management** — registration, allocation, blocking, and contingency handling.
- **Visitor & companion control** — check-in/out with full history.
- **Lost & found** (achados-perdidos) registry.
- **Responsibility terms** generation and storage.
- **Image records** attached to entries.
- **Full audit logs** of every action for traceability.
- **User management** with access control.
- **Responsive interface** for desk and mobile use.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (single-page web app)
- **Backend:** Google Apps Script (`Code.gs`)
- **Data:** Google Sheets (sheets: Cadastro Armários, Movimentações, Visitantes,
  Acompanhantes, Termos de Responsabilidade, Registro de Imagens, Usuários, LOGS)
- **Platform:** Google Workspace Web App deployment

## What I implemented

I designed and built the entire application end to end — data model, server
logic, and UI. On the engineering side, this project goes well beyond a simple
form-over-sheet:

- A **caching layer** (`executarComCache`, targeted cache invalidation) to keep
  a spreadsheet backend responsive.
- **Document locking** with **retry + backoff** (`executarComLock`,
  `executarComRetry`, transient-error detection) to make concurrent writes safe.
- **Data normalization** helpers (text, numbers, dates, time zones) so messy
  human input becomes consistent records.
- A **structured audit log** so every change is traceable — a real requirement
  in a hospital environment.

## Technical decisions

- **Google Sheets as the database:** chosen because the operations team already
  lives in Sheets; it removes infrastructure cost and lets non-developers audit
  data directly. The trade-off (no SQL, rate limits) is handled with caching and
  locks rather than fighting the platform.
- **Cache + lock + retry pattern:** Apps Script and Sheets are slow and have
  quotas, so reads are cached and writes are serialized with locks and retried on
  transient failures — the difference between a toy and something a team relies on.
- **Modular pages** (dashboard, registrations, visitors, logs, users) routed by a
  single `data-page` switch, keeping one deployable app with clear separation.

## Run it locally

This is a Google Apps Script Web App; it runs inside Google Workspace, not on a
generic localhost.

1. Create a Google Sheet to act as the backend.
2. Open **Extensions → Apps Script** and paste `Code.gs` and the HTML files.
3. Run the initialization function once to create the required sheet tabs.
4. **Deploy → New deployment → Web app** (execute as the accessing user;
   restrict access to your organization).
5. Open the generated `/exec` URL.

## Future improvements

- Migrate the data layer behind an interface so it could move to Firestore/SQL
  without touching the UI.
- Add automated tests around the normalization and locking helpers.
- Export audit logs to a read-only BI dashboard.

## What this project shows

It shows I can take a real, messy operational problem and ship a complete,
reliable system around constraints — handling concurrency, caching, validation,
and auditability — not just wire up a CRUD form. It's the project that best
demonstrates I can own software that people depend on.
