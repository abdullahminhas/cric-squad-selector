Understood — let's raise this to a genuinely professional standard, not just "fix the bugs." Here's a full, detailed spec covering visual design, layout, and interaction quality, while staying honest to what your data and model can actually support.

---

## Design System (give this to your assistant as the foundation)

**Colour palette:**
- Background: white / very light grey (#F8F9FA)
- Primary text: dark navy (#1A2332) or near-black
- Accent colour: one muted, professional blue (#1D4E89) for buttons, links, active states
- Role-based tags: Batsman (green #2E7D32), Bowler (red/maroon #B71C1C), All-rounder (blue/purple #4527A0) — used consistently everywhere, not just one table
- Success/positive indicators: green; caution/low-confidence: amber, not red (red should be reserved for errors only)

**Typography:** one clean sans-serif (Inter, or system default), clear hierarchy — large page titles, medium section headers, consistent body text size. No default browser styling left unstyled.

**Layout principles:** generous whitespace, card-based sections (not raw HTML tables with no styling), consistent spacing/padding, subtle borders or shadows to separate sections — should feel like a real analytics product (think a clean sports-data dashboard), not a prototype.

---

## Page-by-page professional spec

### 1. Squad Generation Page

**Form section:** three dropdowns (Format, Team, Opposition) inside a clean card, with a clear "Generate Squad" primary button. Add a loading state (spinner or skeleton) while the squad is generating, not a blank pause.

**Results — upgrade from a plain table to a structured squad view:**
- Header summary bar at top: "ODI Squad — Pakistan vs India" with the two team names/flags-as-text, format, and date generated.
- Group players visually by role in three sections (Batsmen / Bowlers / All-rounders), each as a small card grid, not one long undifferentiated table — this reads as far more professional and matches how real squads are actually presented.
- Each player card shows: name, team, role tag, captain/vice-captain badge where relevant, and their key predicted stat (runs for batsmen/all-rounders, wickets+economy for bowlers — using the corrected, non-negative bowler metric from before).
- Clicking or expanding a player card reveals the **Selection Analysis** panel underneath: recent form (last 5/10), opposition-specific record, and a short one-line explanation such as *"Selected primarily due to strong recent form and a high average against this opposition."* (a simple templated sentence generated from which stat is strongest — not a new model, just a small rule-based summary line).

### 2. Selection Probability
Displayed as a small horizontal bar or circular indicator next to each player's predicted stat, with a percentage label (e.g. "84% confidence"). Convert the raw predicted score into this percentage using a simple normalization against the format's realistic score range (the `max_runs_by_format` caps you already have double as a natural ceiling for this calculation).

### 3. Player Form Dashboard
- A proper search bar with autocomplete/type-ahead (not just a plain dropdown of hundreds of names).
- Player profile header: name, team, primary role.
- Two clearly separated sections: **Career Stats** (batting average, strike rate, bowling average, economy) shown as stat cards with large numbers and small labels, and **Recent Form** showing last 5 and last 10 match trends — ideally a small line/bar chart if your assistant can add a lightweight charting library (e.g. Chart.js), so form is visually readable, not just numbers in a row.

### 4. Authentication
Clean, centred login/register cards, consistent with the rest of the site's design system, clear inline validation messages (not browser default alerts), and a proper navbar state change (avatar/initials + dropdown for logged-in users, not just plain text).

### 5. Overall polish expected throughout
- Consistent navbar across all pages, with the active page highlighted.
- A proper footer (project name, maybe a small note like "Built using Random Forest + XGBoost on Cricsheet data").
- Empty states handled gracefully (e.g. "No players found for this combination" instead of a blank page or error).
- Fully responsive on mobile — squad cards should stack cleanly, not just shrink.

---

**One honest note:** the "one-line explanation" and probability percentage are presentation-layer improvements built from data/scores you already have — no new model training needed. The charts on the Player Dashboard are also just visualizing existing CSV data. So this raises the professional feel significantly without requiring more ML work, which matters given your timeline.

Want me to now combine this with the earlier bug-fix list (missing Team dropdown, negative bowler scores, etc.) into one single, ordered document you can hand directly to your AI assistant, step by step?