# Hermes Web UI — Roadmap

> Web companion to the Hermes Agent CLI. Same workflows, browser-native.
>
> Last updated: v0.51.31 (May 9, 2026) — 5028 tests collected — Release H 12-PR contributor batch (image-mode fix + race fixes + composer drafts + locale parity + custom-provider dedup + TTL config + heartbeat polish)
> Test source: `pytest tests/ --collect-only -q`
> Per-version detail: see [CHANGELOG.md](./CHANGELOG.md)

---

## Status snapshot

| Surface | Status |
|---|---|
| **Hermes CLI parity** | ✅ Complete — every CLI workflow has a web equivalent |
| **Streaming + tool transparency** | ✅ Live tool cards, reasoning cards, approval prompts, cancel |
| **Multi-provider model support** | ✅ Any provider configured in `config.yaml` shows in the picker |
| **Sessions + projects + search** | ✅ CRUD, content search, projects, tags, archive, fork, import |
| **Mobile + Docker + auth** | ✅ Hamburger nav, slide-overs, password auth, GHCR images |
| **Auxiliary surfaces** | ✅ Workspace tree + edit, cron CRUD, skills CRUD, memory write, MCP server UI |
| **Visual polish** | ✅ 8 themes (incl. light/system/OLED/Sienna), Mermaid, KaTeX, syntax highlighting |
| **Native distribution** | ✅ macOS desktop app (universal arm64+x86_64 DMG, signed) — separate repo |

