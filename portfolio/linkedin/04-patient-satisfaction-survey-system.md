# LinkedIn — Patient Satisfaction Survey System

**Repo:** github.com/Lukyammm/patient-satisfaction-survey-system
**Suggested images (carousel, in order):**
1. `01-home.png` — overview with summary cards
2. `02-dashboard.png` — satisfaction / NPS charts
3. `03-feature-main.png` — manifestations (complaints/compliments)
4. `04-result.png` — report + CSV export

---

## Short version

Patient feedback is only useful when it becomes a number you can act on.

I built a system that captures surveys, sorts manifestations (complaints,
compliments, suggestions) by service area, and computes satisfaction and NPS —
with CSV export for deeper analysis.

🔗 github.com/Lukyammm/patient-satisfaction-survey-system

#JavaScript #GoogleAppsScript #Analytics #HealthTech #OpenToWork

---

## Medium version

"How satisfied are our patients?" is easy to ask and hard to answer when the
feedback is a pile of free-text rows.

I built a system that turns that pile into decisions:
• Captures surveys across service blocks (reception, care, services)
• Sorts manifestations — suggestions, complaints, comments, compliments
• Computes satisfaction scores and NPS automatically
• Exports clean CSV for deeper analysis

The real engineering is in trusting the numbers. Real survey data writes the same
department ten different ways, so I built a fuzzy-matching pipeline that merges
them into canonical sectors, plus deduplication — so the NPS you see is honest,
not an artifact of messy input.

🔗 github.com/Lukyammm/patient-satisfaction-survey-system

#SoftwareDevelopment #JavaScript #DataEngineering #HealthTech #OpenToWork

---

## Storytelling version

The dashboard looked great — until I noticed the same department listed five
times, each spelled slightly differently, each with its own score. The numbers
were precise and completely untrustworthy.

That bug taught me what this project was really about. Capturing patient feedback
is the easy half; making the resulting metrics honest is the hard half.

So I built a canonicalization pipeline: a scoring function that recognizes
"Pronto Socorro", "P. Socorro", and "pronto-socorro" as the same place, merges
them, and deduplicates the records. Only then do the satisfaction and NPS numbers
mean anything.

On top of that sits the part users see — survey capture, manifestations sorted by
service block, reports, CSV export. And because restructuring live data is scary,
the migration backs up the sheet first and refuses to run twice.

It's the project that turned me from "I can build a form" into "I can make data
you can trust."

🔗 github.com/Lukyammm/patient-satisfaction-survey-system

#SoftwareDevelopment #JavaScript #DataEngineering #HealthTech #OpenToWork

---

## Technical version

Building patient-satisfaction analytics on Google Apps Script — the hard part is
data quality, not charts.

What's inside:
• **NPS classification + satisfaction scoring** computed server-side
  (`classifyNps_`, `satisfaction_`, `countRating_`) so every view agrees.
• **Sector canonicalization** — a scoring-based fuzzy-match pipeline
  (`sectorNameScore_`, `buildSectorCanonicalMap_`, `canonicalSector_`) that
  collapses inconsistent department names into one canonical sector.
• **Deduplication** of records before aggregation.
• **Safe migration** (`migrateToBlockManifestations`) that auto-backs-up and is
  idempotent.
• **CSV export** with proper cell escaping.

Lesson: an analytics tool is only as good as its normalization layer. Charts are
the easy 20%.

🔗 github.com/Lukyammm/patient-satisfaction-survey-system

#JavaScript #GoogleAppsScript #DataEngineering #Analytics #HealthTech
