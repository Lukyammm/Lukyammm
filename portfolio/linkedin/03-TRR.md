# LinkedIn — TRR (Rapid Response Team Call System)

**Repo:** github.com/Lukyammm/TRR
**Suggested images (carousel, in order):**
1. `01-home.png` — Clinical / Surgical type selection
2. `03-feature-main.png` — MEWS criticality during intake
3. `02-dashboard.png` — open calls with criticality colors
4. `05-mobile-view.png` — new-call flow on mobile

---

## Short version

When a patient deteriorates, the Rapid Response Team has seconds — not time for a
clunky form.

I built TRR: pick Clinical or Surgical, capture the patient, set criticality from
the MEWS scale, and track the call against an SLA. Fast at the bedside, secure
behind the scenes.

🔗 github.com/Lukyammm/TRR

#JavaScript #GoogleAppsScript #HealthTech #WebDevelopment #OpenToWork

---

## Medium version

Some software has to be fast because seconds matter.

TRR is the call-intake app for a hospital's Rapid Response Team. When a patient
deteriorates, anyone can open a call in two taps — Clinical or Surgical, no login
required — then capture the patient and set criticality straight from the MEWS
scale shown on screen.

Behind that simple front door, I built real security: salted and hashed
passwords, timing-safe comparison, brute-force lockout, password-reset tokens,
and session handling — because the data is clinical and the staff actions need to
be protected. Calls are then tracked against SLA targets so nothing slips.

The design principle: optimize for the moment that matters (raising the alarm),
without compromising on security.

🔗 github.com/Lukyammm/TRR

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Storytelling version

The brief was almost intimidating: build the tool people reach for when a patient
is crashing. If it's slow or confusing, it's worse than useless.

So I made the first step ruthlessly simple. Open TRR, choose Clinical or
Surgical, and you're already capturing the patient — no login, no friction, just
the MEWS criticality table on screen to guide the call. That's the part the team
sees.

The part they don't see is where I spent the most care. This is clinical data and
staff actions, so I implemented authentication properly from scratch on Apps
Script: salted password hashing, timing-safe comparison, lockout after repeated
failed logins, reset tokens, sessions. Then SLA tracking, so response times are
measured, not guessed.

Building something for a high-stakes moment changed how I think about software:
the easy path for the user and the hard, careful path under the hood are the same
project.

🔗 github.com/Lukyammm/TRR

#SoftwareDevelopment #JavaScript #GoogleAppsScript #HealthTech #OpenToWork

---

## Technical version

How I built a rapid-response call app on Google Apps Script that's fast for users
and genuinely secure under the hood.

UX decisions:
• **No login to open a call, login to manage it** — optimize the alarm, protect
  the data.
• **MEWS table on screen**, color chosen by the operator — support the clinical
  decision, don't hide it.

Security (implemented, not assumed — Apps Script gives primitives, not a
framework):
• Salted + hashed passwords (`gerarSaltSenha_`, `hashSenhaComSalt_`)
• Timing-safe comparison (`timingSafeEqualHex_`)
• Brute-force lockout via failed-attempt tracking
• Password-reset tokens + session cache
• SLA targets with correct server-side time-zone handling

~7.7k lines total. The takeaway: "simple stack" and "real security" aren't a
contradiction.

🔗 github.com/Lukyammm/TRR

#JavaScript #GoogleAppsScript #SoftwareEngineering #Security #HealthTech
