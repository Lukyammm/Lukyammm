# LinkedIn — Hospital Reporting Dashboard (CRP / CRO)

**Repo:** github.com/Lukyammm/hospital-reporting-dashboard
**Suggested images (carousel, in order):**
1. `02-dashboard.png` — conformity charts
2. `01-home.png` — report with period filters
3. `03-feature-main.png` — death-review (CRO) management
4. `04-result.png` — data-review / correction tooling

---

## Short version

Compliance reports are worthless if the numbers are wrong — or frozen in code.

I built a reporting engine where the indicators are configuration, not
hard-coded: quality committees change what's measured without a redeploy, and the
data is validated before any number is shown.

🔗 github.com/Lukyammm/hospital-reporting-dashboard

#JavaScript #GoogleAppsScript #Dashboard #HealthTech #OpenToWork

---

## Medium version

A quality committee asked me for a conformity report. Then they asked to change
what "conformity" meant. Then they asked again.

That's why I built this as a configuration-driven engine instead of a fixed
report. Indicators live in a config store the committee edits through the app —
no redeploy. The system computes conformity (conforme / não conforme) with period
filters, manages the death-review (CRO) process, and includes tooling to review
and correct data without touching raw sheets.

Because it's a compliance context, correctness comes first: the base structure is
validated before anything renders, config edits are permission-gated, and a
malformed base fails loudly instead of producing a confident wrong number.

🔗 github.com/Lukyammm/hospital-reporting-dashboard

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Storytelling version

The most useful thing I learned on this project: in a compliance report, a wrong
number is worse than an error message.

The committee needed a report on care-record quality — but "quality" kept
evolving. If I hard-coded the indicators, I'd be redeploying every month. So I
flipped it: the indicators became data. The committee edits them through the app,
and the report recomputes itself.

Then I made it defensive. Before the report renders, it validates the structure
of the base. If something's off, it says so — loudly — instead of quietly
producing a number someone might take into a meeting. Config edits are gated to
admins, cached for speed, and mirrored for resilience.

It also manages the death-review (CRO) process and lets authorized users correct
data safely. It's the project that taught me to design for *change* and
*correctness* at the same time.

🔗 github.com/Lukyammm/hospital-reporting-dashboard

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Technical version

A configuration-driven reporting engine on Google Apps Script — built so the
report can change without code changes, and never lie.

Design:
• **Indicators as data** — definitions live in a config sheet, edited in-app,
  recomputed on demand (no redeploy to change what's measured).
• **Cache + Script Properties mirror** (`obterConfigRel`, `obterCacheConfigRel`,
  `executarComLockConfigRel`) for speed and resilience against read limits.
• **Permission model** — only listed admins edit config (`usuarioPodeEditarRel`).
• **Structure validation** (`validarEstruturaCRP`) before reporting — fail loud,
  not wrong.
• **JSON routing** with structured error payloads and error logging.

Heavy interactive dashboards live in Looker Studio; the app owns capture, config,
validation, and review.

🔗 github.com/Lukyammm/hospital-reporting-dashboard

#JavaScript #GoogleAppsScript #SoftwareEngineering #Dashboard #HealthTech
