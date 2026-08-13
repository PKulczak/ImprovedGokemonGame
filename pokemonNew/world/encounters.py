"""Wild encounter rolling. Takes an injected random.Random so tests can force
deterministic outcomes instead of being flaky."""

import json
import os

from engine.assets import DATA_DIR

_TABLES_CACHE = None


def _load_tables(path=None):
    global _TABLES_CACHE
    if path is None:
        if _TABLES_CACHE is not None:
            return _TABLES_CACHE
        path = os.path.join(DATA_DIR, "encounter_tables.json")
    with open(path) as f:
        tables = json.load(f)
    if path == os.path.join(DATA_DIR, "encounter_tables.json"):
        _TABLES_CACHE = tables
    return tables


def roll_encounter(table_id, rng, base_chance=0.1, tables=None):
    """Returns {"species": name, "level": n} or None."""
    if rng.random() >= base_chance:
        return None
    tables = tables if tables is not None else _load_tables()
    table = tables.get(table_id)
    if not table or not table.get("entries"):
        return None
    entries = table["entries"]
    weights = [e["weight"] for e in entries]
    choice = rng.choices(entries, weights=weights, k=1)[0]
    level = rng.randint(choice["min_level"], choice["max_level"])
    return {"species": choice["species"], "level": level}
