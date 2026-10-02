# Deployment Pages as Tools — the fleet design language

Date: 2026-10-03. Status: doctrine, with one reference implementation
(`docs/foundry.html`). Applies to every repo that can host a static page
(GitHub Pages; Cloudflare Pages when functions outgrow static).

## The thesis (Kimi, 01:06)

A repo's deployment page should be **a tool agents visit**, not a brochure
humans read. Revolutionary iff:

- **Agents play-test it and come back** — because it does their job
  smarter / faster / for fewer tokens, or returns a unique artifact that
  compiles and plugs into their project.
- **Humans jump through settings** — fill boxes, click compile, download
  (or just download for JIT formats: TS interpreted, JS read-through,
  Python read-through).
- **The page is the runtime** — flow-state without an instance; other
  agents use the page as the boilerplate application and never clone.

## The two doors (one page, two species)

| | agents | humans |
|---|---|---|
| input | **URL params** (`?name=x&caps=a,b&type=ballot`) | form fields |
| output mode | `?raw=1` → `text/plain` code blocks, pipe straight to a file | rendered blocks + **Compile → Download** (Blob) |
| interaction | zero clicks; GET, read, leave with the artifact | play, watch ah-ha, tweak, download |
| discovery | linked from README with a ready-made `curl` one-liner | linked from README with a screenshot |

The same static file serves both. No backend. No build step. The page is
the compiler.

## Ah-ha moment grammar (what makes the click)

1. **Playground first** — the page must *do the repo's thing* in-browser
   before explaining it. (warp: ballot → gate flips. holdem: WAL replay.
   nb: time-walk a note. fleet/omz: the dot.)
2. **A parameter visibly changes the artifact** — agents see cause→effect
   in the generated code; humans see the same in the form.
3. **Compile & download is one gesture** — and for interpreter formats the
   "compile" is a no-op; say so proudly (JIT honesty).
4. **Receipts culture survives the browser** — generated bundles carry a
   content hash (h16), pins are FAIL-first, P0 demonstrates RED before
   first run.
5. **Deterministic** — same params → same hash → same bytes. Agents can
   cite the hash in their own receipts ("tool obtained from foundry@
   <hash>").

## Real-world-useful bar (the honest test)

An agent should be able to: GET the page with params → receive a working
plugin module + pin scaffold → drop it into `platform/plugins/` → pass
the host's contract on first load. If any step fails, the page is a demo,
not a tool. `docs/foundry.html` is built to this bar.

## Boundaries (sealed)

- Static pages can't keep secrets or state; anything needing auth, big
  compute, or persistence graduates to Cloudflare Pages + functions and
  says so on the page.
- The browser demo is not the product's evidence; pins in repos remain
  the evidence. Pages generate *candidates*; pins *admit* them.
