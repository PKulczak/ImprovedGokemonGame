"""Plain-JSON save/load, fully isolated from the old repo's game/Fight/Files/*.json.
Pure stdlib, zero pygame dependency."""

import json
import os

from save.schema import SaveData


class SaveManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def _path(self, slot):
        return os.path.join(self.save_dir, f"slot_{slot}.json")

    def save(self, save_data, slot=1):
        with open(self._path(slot), "w") as f:
            json.dump(save_data.to_dict(), f, indent=2)

    def load(self, slot=1):
        path = self._path(slot)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            data = json.load(f)
        return SaveData.from_dict(data)

    def has_save(self, slot=1):
        return os.path.exists(self._path(slot))

    def delete(self, slot=1):
        path = self._path(slot)
        if os.path.exists(path):
            os.remove(path)
