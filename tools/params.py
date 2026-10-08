"""A port's parameter list, the input to gen_vst.py and the skin studio.

Generic format (params.json): {"name": "...", "params": [...], "sections": [{"label": "...", "keys": [...]}]}
or just the list. Each param: key, name, and either min/max (+ unit) or options (+ optional "values": the number
each option sends the DSP instead of its index, or "send": the word it sends); optional default,
momentary (a trigger that reports back to 0), display ("string" | "int"), step_of/step_delta, type
(the studio's widget hint: readout, stepper, trigger, slot). The list order is the VST parameter index.

Engines from other ecosystems bring their own parameter files through adapters/ (e.g.
adapters/schwung reads a module.json when vst.json names a "module")."""
import json
import os
import sys

ADAPTERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "adapters")


def load(path):
    """-> (params, sections [(label, [keys])] or None)"""
    d = json.load(open(path))
    if isinstance(d, list):
        return d, None
    if "params" in d:
        secs = [(s["label"], s["keys"]) for s in d.get("sections", [])] or None
        return d["params"], secs
    sys.path.insert(0, os.path.join(ADAPTERS, "schwung"))
    import module_params
    if module_params.is_module(d):
        return module_params.load(path)
    raise SystemExit("%s: no parameter list" % path)


def source(cfg):
    """vst.json -> (params file path relative to it, adapter name or None)

    A "module" names an adapter engine (schwung). Its parameter list normally comes from the module.json, but a port
    may give a hand-made "params" file beside "module" to override it (types, ranges, options and names the
    module.json doesn't carry, e.g. OB-Xd's bare keys). The adapter is linked either way."""
    if cfg.get("module"):
        return cfg.get("params") or cfg["module"], "schwung"
    if cfg.get("params"):
        return cfg["params"], None
    raise SystemExit('vst.json: needs "params" (or an adapter\'s source, e.g. "module")')
