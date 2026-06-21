# Project Audit — Lukyam Madeira

**Prepared:** 2026-06-21 · **Scope:** 22 repositories on `github.com/Lukyammm`

This audit reviews every repository on the account, classifies each by hiring
impact, and explains exactly what should be polished before the portfolio goes
in front of recruiters. The analysis is based on reading the actual source code
(server-side `Code.gs` and client `index.html`), not just the existing READMEs.

---

## What these projects actually are

Almost every project is a **real internal web application** for a hospital
(Hospital Universitário do Ceará / Instituto de Saúde e Gestão Hospitalar),
built with **Google Apps Script + Google Sheets + HTML/CSS/JavaScript**, and
deployed as Google Web Apps used in day-to-day operations.

This is a strong, honest hiring narrative: *a developer who ships real
production tools that hospital teams depend on every day.* The engineering is
more serious than the current READMEs suggest — several apps include salted +
hashed passwords, session tokens, brute-force lockout, caching layers, document
locks with retry/backoff, scheduled jobs, schema migrations, and role-based
permissions.

**The single biggest problem:** the most "portfolio-named" repositories have
**generic, templated READMEs** that describe none of this. A recruiter opening
them today cannot tell these are substantial systems. Fixing the READMEs (and
adding screenshots) is the highest-leverage change available.

---

## Impact classification

### 🟢 HIGH impact — lead with these

| Project | What it really is | Why it ranks high |
|---|---|---|
| **administrative-workflow-system** (`Cosign`) | Locker, visitor, companion & access-control system for a hospital. Modules: dashboard, locker/units registration, visitors, companions, lost & found, responsibility terms, image records, audit logs, users. | Largest, most complete codebase (~26k lines). Real auth, caching, document locks, retry/backoff, contingency handling, cache invalidation. Demonstrates architecture at scale. |
| **hospital-process-management-system** (`SIGEP-HUC`) | Process / indicator (KPI) management with follow-up, process mapping, and an admin area. | Dashboard snapshots, scheduled jobs, schema migrations, role-based (write/admin) permissions, audit history, batch updates. Reads like a real product. |
| **TRR** (Rapid Response Team) | Clinical/surgical rapid-response call intake with MEWS-based criticality and SLA tracking. | Compelling clinical story + genuine security: salted/hashed passwords, timing-safe compare, login lockout, password-reset tokens, session cache, SLA metas. |
| **patient-satisfaction-survey-system** | Patient satisfaction capture + analytics (NPS, satisfaction scoring, manifestations by block, CSV export). | Real data engineering: sector canonicalization/dedupe, NPS classification, computed metrics. Clear before/after value story. |
| **hospital-reporting-dashboard** (`CRP/CRO`) | Analytics report on quality/conformity of care records + death-review (óbitos) management. | Config-driven reporting engine with caching, permissions, admin editing, and data-review/correction tooling. Strong "data → decision" framing. |

### 🟡 MEDIUM impact — solid supporting projects

| Project | What it is | Note |
|---|---|---|
| **Boletim** (`COSEP`) | Patient-safety monitoring dashboard with critical-notification email alerts. | Already has the best existing README. Good second-tier feature. |
| **NIR** | Internal Regulation Center: shift handover + bed/regulation records + daily reports. | Clean domain model (start/close shift, records, reports, archive/restore). |
| **Gama_agendamento_sala** | Room scheduling, blocking, monitoring & audit. | Huge (~27k lines) with real auth/sessions; domain is more generic than the clinical apps. |
| **Pulse** | Wristband request system with a clean API-style backend + guest access. | Nicely structured `api*` server layer; good "clean code" example. |
| **planilha-gestao** / **HELV_BOLETIM** | Operational management dashboards / hospital bulletins. | Decent existing READMEs; good "breadth" repos. |
| **internal-communication-platform** | Announcements / updates / team info hub. | Functional; README is generic. |
| **google-sheets-automation-tool** | Apps Script automation utility for Sheets productivity. | Good "tooling" example; README is generic. |

### 🔴 LOW impact — keep private or finish later (do not feature)

