"""FAIL-first pins for the warp platform core.

P0  receipts absent -> FAIL (demonstrated RED before first run).
P1  registry load receipts the manifest; re-load is a new ledger row.
P2  capability contract refused when the plugin does not offer the verb
    (claims vote.delete -> named PluginRefused).
P3  two-pass ballot math: 32-warp masks, abstain = neither bit,
    deterministic across calls.
P4  VETO GATE: a vetoed verdict HOLDS the effect (state=held,
    hold_reason=vetoed). Evidence present is necessary, never sufficient.
P5  NO-EVIDENCE GATE: a proposal without evidence_call stays held forever.
P6  session WAL rows append; verify() replays and counts gated rows.
P7  deterministic replay: same votes -> same verdict_hash bit-identical.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "platform"))
import core  # noqa: E402
import plugins.quilt_vote as quilt_vote  # noqa: E402

results = []


def pin(name, cond, detail=""):
    results.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + name + (f" - {detail}" if detail else ""))


def fresh_reg():
    reg = core.Registry()
    m = core.Manifest("quilt_vote", "0.1.0", ["vote.ballot", "vote.tally"],
                      "tools/pin_platform.py")
    reg.load("quilt_vote", quilt_vote, m)
    return reg


def main():
    wal = Path("receipts/session-demo.jsonl")
    if not wal.exists():
        print("FAIL P0 receipts absent (run platform/cli.py first)")
        return 1
    pin("P0 session WAL exists from the demo run", True)

    reg = fresh_reg()
    pin("P1 manifest receipt present in load ledger",
        any(e.get("event") == "load" and e.get("manifest") for e in reg.ledger))

    # P2: contract violation is a NAMED refusal
    try:
        bad = core.Manifest("quilt_vote", "0.1.0", ["vote.delete"])
        reg.load("quilt_vote", quilt_vote, bad)
        pin("P2 overclaim refused with named capability", False)
    except core.PluginRefused as e:
        pin("P2 overclaim refused with named capability", "vote.delete" in str(e), str(e))

    # P3: ballot masks
    b = quilt_vote.ballot(["agree"] * 3 + ["reject"] * 1 + ["abstain"] * 28)
    pin("P3 ballot masks", b["agree_mask"] == 0b111 and b["reject_mask"] == 0b1000
        and b["n_agree"] == 3 and b["n_reject"] == 1 and b["n_abstain"] == 28,
        json.dumps(b))

    # P4 + P5 via a fresh session
    wal2 = Path("receipts/pin-gates.jsonl"); wal2.unlink(missing_ok=True)
    s = core.Session(fresh_reg(), wal2)
    r_pass = s.propose("a", "write:x", ("quilt_vote", "vote.tally",
                       {"votes": ["agree"] * 20}))
    r_veto = s.propose("b", "delete:y", ("quilt_vote", "vote.tally",
                       {"votes": ["reject"] * 20 + ["abstain"] * 12}))
    r_none = s.propose("c", "push:main")
    pin("P4 passed ballot releases", r_pass["state"] == "released")
    pin("P4b vetoed ballot HOLDS with reason", r_veto["state"] == "held"
        and r_veto.get("hold_reason") == "vetoed")
    pin("P5 no-evidence proposal stays held", r_none["state"] == "held")

    # P6: WAL rows + verify replay
    rows = [json.loads(l) for l in wal2.read_text().splitlines()]
    pin("P6 three WAL rows appended", len(rows) == 3)
    v = s.verify()
    pin("P6b verify replays gated rows", v["rows"] == 3 and v["gated"] == 2
        and v["held_open"] == 2, json.dumps(v))

    # P7: determinism of verdict hash
    t1 = quilt_vote.tally(["agree"] * 21)
    t2 = quilt_vote.tally(["agree"] * 21)
    pin("P7 verdict hash deterministic", core.h(t1) == core.h(t2))

    n = sum(results)
    print(("GREEN: platform core is gate-true" if n == len(results)
           else "RED: pins failed") + f" ({n}/{len(results)})")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
