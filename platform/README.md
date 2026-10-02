# warp platform — a quilt-plugin agentic host

The rebuild bet: the old monolith tried to be the whole environment. The
platform is the fleet bet instead — **thin host, plugin constellation,
receipts everywhere**. The 14-repo warp constellation (see
[`CONSTELLATION.md`](../CONSTELLATION.md)) maps onto this host as plugin
modules: consensus (warp-vote family), arithmetic (ternary-warp family),
execution (flux, cudaclaw), rooms (warp-room, holodeck-cuda,
room-topology, vessel-navigator), silicon emulation (quilt-silicon).

![the gate: effects wait for evidence](assets/platform-wow.png)

*Open [`docs/demo.html`](docs/demo.html) in a browser — click the ballots
and watch a veto stop an agent from acting, live.*

## What ships here (first slice)

```
platform/
  core.py              Registry + Session. Stdlib only.
  plugins/quilt_vote.py  demo plugin: two-pass ternary ballot (warp=32),
                         ported from warp-vote-consensus's 2-bit encoding
  cli.py               demo session run
receipts/              session WALs (JSONL, append-only)
tools/pin_platform.py  10 FAIL-first pins — 10/10 green
```

## The two laws the host enforces

1. **Load ≠ trust.** Manifests are receipted at load (content hash);
   capability overclaims are *named refusals*, never silent.
2. **Effects wait for evidence — and the gate reads the verdict.**
   A proposal with a vetoed ballot is HELD (`hold_reason: vetoed`).
   A proposal with no evidence is HELD forever. Evidence present is
   necessary, never sufficient. (evidence-before-effect, Janus
   vocabulary — adopted via doubt-ledger#9.)

`Session.verify()` replays the WAL's recorded args through the plugin and
flags any verdict that fails to re-derive — the wal_ref-substitution
defense (post-approval substitution class, same hedge).

## Run it

```sh
python3 platform/cli.py        # demo session: A released, B held, C vetoed
python3 tools/pin_platform.py  # 10/10 pins (P0 is demonstrated RED first)
```

## Honest boundaries (sealed)

- The demo plugin is pure python; no GPU. The 4-cycle hardware claim from
  warp-vote-consensus README is *their* measurement, not re-derived here.
- `verify()` replays in-process; there is no cross-process auditor yet.
- The constellation charter (CONSTELLATION.md) is the target architecture;
  only `quilt_vote` is ported today. Each further port = a manifest +
  capabilities + pins, loaded by this host.
- The legacy monolith tree is untouched; the platform grows beside it.
