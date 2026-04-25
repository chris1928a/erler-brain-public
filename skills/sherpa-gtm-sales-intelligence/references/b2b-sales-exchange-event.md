# B2B Sales Exchange Event — 24. April 2026

## Event Details
- **Titel:** MyEO Experience Share — Claude Skills für Sales Organisationen
- **Datum:** 24. April 2026
- **Hosts:** Philipp Ströhemann (PAS Ventures), Manuel Hartmann (SalesPlaybook), Chris Erler (Erler Ventures)
- **Format:** 20min Main Section + 30min Q&A
- **Luma Link:** (event organizer's calendar)
- **Google Doc Agenda:** (private, shared with hosts)

## Meta-Narrativ
Alle drei Hosts zeigen verschiedene Anwendungen derselben Datenquelle (Call Transcripts):
- **Phil:** Transcripts → Marketing Assets (ICP, Sales Scripts, Landing Pages, Ads, Content)
- **Manu:** Transcripts → Sales Tools (Case Studies, Offers, ROI Calculator, ICP)
- **Chris:** Transcripts → Individualized Coaching (Gap-Detection, Call Scoring, Framework-Empfehlungen, ICP Feedback Loop)
- **Umbrella-Theme:** "Transcripts as Gold Mine"

## Agenda-Struktur (Main Section 20min)
1. 🔍 Skills Overview (Philipp) — Was sind Claude Skills, warum Sales & Marketing
2. 🚀 Real Results (Philipp) — €12 Demo Funnel, AI Sales Scripts, ICP Refinement
3. 🎯 Manuel: Where AI actually works (3 Use Cases) — Case Studies, ROI Calculator, ICP & Pattern Recognition
4. 🎯 Chris: From Transcripts to Individualized Coaching (2 Use Cases)
5. 🔥 Discussion Prompts (optional)
6. ❓ Audience Q&A (30min)

## Chris' Abschnitt (wie im Google Doc eingereicht)

### 🎯 4. Chris: From Transcripts to Individualized Coaching

Phil zeigt, wie Transcripts zu Marketing Assets werden. Manu zeigt Sales Tools. Hier die dritte Dimension: Dieselben Call-Daten fließen zurück ins Team als individuelles Coaching.

#### 💡 Use Case 4: Automated SDR Coaching

**Problem:**
- Dashboard sagt allen Reps dasselbe: "Pitch-Problem"
- 3 Reps, 3 komplett verschiedene Schwächen, eine Diagnose
- Coaching basiert auf Bauchgefühl, nicht auf Daten

**Solution:**
- CRM-Daten (Close.com API) + Call Transcripts (Deepgram) laufen jede Nacht durch ein Scoring
- Gap-Detection Matrix: Aktivität vs. Outcomes auf zwei Achsen, ergibt 9 verschiedene Diagnosen statt einer
- Call Scoring in 6 Dimensionen (Opener, Pitch, Einwandbehandlung, Closing, Gesprächstiefe, Rapport)
- Schwächste Dimension = konkretes Framework als Coaching-Fokus der Woche (LARC, SPIN, Pattern-Interrupt, 3-Sekunden-Pause)

👉 **Ergebnis:**
- Jeder Rep bekommt individuelle Coaching-Empfehlung pro Woche
- Manager spart Vorbereitungszeit, Rep weiß genau was er üben soll
- Closed Loop: Nächste Woche misst das System, ob sich die Dimension verbessert hat

#### 💡 Use Case 5: ICP Validation from Call Patterns

**Problem:**
- ICP basiert auf Annahmen, nicht auf echten Gesprächsdaten
- Keiner weiß, welche Segmente wirklich konvertieren

**Solution:**
- 256 Calls analysiert: 52% scheitern am Gatekeeper, nur 7% echtes Engagement
- Lost Reasons zeigen gehäufte Einwände = Markttrends, nicht Einzelfälle
- Call-Sprache fließt zurück in Ad Copy, Email-Cadences, Landing Pages

👉 **Ergebnis:** ICP-Shift (raus: Firmen <50 MA, rein: Tech-Scaleups mit Spezialrollen). Sales-Daten steuern Marketing mit.

**Takeaway:** Reporting zeigt was passiert. Dieses System sagt jedem Rep, was er diese Woche üben soll. Blueprint ist Open Source auf GitHub.

### Bio (für "About the Hosts")
**Christoph Erler:** Founder Erler Ventures. Hat für eine Recruiting Agency ein Sales Leadership Board gebaut, das CRM-Daten (Close.com API) automatisch in individuelle Coaching-Empfehlungen, Red Flags und ICP-Updates umwandelt. 256 Calls analysiert, Open Source Blueprint auf GitHub.

## Präsentation
- **Chris-Slot Deck (FINAL, Phil-Brand, 10 Slides):** `presentation/chris-deck.html`
- **Komplette Storyline + WHY + Speaker Notes + Q&A:** `presentation/STORYLINE.md`
- **Alt-Deck (Dark Theme, 14 Slides):** `presentation/index.html` + `presentation/Sales-Leadership-Board-Presentation.pdf` (deprecated, wird ersetzt)
- **GitHub Repo:** https://github.com/chris1928a/sales-leadership-board

## Live-Assets (für Screen-Share-Momente)
- **Live Dashboard:** Live Google Sheet with real rep scores (not linked publicly — client data).
- **ICP Assessment v1:** Original analysis of 256 calls (private client deliverable).
- **ICP Assessment v2:** Rebuild with new ICP cut after Sherpa Skill rollout (private).

## Demo-Plan
- Nach Slide 5 (6-Dim Stack): 20s Screen-Share aufs Live-Dashboard — "Das ist kein Mockup, läuft seit März"
- Slide 8 (Shift 3 "Handoff to Marketing"): 45s Toggle zwischen ICP v1 und v2 — "Sales-Daten haben Marketing umgebaut, nicht umgekehrt"
- Hart-Limit: 60s Gesamt-Live-Demo im 10-min-Slot, sonst reißt Pacing

## Kernthese der Präsentation
"Euer CRM weiß, was schiefläuft. Ihr hört nur nicht zu."

## EO AI Exchange — Referenz-Setups anderer Teilnehmer

### Daniel Miessler — Personal AI Infrastructure (PAI)
- **Repo:** https://github.com/danielmiessler/Personal_AI_Infrastructure/tree/main
- **Version:** v4.0.3 (März 2026), 11.7k Stars, MIT
- **Kern:** Claude Code als Foundation, persistente Identität (TELOS = 10 Dateien: MISSION, GOALS, BELIEFS etc.)
- **Primitives:** Assistant-Mode, USER/SYSTEM-Trennung, Skill-System (Code → CLI → Prompt → Skill), Memory (hot/warm/cold), Hooks (8 Lifecycle-Events), Security AllowList, Notifications (ntfy/Discord/ElevenLabs)
- **11 Packs:** ContextSearch, Research, Telos, ContentAnalysis, Investigation, Security, Media, Thinking, Scraping, USMetrics, Utilities
- **Philosophie:** "Scaffolding > Model", CLI-First, Code vor Prompts, Open-Source fuer die Masse
- **Differenzierung:** PAI = Infrastructure (HOW), Fabric = Prompts (WHAT)

## Slide-Übersicht (14 Slides)
1. Sales Leadership Board — Titel
2. Ausgangslage — 3 Reps, 3 Probleme, 1 Dashboard
3. Red Flag System — Automatische Diagnose pro Rep
4. Gap-Detection Matrix — 9 Diagnosen statt einer (2-Achsen-System)
5. Call Scoring — 6 Dimensionen
6. Coaching Frameworks — LARC, SPIN, Pattern-Interrupt, 3-Sekunden-Pause (mit WHY)
7. Coaching Closed Loop — Schwächste Dimension → Framework → Nächste Woche messen
8. Learning ICP — 256 Calls analysiert, Gatekeeper-Quote, Engagement-Rate
9. Learning Ads/Outbound — Call-Sprache fließt in Marketing
10. Architektur — Close.com API → Deepgram → Claude → Google Sheets → Telegram
11. Der Loop — Red Flags → Coaching → Learning → bessere Calls
12. Blueprint — Open Source auf GitHub
13. Takeaways — 3 Key Messages
14. Q&A
