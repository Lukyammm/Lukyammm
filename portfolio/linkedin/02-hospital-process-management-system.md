# LinkedIn — Hospital Process Management System (SIGEP)

**Repo:** github.com/Lukyammm/hospital-process-management-system
**Suggested images (carousel, in order):**
1. `02-dashboard.png` — KPI/indicators view
2. `03-feature-main.png` — processes list
3. `04-result.png` — follow-up / admin
4. `05-mobile-view.png` — mobile

---

## Short version

Which processes exist, who owns them, and what do the indicators say?

I built SIGEP so a hospital team can answer that in one place: processes,
follow-up actions, and KPI dashboards — with scheduled snapshots, role-based
access, and audit history.

🔗 github.com/Lukyammm/hospital-process-management-system

#JavaScript #GoogleAppsScript #Dashboard #HealthTech #OpenToWork

---

## Medium version

Operational teams drown in disconnected spreadsheets: one for processes, one for
indicators, one for "who's following up on what."

I built SIGEP to bring them together — a single system with:
• A KPI dashboard backed by periodic snapshots
• Process registration and mapping
• Follow-up tracking per item
• An admin area with users, sectors, and configuration

Under the hood it behaves like a product, not a script: scheduled jobs generate
dashboard snapshots and run health checks, schema migrations let the data
structure evolve safely, and every mutating action is gated by server-enforced
permissions with audit history.

🔗 github.com/Lukyammm/hospital-process-management-system

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Storytelling version

The first time I asked "how many of our processes are actually on target right
now?", the honest answer was: nobody knew. The data existed — scattered across
spreadsheets — but no one could see it together.

That gap became SIGEP.

I built it so processes, follow-up actions, and indicators live in one governed
system. Managers open a dashboard and see KPI snapshots; owners track their
processes; admins manage users and configuration — all with an audit trail.

What I'm proudest of is the parts you don't see: scheduled jobs that snapshot the
dashboard and check the data's health every day, migrations that let the schema
change without breaking live instances, and permissions enforced on the server so
the rules can't be clicked around.

It's the project where I stopped writing scripts and started building software
that survives change.

🔗 github.com/Lukyammm/hospital-process-management-system

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Technical version

Built an internal process + KPI system (SIGEP) on Google Apps Script that's
designed to last, not just to demo.

The product-grade pieces:
• **Scheduled jobs** — dashboard snapshots, base health checks, and a daily
  operational guard (time-driven triggers).
• **Schema migrations** (`runSchemaMigrations`) — idempotent, so deploying an
  update to an instance that already has data is safe.
• **Server-enforced permissions** (`withWritePermission_`, `withAdminPermission_`)
  wrapping every mutation — access control can't be bypassed from the client.
• **Paged loads** (`getProcessosPage`, `getIndicadoresPage`) instead of pulling
  whole sheets into the browser.
• **Snapshots over live recompute** so the dashboard stays fast as data grows.

The theme: internal tools rot without migrations, permissions, and paging. I
built those in from the start.

🔗 github.com/Lukyammm/hospital-process-management-system

#JavaScript #GoogleAppsScript #SoftwareEngineering #Dashboard #HealthTech
