# GitHub Profile Setup Guide

Concrete, copy-paste settings to make the profile recruiter-ready. Apply these
in each repository's **About** panel (the ⚙️ next to "About" on the repo home
page) and on your profile's **pinned repositories** section.

---

## 1. Repositories to PIN (max 6 — order matters)

Pin these, in this order. They tell a clean story: scale → product → clinical
impact → analytics.

1. `administrative-workflow-system`
2. `hospital-process-management-system`
3. `TRR`
4. `patient-satisfaction-survey-system`
5. `hospital-reporting-dashboard`
6. `Boletim`

---

## 2. Repository descriptions + topics

Paste the **Description** into the About box, and add the **Topics** (comma-fine,
GitHub stores them as tags). Topics boost discoverability and look professional.

### administrative-workflow-system
- **Description:** `Hospital access-control web app (lockers, visitors, companions, audit logs) built on Google Apps Script + Sheets. Auth, caching, and document locking included.`
- **Topics:** `google-apps-script`, `javascript`, `web-app`, `healthcare`, `dashboard`, `internal-tools`, `automation`, `google-sheets`

### hospital-process-management-system
- **Description:** `Internal process & KPI management system (SIGEP) with dashboards, scheduled jobs, role-based access, and audit history. Google Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `dashboard`, `kpi`, `healthcare`, `internal-tools`, `automation`, `google-sheets`

### TRR
- **Description:** `Rapid Response Team call-intake web app with MEWS-based criticality, SLA tracking, and secure auth (salted hashing, lockout, sessions). Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `healthcare`, `web-app`, `authentication`, `internal-tools`, `google-sheets`

### patient-satisfaction-survey-system
- **Description:** `Patient satisfaction capture + analytics (NPS, satisfaction scoring, complaints/compliments) with CSV export. Google Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `analytics`, `nps`, `healthcare`, `dashboard`, `google-sheets`

### hospital-reporting-dashboard
- **Description:** `Analytics & reporting engine for care-record quality and death-review (CRP/CRO) with configurable indicators, caching, and admin editing. Apps Script + Sheets + Looker.`
- **Topics:** `google-apps-script`, `javascript`, `dashboard`, `analytics`, `reporting`, `healthcare`, `looker-studio`, `google-sheets`

### Boletim
- **Description:** `Patient-safety monitoring dashboard (COSEP) with indicator compliance, smart filters, and automated critical-notification email alerts. Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `dashboard`, `patient-safety`, `healthcare`, `automation`, `google-sheets`

### NIR
- **Description:** `Internal Regulation Center app: shift handover, bed/regulation records, and daily reports for hospital operations. Google Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `healthcare`, `web-app`, `internal-tools`, `google-sheets`

### Pulse
- **Description:** `Wristband request system with a clean API-style backend, guest access, and role-based admin. Google Apps Script + Sheets.`
- **Topics:** `google-apps-script`, `javascript`, `web-app`, `healthcare`, `api`, `google-sheets`

> For the remaining medium repos (`Gama_agendamento_sala`, `planilha-gestao`,
> `HELV_BOLETIM`, `internal-communication-platform`, `google-sheets-automation-tool`)
> reuse the same pattern: one sentence on *what it does + who uses it + stack*,
> plus the `google-apps-script`, `javascript`, `google-sheets` topics.

---

## 3. Clean-up actions

- **`coordena_planilhas_gestao`** and **`INFECTOLOGIA`** are empty — either delete
  them or mark them private. Empty public repos hurt a recruiter's first impression.
- **`passagem-plantao`** is superseded by `NIR` — make private or archive.
- **`LISTA_CRO`**, **`Cuidados-Paliativos`**, **`MAPA_gerenciamento_mapa`** — keep,
  but they should not be pinned. Give them a one-line description so they don't
  look abandoned.
- Set a consistent **default branch name** (`main`) — already the case. Good.

---

## 4. Profile README (the `Lukyammm/Lukyammm` repo)

The profile README has been upgraded in this branch. It now leads with a clear
positioning line, groups featured projects with one-line value statements, and
adds a "What I bring" section aimed at hiring managers. After merging, the
profile at `github.com/Lukyammm` will read like a focused product engineer's
page rather than a list of repos.

**Optional polish (manual, outside this repo):**
- Add a profile **avatar** and a one-line **bio** (the API bio is already good).
- Set **Location** and turn on **"Available for hire"** in profile settings.
- Add a link to your LinkedIn once the posts go live.
