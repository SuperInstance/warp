"""quilt_vote — demo plugin: warp-vote two-pass ternary ballot, pure python.

Ports the warp-vote-consensus encoding (2 bits: Reject 0b00, Abstain 0b01,
Agree 0b10) and its two-pass ballot collection to a deterministic,
GPU-free host. 32 voters per ballot = one warp. Deterministic given votes;
no wall clock, no randomness.
"""

CAPABILITIES = ["vote.ballot", "vote.tally"]
REQUIRES = []


def _encode(v):
    return {"reject": 0b00, "abstain": 0b01, "agree": 0b10}[v]


def ballot(votes):
    """Two-pass ballot: pass 1 agrees, pass 2 rejects; abstain = neither.

    votes: list of "agree"|"abstain"|"reject", any length (pads to warp=32
    with abstain when fewer — a partial warp still ballots).
    """
    vs = list(votes)[:32]
    vs += ["abstain"] * (32 - len(vs))
    agree_mask, reject_mask = 0, 0
    for i, v in enumerate(vs):
        code = _encode(v)
        if code == 0b10:
            agree_mask |= (1 << i)
        elif code == 0b00:
            reject_mask |= (1 << i)
    return {"agree_mask": agree_mask, "reject_mask": reject_mask,
            "n_agree": bin(agree_mask).count("1"),
            "n_reject": bin(reject_mask).count("1"),
            "n_abstain": 32 - bin(agree_mask | reject_mask).count("1"),
            "warp": 32}


def tally(votes, quorum_agree=17, quorum_reject=16):
    """Verdict from the ballot. Defaults: >half agree passes; >=half reject
    vetoes (reject wins ties against release — release is the effectful
    path, so the burden sits on release)."""
    b = ballot(votes)
    if b["n_reject"] >= quorum_reject:
        verdict = "vetoed"
    elif b["n_agree"] >= quorum_agree:
        verdict = "passed"
    else:
        verdict = "no_quorum"
    return {**b, "verdict": verdict,
            "rule": f"pass if agree>={quorum_agree} and reject<{quorum_reject}"}


CAP_IMPL = {"vote.ballot": ballot, "vote.tally": tally}
