from __future__ import annotations

import dataclasses
import inspect
import json
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

import cfc_anchor
from cfc_anchor import Controller
import cfc_anchor._engine as frozen_engine


def describe(name, obj):
    row = {
        "name": name,
        "type": type(obj).__name__,
        "callable": callable(obj),
        "signature": None,
        "dataclass_fields": None,
        "source": None,
    }
    if callable(obj):
        try:
            row["signature"] = str(inspect.signature(obj))
        except Exception as exc:
            row["signature"] = f"<signature-error:{type(exc).__name__}:{exc}>"
    if dataclasses.is_dataclass(obj):
        row["dataclass_fields"] = [
            {
                "name": f.name,
                "default": (
                    repr(f.default)
                    if f.default is not dataclasses.MISSING
                    else None
                ),
            }
            for f in dataclasses.fields(obj)
        ]
    try:
        row["source"] = inspect.getsource(obj).splitlines()
    except Exception:
        pass
    return row


def main():
    names = sorted(
        name
        for name in dir(cfc_anchor)
        if (
            "DecisionGenericDependencyAccounting" in name
            or "DECISION_GENERIC_DEPENDENCY_ACCOUNTING" in name
        )
    )
    controller_names = sorted(
        name
        for name in dir(Controller)
        if "decision_generic_dependency_accounting" in name.lower()
    )
    controller_module = inspect.getmodule(Controller)
    private_contract = {}
    if controller_module is not None:
        for name in dir(controller_module):
            if (
                "DECISION_GENERIC_DEPENDENCY_ACCOUNTING" in name
                or "DECISION_DEPENDENCY_ACCOUNTING" in name
            ):
                value = getattr(controller_module, name)
                if isinstance(value, (str, int, float, bool, type(None))):
                    private_contract[name] = value
                else:
                    private_contract[name] = repr(value)

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "DECISION_GENERIC_ACCOUNTING_PUBLIC_LIFECYCLE_INTROSPECTION",
        "module_symbols": [
            describe(name, getattr(cfc_anchor, name))
            for name in names
        ],
        "controller_symbols": [
            describe(name, getattr(Controller, name))
            for name in controller_names
        ],
        "controller_private_contract": private_contract,
        "engine_constants": {
            key: repr(getattr(frozen_engine, key))
            for key in dir(frozen_engine)
            if "DECISION_GENERIC_DEPENDENCY_ACCOUNTING" in key
        },
        "non_mutation": True,
    }

    Path("decision_generic_accounting_lifecycle_introspection.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