Remaining gaps and forward work live in [Forward Work](#forward-work) below.

---

## Architecture

| Layer | Files | Status |
|---|---|---|
| Python server | `server.py` (~165 lines) + `api/` modules (~20k lines) | Thin shell + auth middleware + business logic |
| HTML template | `static/index.html` (~600 lines) | Served from disk |
| CSS | `static/style.css` (~3k lines) | Themes, mobile responsive, KaTeX, table styles |
| JavaScript | `static/{ui,sessions,messages,workspace,panels,boot,commands,icons,i18n,login,onboarding}.js` (~26k lines) | 11 modules served as static files |
| Service worker | `static/sw.js` | Offline shell cache, version-pinned assets |
| Docker | `Dockerfile`, `docker-compose.yml` | `python:3.12-slim`, multi-arch (amd64+arm64), HEALTHCHECK |
| CI/CD | `.github/workflows/release.yml` | Auto-release + GHCR publish on tag push |
| Test isolation | `tests/_pytest_port.py` | Per-worktree port + state-dir derivation, no collisions |

---

## Feature parity checklist




















---

## Forward work

### Confirmed candidates (open feature requests with sprint-candidate or active interest)

| Theme | Tracking | Why |
|---|---|---|
| Persistent-host stability | #1458 | Bootstrap fork pattern crashes under launchd / systemd — partial fix shipped (foreground mode); state.db FD leak and HTTP-unhealthy wedge remain |
| Free-tier OpenRouter variants visible | #1426 | `:free` tool-support filter currently hides them from the picker |
| macOS scroll override regression | #1360 | Auto-scroll sometimes overrides user scroll on the desktop app |
| GLM dual-use (main + auxiliary) | #1291 | Currently mutually exclusive; same provider can't serve both surfaces |
| Auto-assign session to filtered project | #1468 | When user is filtering by project X, new session should default to project X |
| Update banner "What's new?" link | #1512 | Surface release highlights from the update banner |
| Sunset legacy `LMSTUDIO_API_KEY` env var | #1502 | Tracking issue — alias stays for one minor cycle, then removed |
| Hermes Agent dashboard cross-link | #1459 | Detect a running Hermes Agent and surface link in nav |
| Gateway status card in Settings | #1457 | Current gateway-status dots only on profile picker |
| Insights — daily token chart + per-model breakdown | #1456 | Existing usage badge is per-message; need rollup view |
| Logs tab — view agent / errors / gateway logs | #1455 | Currently requires terminal access to log files |
| Model picker collision handling | #1425 | Same-name models from different providers aren't disambiguated in dropdown |
| "Reveal in Finder" right-click on workspace | #1424 | macOS desktop app convenience |
| Configurable session persistence timing | #1406 | Currently every checkpoint, want operator control |
| Silent credential self-heal on 401 | #1401 | Gateway auth.json drift should resolve without user re-auth |
| LLM Wiki status panel | #1257 | On / off toggle for Wiki integration |
| Lightweight in-app Canvas editing | #1255 | Text canvas for prompt drafting / shared notes |
| Provider / Model source-of-truth alignment | #1240 | Reconcile WebUI vs CLI vs Gateway provider resolution |
| Built-in SearXNG web search | #1037 | Lightweight search tool with on / off toggle |
| Subagent session relationship view | #1004 | Show subagent hierarchy in sidebar with expand / collapse |

### Backlog (deferred, listed for visibility)

- **Insights / monitoring suite** — agent heartbeat + alerts (#716), quota / rate-limit display (#706), data tabs (#722), monitor dashboard concepts (#766, #721)
- **Native MCP server expose** — Hermes WebUI as an MCP server for direct agent integration (#733)
- **Teams / agents management panel** — editable names, roles, assignments (#719)
- **Web UI profile model alignment with Hermes runtime** — design parity (#749)
- **DOM windowing / message virtualization** — for sessions with hundreds of messages (#734)
- **Searchable global tool list** (#697)
- **Add agent / replace model modals** (#698)
- **Code execution inline cells** — Jupyter-style cell rendering inside chat
- **Sharing / public conversation URLs** — requires hosted backend with access control (out of scope for self-host)

### Intentionally not planned
- Full SwiftUI rewrite of the frontend — the WKWebView shell already gets 95% of native benefit
- App Store distribution — sandboxing breaks the local server model
- Real-time multi-user collaboration — single-user assumption throughout
- Plugin marketplace — Hermes skills cover this surface
- Anthropic / Claude proprietary features — Projects AI memory, Claude artifacts sync (not reproducible)

---

## Sprint history

Per-version detail lives in [CHANGELOG.md](./CHANGELOG.md). The table below is a high-level chronology of major sprint themes; individual PR / fix detail moved to CHANGELOG to keep this file readable.

| Range | Theme | Highlights |
|---|---|---|
| Sprints 1–6 | Foundations + workspace | server / static split, JS module split, workspace CRUD, file editor, message queue + INFLIGHT, isolated test environment |
| Sprint 7 | Wave 2 core | Cron / skill / memory CRUD, session content search, health endpoint, git init |
| Sprint 8 | Daily-driver finish line | Edit + regenerate, regenerate last response, clear conversation, Prism.js, queue + INFLIGHT polish |
| Sprints 9–10 | Codebase health + operational polish | `app.js` → 6 modules, server.py → `api/` modules, tool card UX, background task cancel, regression tests |
| Sprint 11 | Multi-provider models + streaming | Dynamic model dropdown, smooth scroll pinning, routes extracted to `api/routes.py` |
| Sprint 12 | Settings + reliability + session QoL | Settings panel, SSE auto-reconnect, pin sessions, JSON import |
| Sprint 13 | Alerts + polish | Cron alerts, background error banner, session duplicate, browser tab title |
| Sprint 14 | Visual polish + workspace ops | Mermaid, message timestamps, file rename, folder create, session tags, archive |
| Sprint 15 | Session projects + code copy | Projects / folders, code copy button, tool card expand / collapse |
| Sprint 16 | Sidebar visual polish | SVG icons, action dropdown, pin indicator, project border, safe HTML rendering |
| Sprint 17 | Workspace polish + slash commands | Breadcrumb nav, slash command autocomplete, send key setting (#26) |
| Sprint 18 | Thinking display + workspace tree | File preview auto-close, thinking / reasoning cards, expandable directory tree (#22) |
| Sprint 19 | Auth + security hardening | Password auth, login page, security headers, body limit (#23) |
| Sprint 20 | Voice input + send button | Web Speech API voice, send button polish |
| Sprint 21 | Mobile responsive + Docker | Hamburger sidebar, mobile nav, slide-over files, Docker support (#21, #7) |
| Sprint 22 | Multi-profile support | Profile picker, management panel, seamless switching, per-session tracking (#28) |
| Sprint 23 | Agentic transparency | Token / cost display, subagent cards, skill picker in cron, profile-local storage |
| Sprint 24 | Web polish | rAF streaming, git detection, collapsible date groups, context ring (#80, #81, #82, #83) |
| Sprint 25 | macOS desktop application | Native Swift + WKWebView shell, universal DMG, Sparkle 2 auto-update — separate repo |
| Sprint 26 | Pluggable themes | Light / Slate / Solarized / Monokai / Nord, settings unsaved-changes guard, `/theme` |
| Sprint 27 | Theme polish | 30+ hardcoded colors → CSS variables, light theme final polish |
| Sprint 28 | Security hardening | Env race fix, random signing key, upload traversal, PBKDF2 |
| Sprints 29–32 | Model routing + custom endpoints + reasoning | Model routing by provider prefix, custom endpoint URL fix, OLED theme, top-level reasoning, message_count sync |
| Sprint 33 | Approval card + Lucide icons | Approval prompt surfaced, emoji → SVG, login CSP fix, update diagnostics |
| Sprint 34 | v0.50.0 UI overhaul | Composer-centric controls, Control Center modal, workspace state machine, collapsible date groups, rAF throttle, context ring |
| Sprints 35–37 | Onboarding + i18n + Spanish | First-run wizard, OpenRouter / Anthropic / OpenAI / Custom config, Spanish locale, Docker two-container, mobile Profiles button |
| Sprints 38–40 | Session + UI polish + Sprint 40 | Five-bug clean-up + sidebar timestamp + test port isolation |
| Sprints 41–42 | Renderer hardening + KaTeX + handoff | Context ring live usage, renderMd link / image / code stash chain, MEDIA: image rendering, gateway handoff foundation |
| Sprints 43+ | Continuous contributor sprints | Custom providers, Russian locale, IME fixes, model-switch toast, approval queue multi-slot, profile polish, font-size CSS, contributor wave |

---

## Sprint methodology

A sprint is a thematic batch (usually 3-8 PRs). External contributor PRs that
do not fit a planned sprint ship individually as patch versions. Active sprint
candidates are tracked via the `sprint-candidate` GitHub label.

Pre-release gate (mandatory): `pytest tests/ -q --timeout=120` clean, browser
sanity check, Opus advisor pass on the merged stage diff, CHANGELOG/ROADMAP
version stamp, and CI green on Python 3.11/3.12/3.13.

## Versioning conventions

- **Patch** (`v0.50.X`) — small batches, contributor PR releases, hotfixes
- **Minor** (`v0.X.0`) — sprint completion, new feature surface, architecture milestone
- **Major** (`v1.0.0`) — declared when CLI parity + Claude parity reach steady state and the feature surface stabilizes

Per-version detail and contributor attribution live in [CHANGELOG.md](./CHANGELOG.md).