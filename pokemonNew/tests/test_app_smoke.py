import pygame

from engine.app import App
from engine.scene import Scene


class RedScene(Scene):
    def draw(self, surface):
        surface.fill((200, 30, 30))


def test_headless_app_ticks_and_renders(tmp_path):
    app = App(headless=True)
    app.scene_stack.push(RedScene(app))
    for _ in range(5):
        app.tick(1 / 60)
    app.draw()

    out_path = tmp_path / "frame.png"
    pygame.image.save(app.virtual_surface, str(out_path))

    assert out_path.exists()
    surf = pygame.image.load(str(out_path))
    assert surf.get_at((5, 5))[:3] == (200, 30, 30)


def test_app_quit_stops_running_flag():
    app = App(headless=True)
    assert app.running is True
    app.quit()
    assert app.running is False
