# The Warp Constellation — a quilt-plugin digest

Date: 2026-10-03. Author: fleet lane (main session). Status: charter for the
warp rebuild. Every claim about a repo cites its README of record; where a
repo has moved since, the plugin contract below is the target, not the
current code.

## The step-back insight

The constellation was built as *separate experiments orbiting an idea*
(warp-level primitives as agent infrastructure). Rebuilt right, the idea
inverts: **quilt is the substrate; warp is a plugin host; every satellite
repo is a plugin module.** Nothing here rivals quilt's kernel — everything
rides it.

```
                        quilt  (kernel, receipts, tiling, WAL law)
                          │
        ┌───────────┬─────┴─────┬────────────┬─────────────┐
     agentic      consensus   execution    rooms/         silicon
     host         primitives  plugins      topology       emulation
     (warp)       (vote*)     (flux,       (warp-room,    (quilt-silicon)
                  (ternary*)   cudaclaw)    holodeck-cuda,
                               (drone-fleet) room-topology,
                                            vessel-nav)
```

## Repo → plugin-role map (14 satellites + core)

| repo | plugin role | capability surface | status (README of record) |
|---|---|---|---|
| `warp` | **agentic host core** — editor/terminal shell, a2a coordination | session orchestration, agent registry, UI | dormant 2026-07-12; rebuild target |
| `quilt-silicon` | silicon emulator plugin | SIMT warp emulation over quilt-arch kernels | newest (Sep 26); the seam that named this digest |
| `warp-vote-consensus` | consensus plugin | 2-bit ternary ballot, quorum tree, CRDT merge, 10k agents | mature concept, 4-cycle ballot math |
| `warp-ternary-vote` | consensus plugin (sim) | 32-thread {-1,0,+1} warp-vote simulation | experiment |
| `ternary-warp` | arithmetic plugin | clamp/quantize/fold/warp over Z₃ | library |
| `ternary-warp-block` | arithmetic plugin (block-scoped) | Z₃ ops at block granularity | crate |
| `ternary-auto-vectorizer` | compiler plugin | scalar Z₃ → warp-level, equivalence proofs | proofs included |
| `warp-flux-poc` | constraint-execution plugin | lattice snap, proof chains | PoC |
| `cudaclaw` | CRDT execution plugin | persistent CUDA kernels, warp-level consensus | ⚡ project |
| `cudaclaw-bridge` | bridge plugin | Flux→PTX oxide pipeline ↔ cudaclaw runtime | bridge |
| `holodeck-cuda` | world plugin | 16K rooms, 65K agents, warp-level combat | ⚡ project |
| `warp-room` | room plugin | C17 subroutine-threaded tile classifier | ported concept |
| `room-topology` | topology plugin | doors as continuous maps, warp ⇒ non-trivial π₁ | math core |
| `vessel-room-navigator` | viewer plugin | boat as navigable 3D web space | web viewer |
| `drone-fleet-ternary` | **application** (consumer, not plugin) | ternary decisions + warp-vote coordination | uses the stack |

## The plugin contract (what every module must satisfy)

1. **Manifest**: name, version, capabilities[], pins_path. Loaded manifests
   are receipted (content hash) by the host — load ≠ trust, pins = trust.
2. **Capabilities are verbs, not adjectives** — `vote.ballot`, `emulate.warp`,
   `room.enter`. The host session cites capability + manifest hash per call.
3. **Effects are gated**: an agent's effect stays held until the evidence
   receipt is durable in the session WAL (evidence-before-effect, Janus
   row-1 vocabulary — adopted in doubt-ledger#9).
4. **Pins before merge**: every plugin ships `tools/pin_*.py`, fail-first.
5. **Deterministic replay**: given the session WAL + manifests, the host
   re-derives every effect decision offline.

## The rebuild (first slice, shipped with this charter)

`platform/` in the warp repo: registry + session + one demo plugin
(`quilt_vote` — the warp-vote two-pass ballot in pure python) + CLI +
13 pins. The monolith stays untouched; the platform grows beside it the
same way `nb/` grew beside notebookLM's legacy tree.
