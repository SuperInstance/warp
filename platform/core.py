"""warp platform core — registry + session for a quilt-plugin agentic host.

Design laws (from CONSTELLATION.md):
  1. Manifests are receipted at load (content hash). Load != trust.
  2. Session actions append to a WAL; effects are HELD until their
     evidence receipt is durable (evidence-before-effect).
  3. Verdicts are re-derivable offline from WAL + manifests.
  4. Pure python3 stdlib — the host has no dependencies the plugins
     don't also have.
"""
import hashlib
import json
import time
from pathlib import Path


def h(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"),
                   default=str).encode()).hexdigest()[:16]


class Manifest:
    """A plugin's contract with the host."""

    REQUIRED = ("name", "version", "capabilities")

    def __init__(self, name, version, capabilities, pins_path=None):
        vals = {"name": name, "version": version, "capabilities": capabilities}
        for k in self.REQUIRED:
            if not vals[k]:
                raise ValueError(f"manifest missing {k}")
        self.name, self.version = name, str(version)
        self.capabilities = list(capabilities)
        self.pins_path = pins_path

    def receipt(self):
        return {"manifest": h(vars(self)), "name": self.name,
                "version": self.version,
                "capabilities": sorted(self.capabilities)}


class PluginRefused(Exception):
    """Named refusal — the host never silently ignores a bad plugin."""


class Registry:
    """Loads plugins, receipts manifests, enforces capability contracts."""

    def __init__(self):
        self.plugins = {}          # name -> (manifest, module)
        self.ledger = []           # load receipts

    def load(self, name, module, manifest):
        offered = set(getattr(module, "CAPABILITIES", []))
        if not set(manifest.capabilities) <= offered:
            missing = sorted(set(manifest.capabilities) - offered)
            raise PluginRefused(
                f"plugin {name} claims {missing} but does not offer them")
        required = getattr(module, "REQUIRES", [])
        for cap in manifest.capabilities:
            if cap not in offered:
                raise PluginRefused(f"capability {cap} not offered")
        self.plugins[name] = (manifest, module)
        self.ledger.append({"event": "load", "plugin": name,
                            **manifest.receipt()})
        return manifest.receipt()

    def call(self, plugin, capability, **kwargs):
        if plugin not in self.plugins:
            raise PluginRefused(f"plugin {plugin} not loaded")
        manifest, module = self.plugins[plugin]
        if capability not in manifest.capabilities:
            raise PluginRefused(
                f"{plugin} has no contract for {capability} "
                f"(offers {sorted(manifest.capabilities)})")
        fn = getattr(module, "CAP_IMPL", {}).get(capability)
        if fn is None:
            raise PluginRefused(f"{plugin}.{capability} has no implementation")
        out = fn(**kwargs)
        self.ledger.append({"event": "call", "plugin": plugin,
                            "capability": capability,
                            "args": kwargs, "args_hash": h(kwargs),
                            "result_hash": h(out)})
        return out


class Session:
    """Agent session: proposals gated on durable evidence receipts."""

    def __init__(self, registry, wal_path):
        self.reg = registry
        self.wal = Path(wal_path)
        self.wal.parent.mkdir(parents=True, exist_ok=True)
        self.held = []             # effects waiting for evidence

    def _append(self, row):
        with self.wal.open("a") as f:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    def propose(self, agent, effect, evidence_call=None):
        """Effect is HELD unless/until evidence is durable in the WAL.

        evidence_call = (plugin, capability, kwargs). Without it the effect
        stays held forever — the Janus gate, in our vocabulary.
        """
        row = {"ts": time.time(), "agent": agent, "effect": effect,
               "state": "held", "evidence": None}
        if evidence_call:
            plugin, cap, kw = evidence_call
            verdict = self.reg.call(plugin, cap, **kw)
            ev = {"plugin": plugin, "capability": cap,
                  "args": kw, "verdict_hash": h(verdict)}
            row["evidence"] = ev
            # The gate reads the VERDICT, not the receipt's existence:
            # a vetoed or quorum-less ballot holds the effect. Evidence
            # durable is necessary, never sufficient.
            v = verdict.get("verdict") if isinstance(verdict, dict) else None
            if v == "passed":
                row["state"] = "released"
            elif v is not None:
                row["state"] = "held"
                row["hold_reason"] = v
            else:
                row["state"] = "released"  # non-verdict evidence: presence rule
        self._append(row)
        if row["state"] != "released":
            self.held.append(row)
        return row

    def verify(self):
        """Offline re-derivation: replay WAL, recompute every verdict hash."""
        rows = [json.loads(l) for l in self.wal.read_text().splitlines()
                if l.strip()]
        ok, bad = 0, []
        for i, r in enumerate(rows):
            ev = r.get("evidence")
            if ev:
                out = self.reg.call(ev["plugin"], ev["capability"],
                                    **ev.get("args", {}))
                if h(out) == ev["verdict_hash"]:
                    ok += 1
                else:
                    bad.append(i)   # substitution caught: row i's verdict
                                    # does not re-derive from its evidence
        return {"rows": len(rows), "gated": ok, "mismatched_rows": bad,
                "held_open": sum(1 for r in rows if r.get("state") == "held")}
