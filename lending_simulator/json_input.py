"""Bounded, exact JSON intake for local scenario and manifest files."""

import json
from decimal import Decimal
from pathlib import Path
from typing import cast

MAX_ASSUMPTIONS_BYTES = 1_000_000
MAX_JSON_DEPTH = 128


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Assumptions JSON contains a duplicate key.")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Assumptions JSON cannot contain non-finite numeric tokens.")


def load_assumptions_document(path: Path) -> dict[str, object]:
    with path.open("rb") as source:
        content = source.read(MAX_ASSUMPTIONS_BYTES + 1)
    if len(content) > MAX_ASSUMPTIONS_BYTES:
        raise ValueError("Assumptions JSON exceeds the 1,000,000-byte limit.")
    try:
        value: object = json.loads(
            content.decode("utf-8"), parse_float=Decimal,
            parse_constant=_reject_constant, object_pairs_hook=_object,
        )
    except RecursionError as error:
        raise ValueError("Assumptions JSON is nested too deeply.") from error
    if not isinstance(value, dict):
        raise ValueError("Assumptions JSON must contain an object.")
    pending: list[tuple[object, int]] = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if isinstance(item, (dict, list)):
            if depth > MAX_JSON_DEPTH:
                raise ValueError("Assumptions JSON exceeds the nesting limit.")
            children = item.values() if isinstance(item, dict) else item
            pending.extend((child, depth + 1) for child in children)
    return cast(dict[str, object], value)
