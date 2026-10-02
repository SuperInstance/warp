"""CLI for the warp platform core: demo session run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402
import plugins.quilt_vote as quilt_vote  # noqa: E402


def main():
    reg = core.Registry()
    m = core.Manifest("quilt_vote", "0.1.0",
                      ["vote.ballot", "vote.tally"], "tools/pin_platform.py")
    rcpt = reg.load("quilt_vote", quilt_vote, m)
    print("loaded:", rcpt)

    wal = "receipts/session-demo.jsonl"
    Path(wal).unlink(missing_ok=True)
    s = core.Session(reg, wal)

    # Agent A proposes an effect with evidence: 20 agree / 5 reject / 7 abstain
    r1 = s.propose("agent-a", "write:platform/README.md",
                   evidence_call=("quilt_vote", "vote.tally",
                                  {"votes": ["agree"] * 20 + ["reject"] * 5
                                   + ["abstain"] * 7}))
    print("A:", r1["state"], r1["evidence"]["verdict_hash"])

    # Agent B proposes with no evidence — must stay held forever
    r2 = s.propose("agent-b", "push:main")
    print("B:", r2["state"], "(held — no evidence, no release)")

    # Agent C proposes with a vetoed ballot — released? No: veto holds it.
    r3 = s.propose("agent-c", "delete:platform/",
                   evidence_call=("quilt_vote", "vote.tally",
                                  {"votes": ["reject"] * 20 + ["agree"] * 10
                                   + ["abstain"] * 2}))
    print("C:", r3["state"], r3.get("hold_reason", ""), "(vetoed ballot holds the effect — the gate reads the verdict)")

    print("verify:", s.verify())
    print("registry ledger:", len(reg.ledger), "events")


if __name__ == "__main__":
    main()
