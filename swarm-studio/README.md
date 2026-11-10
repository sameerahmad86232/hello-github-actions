# Swarm Studio — Codex-first MVP

A Head Coach workflow, **20 permanent website-building specialist roles**, and a phone-friendly studio showing **actual agent reports and filesystem changes**, not simulated activity.

## Requirements
- Node.js 20+ (no npm dependencies)
- A supported coding-agent environment such as Codex to supply reasoning and file editing

## Run locally or from GitHub Codespaces

Open the `swarm-studio/` folder in a Codespace terminal:

```bash
npm run studio
```

Open the forwarded **4173** port in your phone browser. The server binds to `127.0.0.1` by default; GitHub Codespaces port forwarding can provide a protected URL. Never make a preview with sensitive project information publicly accessible.

To prepare a concrete website project:

```bash
node scripts/coach.mjs init --name "Northstar" --audience "Small business owners" --goal "Launch a clear service website" --cta "Contact us" --pages "Home,Services,FAQ" --colors "#152a42,#f5f9fc"
```

The command creates `workspace/BRIEF.md`, `workspace/OWNERSHIP.md`, `workspace/site/tokens.css`, `workspace/site/content.json`, `workspace/PROJECT.json` and 20 specialist task prompts. It **does not** run AI agents or fabricate their output.

Then in Codex working in this directory, say: **Use the `swarm-studio` skill to build my site. Start Wave 1 and show each signed report before continuing.** Codex can delegate real independent subtasks when host subagent tools are available. Otherwise it should run sequentially and disclose that limitation.

Agent event examples (used during actual Codex work):

```bash
node scripts/emit.mjs --agent hero --type start --text "Building hero fragment"
node scripts/emit.mjs --agent hero --type place --file site/sections/hero.html --text "Hero file created"
node scripts/emit.mjs --agent hero --type done --text "Hero implemented and reviewed"
```

`place` rejects a nonexistent file. The file observer independently counts real changes and streams them to the UI. The viewer shows a *live composite of actual section fragments* before the integrator writes `site/index.html`.

## Files
- `.agents/skills/swarm-studio/SKILL.md`: Codex project-local skill
- `.codex-plugin/plugin.json`: Codex plugin package manifest (preview packaging; not published)
- `agents/*.md`: 20 signed specialist job contracts
- `config/roles.json`: roles, ownership and wave plan
- `scripts/coach.mjs`: init and prompt generation
- `scripts/emit.mjs`: truthful worker status events
- `scripts/server.mjs`: local file observer, SSE feed, preview server
- `studio/`: actual event-driven browser interface
- `workspace/`: generated site, inputs and reports (gitignored)

## Truthful limitations
No Codex session is automatically launched by `npm run studio`; Codex must invoke the skill and perform the work. Twenty *definitions* do not imply twenty simultaneously active agents. Event timestamps show reported job starts/dones; `file` events show independently observed filesystem changes. Performance and browser responsiveness checks must be executed before marking a generated site ready for export. No zip-export UI or cross-provider adapter is shipped in this MVP.

## Test

```bash
npm test
```
