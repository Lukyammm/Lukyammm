# Pulse — Wristband Request System

A web app for requesting and tracking patient **wristbands**, built around a
clean, API-style backend with role-based access and guest entry. Google Apps
Script + Google Sheets.

## Overview

Pulse turns an informal wristband-request routine into a tracked ticket flow:
staff open a request, admins manage status, and guests can submit without a full
account — all backed by a tidy server API.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Login / guest | Tickets | Create request |
|---|---|---|
| ![Login](docs/assets/01-home.png) | ![Tickets](docs/assets/02-dashboard.png) | ![Create](docs/assets/03-feature-main.png) |

## Features

- **Ticket flow** — create, list, view, update status, cancel.
- **Authentication** with a session-based login and **guest access**.
- **Role-based admin** — user management and configuration.
- **Responsive design**.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (~1.7k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~1.4k lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App

## What I implemented

I built the app with a deliberately **clean server API** — every server action is
a small, named endpoint (`apiLogin`, `apiListTickets`, `apiCreateTicket`,
`apiUpdateStatus`, `apiCancelTicket`, `apiUpsertUser`, `apiConfigGet`). This keeps
the client thin and the contract between front and back end obvious.

- **Session login** plus **guest access** for low-friction requests.
- **Idempotent setup** (`ensureSetup_`, `seedMeAsAdmin`) so the app is trivial to
  stand up.

## Technical decisions

- **API-style backend:** naming every server function `api*` gives the project a
  clear, REST-like contract even on Apps Script — easy to read, test, and extend.
- **Guest + auth split:** the common case (submitting a request) is frictionless,
  while management actions require a session.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create a Google Sheet named **Pulse**.
2. **Extensions → Apps Script**, paste `Code.gs` and the HTML.
3. Deploy as a Web app (execute as accessing user, restrict to your org).
4. Open the `/exec` URL.

## Future improvements

- Email/print the wristband label on approval.
- Per-unit request analytics.

## What this project shows

It shows I value **clean structure**: a small, well-named API surface and a clear
auth model make even an Apps Script project read like a real product.
