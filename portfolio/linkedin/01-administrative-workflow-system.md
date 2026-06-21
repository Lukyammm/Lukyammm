# LinkedIn — Administrative Workflow System (Cosign)

**Repo:** github.com/Lukyammm/administrative-workflow-system
**Suggested images (carousel, in order):**
1. `02-dashboard.png` — the dashboard
2. `03-feature-main.png` — locker registration / visitor check-in
3. `04-result.png` — audit logs
4. `05-mobile-view.png` — mobile
**Captions per slide:** see `04-PUBLISHING-PLAN.md`.

---

## Short version

Hospitals lose track of lockers, visitors, and signed terms when it all lives in
loose spreadsheets.

So I built Cosign: one web app to register lockers, check visitors and companions
in and out, store responsibility terms, and log every single action for audit.

Stack: JavaScript + Google Apps Script + Sheets — with caching and document locks
so concurrent writes stay safe.

🔗 github.com/Lukyammm/administrative-workflow-system

#JavaScript #GoogleAppsScript #WebDevelopment #HealthTech #OpenToWork

---

## Medium version

What happens when lockers, visitors, and signed responsibility terms are tracked
on scattered spreadsheets? Things get lost, and you can't audit anything.

I built Cosign to fix that — a single web app that handles:
• Locker registration, allocation, and blocking
• Visitor and companion check-in/out with full history
• Lost & found and responsibility terms
• A complete audit log of every action

The interesting part isn't the forms — it's making a spreadsheet backend behave
under real use. So I added a caching layer, document locking with retry/backoff,
and strict data normalization so messy input becomes clean records.

It's my largest project (~26k lines) and the one I'd point to first to show I can
own a real system.

🔗 github.com/Lukyammm/administrative-workflow-system

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Storytelling version

"Whose locker is this?"

That question — asked a dozen times a day — is what started this project. Lockers,
visitor records, and signed terms were spread across spreadsheets nobody fully
trusted. When something went missing, there was no way to reconstruct what
happened.

I wanted a system where every locker, every visitor, and every action had a
record you could trust. So I built Cosign.

It registers and allocates lockers, checks visitors and companions in and out,
stores signed responsibility terms with images, and — most importantly — logs
everything for audit.

The hard part wasn't the screens; it was reliability. A spreadsheet backend isn't
built for many people writing at once, so I added caching to keep it fast,
document locks with retry/backoff to keep writes safe, and normalization so human
input becomes consistent data.

Today it answers "whose locker is this?" in seconds, with a full history behind
it. It's the project that taught me the difference between code that runs and
software a team can rely on.

🔗 github.com/Lukyammm/administrative-workflow-system

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Technical version

Built a hospital access-control app (lockers, visitors, companions, audit) on a
stack people underestimate: Google Apps Script + Google Sheets. Here's how I made
it production-grade.

The challenge: Sheets has no SQL, real quotas, and no concurrency guarantees.

What I did about it:
• **Caching layer** (`executarComCache`) with targeted invalidation per entity,
  so reads don't hammer the Sheet.
• **Document locks + retry/backoff** (`executarComLock`, `executarComRetry`,
  transient-error detection) so concurrent writes don't corrupt rows.
• **Normalization helpers** for text, numbers, dates, and time zones — the
  boundary that keeps the data clean.
• **Structured audit log** so every mutation is traceable.

Modular pages (dashboard, registrations, visitors, logs, users) routed by a
single switch keep it one deployable app with clear separation.

Takeaway: the platform isn't what makes software serious — caching, locking,
validation, and auditability are.

🔗 github.com/Lukyammm/administrative-workflow-system

#JavaScript #GoogleAppsScript #SoftwareEngineering #BackendDevelopment #HealthTech
