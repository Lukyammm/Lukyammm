# Screenshot Capture Guide

**Why this is a guide and not finished images:** these apps are Google Apps
Script Web Apps. They only render with their real Google Sheets backend and an
authenticated Google session — they cannot be run on a generic local machine,
and the UI is data-driven, so any "fake" local render would be empty or broken.
Rather than fabricate screenshots, here is an exact, shot-by-shot plan you run
against your **live deployments** (open the Web App `/exec` URL while logged in).

### Capture settings (do this once)
- Browser at **1440×900**, 100% zoom, light theme, window maximized.
- Use **demo / anonymized data** — no real patient names, IDs, or documents.
  Most apps already have seed/demo functions (e.g. `seedDemoDataNIR`,
  `seedMeAsAdmin`); use them or blur sensitive fields.
- Save as **PNG**, full app area (not the whole desktop).
- Put files in each repo under **`docs/assets/`** and reference them from the
  README (the new READMEs already expect `docs/assets/01-...png`, etc.).
- Also take **one mobile shot** (DevTools → iPhone 12 Pro) per app for the
  "responsive" point.

### Naming convention (use for every project)
```
docs/assets/01-home.png
docs/assets/02-dashboard.png
docs/assets/03-feature-main.png
docs/assets/04-result.png
docs/assets/05-mobile-view.png
```

---

## Per-project shot list

### administrative-workflow-system (Cosign)
1. `01-home` — login / landing screen.
2. `02-dashboard` — main dashboard with locker/visitor totals.
3. `03-feature-main` — locker registration **or** visitor check-in form.
4. `04-result` — audit **Logs** page (shows traceability) or a responsibility term.
5. `05-mobile-view` — dashboard on mobile width.

### hospital-process-management-system (SIGEP)
1. `01-home` — landing / overview.
2. `02-dashboard` — **Indicadores** (KPI) view with charts.
3. `03-feature-main` — **Processos** list with an item open for editing.
4. `04-result` — **Acompanhamento** (follow-up) board or admin area.
5. `05-mobile-view` — KPI view on mobile.

### TRR (Rapid Response Team)
1. `01-home` — type selection (Clinical / Surgical) — the fast-entry screen.
2. `02-dashboard` — open-calls list with criticality colors.
3. `03-feature-main` — MEWS criticality table during a new clinical call.
4. `04-result` — a call detail with SLA / status timeline.
5. `05-mobile-view` — new-call flow on mobile (this is the real-world use case).

### patient-satisfaction-survey-system
1. `01-home` — Overview tab with summary cards.
2. `02-dashboard` — charts (satisfaction / NPS).
3. `03-feature-main` — "Novo" survey entry or **Manifestações** (complaints/compliments).
4. `04-result` — **Relatório** view + the CSV export action.
5. `05-mobile-view` — overview on mobile.

### hospital-reporting-dashboard (CRP/CRO)
1. `01-home` — report landing with period filters.
2. `02-dashboard` — conformity charts (conforme / não conforme).
3. `03-feature-main` — death-review (CRO) management table.
4. `04-result` — data-review / correction tooling.
5. `05-mobile-view` — report on mobile.

### Boletim (COSEP)
1. `01-home` — executive panel.
2. `02-dashboard` — indicators by institutional goal with the smart filters.
3. `03-feature-main` — notification analysis view.
4. `04-result` — a generated alert / email summary screen.
5. `05-mobile-view` — panel on mobile.

### NIR
1. `01-home` — start-shift screen.
2. `02-dashboard` — active records (beds / regulation).
3. `03-feature-main` — new record form.
4. `04-result` — generated daily report.
5. `05-mobile-view` — record list on mobile.

### Pulse
1. `01-home` — login / guest access.
2. `02-dashboard` — tickets list.
3. `03-feature-main` — create-ticket form.
4. `04-result` — ticket status update.
5. `05-mobile-view` — tickets on mobile.

---

## After capturing

Drop the images into each repo's `docs/assets/` folder, commit, and the
"Demonstração / Demo" section in the new README will render them automatically.
For LinkedIn, the same images are reused as carousel slides — see
`portfolio/04-PUBLISHING-PLAN.md` for which image goes on which post.
