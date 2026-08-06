import json
import os
import pygame

MAP_WIDTH = 800
MAP_HEIGHT = 480

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects")


class Placement:
    #one object-layer entry. tileset_name/rect are None for a pure-collision marker with no sprite
    #(e.g. a fight/heal trigger with nothing to look at). collision is a dict matching the game's
    #existing tile-type vocabulary, or None for a purely decorative object.
    def __init__(self, x, y, width, height, tileset_name=None, rect=None, collision=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tileset_name = tileset_name
        self.rect = rect
        self.collision = collision

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "tileset": self.tileset_name, "rect": list(self.rect) if self.rect else None,
            "collision": self.collision,
        }

    @staticmethod
    def from_dict(data):
        return Placement(
            data["x"], data["y"], data["width"], data["height"],
            tileset_name=data.get("tileset"),
            rect=tuple(data["rect"]) if data.get("rect") else None,
            collision=data.get("collision"),
        )


class Project:
    def __init__(self, name):
        self.name = name
        self.ground_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.ground_surface.fill((40, 40, 40))
        self.placements = []

    def project_json_path(self):
        return os.path.join(PROJECTS_DIR, self.name + ".json")

    def ground_png_path(self):
        return os.path.join(PROJECTS_DIR, self.name + "_ground.png")

    def save(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        pygame.image.save(self.ground_surface, self.ground_png_path())
        data = {
            "name": self.name,
            "width": MAP_WIDTH, "height": MAP_HEIGHT,
            "placements": [p.to_dict() for p in self.placements],
        }
        with open(self.project_json_path(), "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def exists(name):
        return os.path.exists(os.path.join(PROJECTS_DIR, name + ".json"))

    @staticmethod
    def load(name):
        project = Project(name)
        with open(project.project_json_path(), "r") as f:
            data = json.load(f)
        if os.path.exists(project.ground_png_path()):
            project.ground_surface = pygame.image.load(project.ground_png_path()).convert()
        project.placements = [Placement.from_dict(d) for d in data["placements"]]
        return project
