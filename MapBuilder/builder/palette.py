from .tileset import Tileset


class PaletteEntry:
    #tileset_name + rect is the source of truth (small, serializable); surface is a cached crop
    def __init__(self, tileset_name, rect, surface):
        self.tileset_name = tileset_name
        self.rect = rect  # (x, y, w, h) within the source tileset sheet
        self.surface = surface

    @property
    def width(self):
        return self.rect[2]

    @property
    def height(self):
        return self.rect[3]

    def to_dict(self):
        return {"tileset": self.tileset_name, "rect": list(self.rect)}

    @staticmethod
    def from_dict(data, tileset_cache):
        name = data["tileset"]
        if name not in tileset_cache:
            tileset_cache[name] = Tileset(name)
        surface = tileset_cache[name].crop(tuple(data["rect"]))
        return PaletteEntry(name, tuple(data["rect"]), surface)


class Palette:
    def __init__(self):
        self.entries = []

    def add(self, tileset_name, rect, surface):
        entry = PaletteEntry(tileset_name, rect, surface)
        self.entries.append(entry)
        return entry

    def remove(self, entry):
        if entry in self.entries:
            self.entries.remove(entry)
