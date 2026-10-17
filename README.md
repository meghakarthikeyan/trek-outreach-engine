# Trek Outreach Engine

Turn a target-company list into **personalized host invitations** for a recruiting
trek — automatically. You paste a Google Sheet (or upload a CSV/Excel file) of
companies; for each one the engine finds a relevant contact, drafts a tailored
outreach email **as a Gmail draft** (never sent), and logs everything to a **Notion
CRM** so you can see at a glance who's been contacted and who replied.

Built for the HBS **NY Tech Trek**, but the workflow fits any outbound list
(prospects, recruiting, partnerships).

![status: local app](https://img.shields.io/badge/runs-locally-2f5bea)

---

## Demo

▶️ **[Watch the 2-minute walkthrough on Loom](https://www.loom.com/share/e61abfadc7f74684b581befadce6ed95)** — paste a company list, watch it research, draft the Gmail invites, and populate the Notion CRM.

---

## How it works

This is a **hybrid app**: a local web UI + a tiny Python bridge, driven by a
**Claude engine** (Claude Code / Cowork) that does the research, drafting, and
syncing through your connected accounts.

```
┌─────────────┐   paste link / upload   ┌──────────────┐   reads/writes   ┌───────────────┐
│  Web UI     │ ──────────────────────▶ │  server.py    │ ◀──────────────▶ │ Claude engine │
│ (index.html)│   POST /submit          │ (local bridge)│   submission /   │  + connectors │
│             │ ◀──────────────────────  │               │   results.json   │               │
└─────────────┘   GET /results          └──────────────┘                  └───────┬───────┘
                                                                                   │
                                        research (web) · Gmail drafts · Notion CRM │
                                                                                   ▼
```

1. You paste a **Google Sheet/Doc link** (or upload a **CSV/Excel**) in the UI and click **Research & draft**.
2. The UI sends it to `server.py`, which saves it to `submission.json`.
3. The **Claude engine** reads the sheet, researches each company, creates the Gmail drafts, writes the Notion rows, and saves `results.json`.
4. The UI polls `results.json` and renders the cards + tracker, with links straight to each Gmail draft and the Notion CRM.

> **Why a Claude engine instead of a standalone server?** The research, writing, and
> account actions run through Claude's connectors (your Google/Gmail/Notion), so there
> are **no API keys to manage and nothing is sent automatically**. The tradeoff is that
> a run is performed by the Claude engine rather than a headless backend.

---

## What you need

| Requirement | Why |
|---|---|
| **Python 3.8+** | Runs the local web server / bridge (`server.py`). No pip installs needed — standard library only. |
| A modern **web browser** | The UI (`index.html`). |
| **Claude Code or Claude Cowork** | The engine that runs the pipeline. |
| **Connectors enabled in Claude** (see below) | So the engine can read your sheet, create drafts, and update Notion. |

### Connectors to enable in Claude

Enable these in Claude (Settings → Connectors, or `/mcp` in Claude Code):

- **Google Drive** — read the pasted Google Sheet / Doc (the list of companies).
- **Gmail** — create the outreach **drafts** (create-only; the workflow never sends).
- **Notion** — create/refresh the CRM rows.
- **Web search** — built into Claude; used to research each company/contact.

> Alternatively, upload a **CSV/Excel** file instead of a Google Sheet link, and you
> won't need the Google Drive connector.

---

## Run it locally

```bash
# 1. Clone
git clone https://github.com/meghakarthikeyan/trek-outreach-engine.git
cd trek-outreach-engine

# 2. Start the local server/bridge (serves the UI on http://localhost:8000)
python3 server.py

# 3. Open the app
open http://localhost:8000        # macOS  (or just visit the URL)
```

Then, in **Claude Code** (same folder), start the engine in watcher mode so it
auto-processes whatever you paste:

```
/loop Watch submission.json; when a new sheet link / company list appears,
read it, research each company, create Gmail drafts (never send), refresh the
Notion CRM, and write results.json in the app's schema.
```

Now in the browser: **paste your sheet link → Research & draft**. Within a moment
the watcher picks it up, runs the pipeline, and the page fills in — drafts in Gmail,
rows in Notion, no further prompting.

*(Prefer manual control? Skip the `/loop` and just tell Claude Code "process the new
submission" after you paste.)*

---

## First-time configuration

The engine writes to a specific Notion database. Create your own once, then point the
app at it:

1. In Claude, ask it to create the CRM database with this schema (or make it by hand):

   ```
   Company (title) · HBS Alum (text) · Role (text) · Email (email) ·
   Confidence (select: Verified / Inferred / Needs lookup) ·
   Status (status: Not contacted → Draft ready → Email sent → Replied → Confirmed) ·
   Email sent (checkbox) · LinkedIn (url) · Gmail draft (url) · Notes (text)
   ```

2. Set **`NOTION_CRM_URL`** at the top of the `<script>` in **`index.html`** to your
   database's URL so the "Open Notion CRM" button points at yours.

3. Make sure the Google Sheet you paste is one **your** Google account can open.
   The sheet should have a **`Company`** column (an optional **`Name`** column lets the
   engine filter to just the rows assigned to you).

---

## Input format

Either:

- **A Google Sheet/Doc link** — normal `…/d/<id>/edit` links and "make a copy" links both work, or
- **A CSV / Excel file** — the first column, or a column named `Company`, is read as the list.

Example sheet columns (only `Company` is required):

| Priority | Name | Company | Stage | Contact | Notes |
|---|---|---|---|---|---|
| 1 | Megha | ElevenLabs | Late stage | Anna Serobyan | Voice AI |

---

## What the output looks like

- **Gmail drafts** — one personalized email per company, in your Drafts folder, ready to review and send.
- **Notion CRM** — one row per company with the contact, email, a **confidence flag**, the draft link, and send status.
- **In-app dashboard** — result cards + a tracker table, with "Open in Gmail" / "Row in Notion" links.

---

## Honest limitations

- **Contact emails are often _inferred_** from the company's domain pattern and flagged
  **Inferred** / **Needs lookup** (not **Verified**). Public web search does not reliably
  expose who at a company is an alum of a given school, or their exact inbox — so
  **always verify the recipient before sending.**
- **Nothing is ever sent automatically.** The engine only creates drafts — that human
  review step is intentional.
- Results and Gmail drafts refresh only when the engine runs (watcher tick or a manual
  "process it"); the web server by itself does not research or draft.

---

## Project structure

```
index.html     # the web UI (single file: HTML + CSS + JS)
server.py      # local bridge: serves the UI, stores submissions, serves results
README.md
.gitignore     # ignores runtime state (submission.json, results.json)
```

---

Built with [Claude Code](https://claude.com/claude-code).