| Project | Status |
|---|---|
| **MAPA_gerenciamento_mapa** | Working but minimal; stub README. |
| **Cuidados-Paliativos** | Two HTML variants, stub README; unclear final form. |
| **passagem-plantao** | Early/duplicate of NIR-style handover; README is a single word. |
| **LISTA_CRO** | Useful internal sheet tool; README is an informal note, not recruiter-facing. |
| **coordena_planilhas_gestao** | Effectively empty (1-line files). |
| **INFECTOLOGIA** | Empty repo (README only). |
| **Acesso**, **HigieneM-os** | **Private** — not part of the public portfolio. Leave as-is. |

---

## Detailed audit table

| Project | Stack | Current status | Strengths | Problems found | Fix priority | LinkedIn | Portfolio |
|---|---|---|---|---|---|---|---|
| administrative-workflow-system | GAS, Sheets, HTML/CSS/JS | Works (deployed); generic README | Large, modular, real auth + caching + locks + retry | README says nothing real; no screenshots; PT-only UI labels | **P1** | High | High |
| hospital-process-management-system | GAS, Sheets, HTML/CSS/JS | "In development"; generic README | KPIs, jobs, migrations, permissions, audit | Generic README; "in development" label undersells it; no shots | **P1** | High | High |
| TRR | GAS, Sheets, HTML/CSS/JS | Works; good PT README | Strong security + SLA + clinical story | Needs English README + screenshots | **P1** | High | High |
| patient-satisfaction-survey-system | GAS, Sheets, HTML/CSS/JS | Works; generic README + migration note | NPS/analytics, data cleaning | Generic README; no shots | **P1** | High | High |
| hospital-reporting-dashboard | GAS, Sheets, Looker | Works; generic README | Config-driven reporting + data review | Generic README; no shots | **P1** | High | High |
| Boletim (COSEP) | GAS, Sheets, HTML/CSS/JS | Works; strong PT README | Patient-safety dashboard + email alerts | English version + shots | **P2** | Medium | High |
| NIR | GAS, Sheets, HTML/CSS/JS | Works; good PT README | Clean shift/regulation model + reports | English version + shots | **P2** | Medium | Medium |
| Gama_agendamento_sala | GAS, Sheets, HTML/CSS/JS | Works; good PT README | Very large; auth/sessions | English README; trim scope in story | **P2** | Medium | Medium |
| Pulse | GAS, Sheets, HTML/CSS/JS | Works; good PT README | Clean API-style backend | English README + shots | **P3** | Medium | Medium |
| planilha-gestao | GAS, Sheets, HTML/CSS/JS | Works; decent PT README | Auto-refresh dashboard | English polish | **P3** | Low | Medium |
| HELV_BOLETIM | GAS, Sheets, HTML/CSS/JS | Works; decent PT README | Bulletin generation | English polish | **P3** | Low | Medium |
| internal-communication-platform | GAS, Sheets, HTML/CSS/JS | Works; generic README | Functional hub | Real README + shots | **P3** | Low | Medium |
| google-sheets-automation-tool | GAS, Sheets, JS | Works; generic README | Good tooling example | Real README | **P3** | Low | Medium |
| MAPA_gerenciamento_mapa | GAS, Sheets, HTML | Works; stub README | — | Stub README | P4 | No | Low |
| Cuidados-Paliativos | GAS, Sheets, HTML | Unclear; stub README | — | Two variants, unclear | P4 | No | Low |
| passagem-plantao | GAS, Sheets, HTML | Early; 1-word README | — | Superseded by NIR | P4 | No | Low |
| LISTA_CRO | GAS, Sheets | Works; informal README | Useful internal tool | Not recruiter-facing | P4 | No | Low |
| coordena_planilhas_gestao | GAS | Empty (1-line) | — | No content | — | No | Hide |
| INFECTOLOGIA | — | Empty | — | No content | — | No | Hide |
| Acesso / HigieneM-os | GAS | Private | — | Out of scope (private) | — | No | — |

---

## The three things that will move the needle most

1. **Replace the generic READMEs** on the 5 HIGH-impact repos with the specific,
   English, recruiter-facing versions in `portfolio/readmes/`.
2. **Add 4–5 screenshots per featured repo** following
   `portfolio/03-SCREENSHOT-GUIDE.md`. A screenshot is worth more than any
   paragraph for these visual dashboards.
3. **Curate the profile:** pin the 6 best repos, hide/finish the empty ones, and
   add clear one-line descriptions + topics (see `portfolio/02-GITHUB-SETUP.md`).
