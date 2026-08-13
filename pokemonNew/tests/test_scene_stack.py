from engine.scene import Scene, SceneStack


class RecordingScene(Scene):
    def __init__(self, app, name, log):
        super().__init__(app)
        self.name = name
        self.log = log

    def on_enter(self, **kwargs):
        self.log.append(f"enter:{self.name}")

    def on_exit(self):
        self.log.append(f"exit:{self.name}")

    def on_child_closed(self, result):
        self.log.append(f"child_closed:{self.name}:{result}")

    def update(self, dt):
        self.log.append(f"update:{self.name}")


def test_push_pop_basic():
    log = []
    stack = SceneStack()
    a = RecordingScene(None, "a", log)
    b = RecordingScene(None, "b", log)
    stack.push(a)
    stack.push(b)
    assert stack.top is b
    stack.pop(result="done")
    assert stack.top is a
    assert log == ["enter:a", "enter:b", "exit:b", "child_closed:a:done"]


def test_replace_swaps_top():
    log = []
    stack = SceneStack()
    a = RecordingScene(None, "a", log)
    b = RecordingScene(None, "b", log)
    stack.push(a)
    stack.replace(b)
    assert stack.top is b
    assert len(stack) == 1
    assert log == ["enter:a", "exit:a", "enter:b"]


def test_update_stops_at_blocking_scene():
    log = []
    stack = SceneStack()
    a = RecordingScene(None, "a", log)
    b = RecordingScene(None, "b", log)
    b.blocks_update_below = True
    stack.push(a)
    stack.push(b)
    log.clear()
    stack.update(0.016)
    assert log == ["update:b"]


def test_update_passes_through_overlay():
    log = []
    stack = SceneStack()
    a = RecordingScene(None, "a", log)
    b = RecordingScene(None, "b", log)
    b.blocks_update_below = False
    stack.push(a)
    stack.push(b)
    log.clear()
    stack.update(0.016)
    assert log == ["update:b", "update:a"]


def test_draw_overlay_draws_scene_below_first():
    order = []
    stack = SceneStack()

    class Drawn(Scene):
        def __init__(self, app, name, draws_below=False):
            super().__init__(app)
            self.name = name
            self.draws_below = draws_below

        def draw(self, surface):
            order.append(self.name)

    base = Drawn(None, "overworld", draws_below=False)
    overlay = Drawn(None, "dialogue", draws_below=True)
    stack.push(base)
    stack.push(overlay)
    stack.draw(surface=None)
    assert order == ["overworld", "dialogue"]


def test_draw_replace_only_draws_top_when_not_overlay():
    order = []
    stack = SceneStack()

    class Drawn(Scene):
        def __init__(self, app, name):
            super().__init__(app)
            self.name = name

        def draw(self, surface):
            order.append(self.name)

    a = Drawn(None, "title")
    b = Drawn(None, "overworld")
    stack.push(a)
    stack.replace(b)
    stack.draw(surface=None)
    assert order == ["overworld"]
