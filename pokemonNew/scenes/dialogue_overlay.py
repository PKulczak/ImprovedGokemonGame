from engine.scene import Scene
from engine.dialogue import DialogueBox


class DialogueScene(Scene):
    blocks_update_below = True
    draws_below = True

    def on_enter(self, pages=None, **kwargs):
        self.box = DialogueBox(self.app.assets)
        self.box.start(pages or [])

    def handle_input(self, input_state):
        if input_state.was_pressed("CONFIRM"):
            done = self.box.advance()
            if done:
                self.app.scene_stack.pop()

    def update(self, dt):
        self.box.update(dt)

    def draw(self, surface):
        self.box.draw(surface)
