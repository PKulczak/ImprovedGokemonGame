import json
import os

from engine.scene import Scene
from engine.assets import DATA_DIR


class BootScene(Scene):
    """Loads static text content, then hands off to the title screen."""

    def on_enter(self, **kwargs):
        self.app.dialogue_text = self._load_dialogue_text()
        from scenes.title import TitleScene
        self.app.scene_stack.replace(TitleScene(self.app))

    def _load_dialogue_text(self):
        directory = os.path.join(DATA_DIR, "dialogue_text")
        merged = {}
        if os.path.isdir(directory):
            for fname in sorted(os.listdir(directory)):
                if fname.endswith(".json"):
                    with open(os.path.join(directory, fname), encoding="utf-8") as f:
                        merged.update(json.load(f))
        return merged

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
