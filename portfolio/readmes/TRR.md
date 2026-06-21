# TRR — Rapid Response Team Call System

A web app for opening and tracking **Rapid Response Team** calls in a university
hospital. It's built for speed at the bedside: pick the call type, capture the
patient, set criticality from the **MEWS** scale, and track the call against an
**SLA** — with real authentication behind it. Google Apps Script + Google Sheets.

## Overview

When a patient deteriorates, the Rapid Response Team has to be reachable in
seconds — there's no time for friction. TRR makes the first step fast (choose
*Clinical* or *Surgical*, no login required to open a call), captures the patient
identifiers, classifies criticality (MEWS color for clinical cases; priority
procedure for surgical), and then tracks each call's status and response time so
nothing slips.

## Demo

> Screenshots live in `docs/assets/`. See the capture guide for the shot list.

| Type selection | Open calls | MEWS criticality |
|---|---|---|
| ![Type](docs/assets/01-home.png) | ![Calls](docs/assets/02-dashboard.png) | ![MEWS](docs/assets/03-feature-main.png) |

## Features

- **Two-step intake** (Clinical / Surgical) optimized for speed.
- **Patient capture:** name, medical record, date of birth, unit, bed.
- **MEWS-based criticality** for clinical cases (color-coded, table shown on screen).
- **Procedure-based criticality** for surgical cases.
- **Call tracking** with status and **SLA targets**.
- **Secure accounts** for staff who manage and close calls.
- **Responsive design** for use on phones at the bedside.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (~5.4k lines)
- **Backend:** Google Apps Script (`Code.gs`, ~2.3k lines)
- **Data:** Google Sheets
- **Platform:** Google Workspace Web App

## What I implemented

I built the full application, and I took the security seriously because this is
real clinical data:

- **Salted + hashed passwords** (`gerarSaltSenha_`, `hashSenhaComSalt_`) — no
  plaintext credentials.
- **Timing-safe comparison** (`timingSafeEqualHex_`) to resist timing attacks.
- **Brute-force lockout** — failed-login tracking with temporary blocking
  (`registrarFalhaLogin_`, `getLoginAttempts_`).
- **Password-reset tokens** and a **session cache** for authenticated flows.
- **SLA logic** (`getSlaMetaMin_`) and server time-zone handling so response
  times are measured correctly.

## Technical decisions

- **No login to *open* a call, login to *manage* it:** the design optimizes for
  the moment that matters (raising the alarm) while still protecting the data and
  the actions that change it.
- **MEWS shown on-screen, color chosen by the operator:** the tool supports the
  clinical decision instead of hiding it — the score table is visible during
  intake.
- **Security primitives written explicitly:** salting, hashing, timing-safe
  compare, and lockout are implemented rather than assumed, because Apps Script
  gives you the building blocks, not a framework.

## Run it locally

Runs as a Google Apps Script Web App:

1. Create the backing Google Sheet.
2. **Extensions → Apps Script**, paste `Code.gs` and `index.html`.
3. Run setup once to build the structure and seed an admin user.
4. **Deploy → New deployment → Web app** and open the `/exec` URL.

## Future improvements

- Push/SMS notification to the on-call team when a critical call opens.
- A live SLA board on a wall display.
- Exportable response-time analytics per unit.

## What this project shows

It shows I can build software for a high-stakes, time-critical context and still
handle authentication, hashing, lockout, and SLA tracking correctly. It's the
project that best demonstrates I care about security and real-world usability,
not just features.
