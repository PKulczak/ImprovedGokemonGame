"""Scene base class + SceneStack: the application's only state-management mechanism."""


class Scene:
    """Base class for every screen/overlay in the game.

    blocks_update_below: when True (default), scenes below this one on the
        stack are not updated while this one is on top.
    draws_below: when True, the scene(s) below this one are drawn first, so
        this scene renders as an overlay (e.g. a dialogue box over the map)
        rather than a full-screen replacement.
    """

    blocks_update_below = True
    draws_below = False

    def __init__(self, app):
        self.app = app

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def on_child_closed(self, result):
        """Called on the new top scene right after a scene it pushed is popped."""
        pass

    def handle_input(self, input_state):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class SceneStack:
    def __init__(self):
        self._stack = []

    @property
    def top(self):
        return self._stack[-1] if self._stack else None

    def __len__(self):
        return len(self._stack)

    def push(self, scene, **kwargs):
        # Append BEFORE on_enter: on_enter is allowed to itself mutate the
        # stack (e.g. BootScene immediately replace()-ing itself with
        # TitleScene), and that only targets the right scene if this one is
        # already on the stack when it runs.
        self._stack.append(scene)
        scene.on_enter(**kwargs)

    def pop(self, result=None):
        if not self._stack:
            return
        scene = self._stack.pop()
        scene.on_exit()
        if self._stack:
            self._stack[-1].on_child_closed(result)

    def replace(self, scene, **kwargs):
        if self._stack:
            old = self._stack.pop()
            old.on_exit()
        self._stack.append(scene)
        scene.on_enter(**kwargs)

    def handle_input(self, input_state):
        top = self.top
        if top is not None:
            top.handle_input(input_state)

    def update(self, dt):
        for scene in reversed(self._stack):
            scene.update(dt)
            if scene.blocks_update_below:
                break

    def draw(self, surface):
        if not self._stack:
            return
        lowest = len(self._stack) - 1
        while lowest > 0 and self._stack[lowest].draws_below:
            lowest -= 1
        for scene in self._stack[lowest:]:
            scene.draw(surface)
