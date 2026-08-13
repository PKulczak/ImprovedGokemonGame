import settings


class Camera:
    def __init__(self, viewport_w=settings.VIRTUAL_W, viewport_h=settings.VIRTUAL_H):
        self.x = 0.0
        self.y = 0.0
        self.viewport_w = viewport_w
        self.viewport_h = viewport_h

    def follow(self, target_px, map_px_w, map_px_h):
        tx, ty = target_px
        cx = tx - self.viewport_w / 2
        cy = ty - self.viewport_h / 2
        max_x = max(0, map_px_w - self.viewport_w)
        max_y = max(0, map_px_h - self.viewport_h)
        self.x = min(max(cx, 0), max_x)
        self.y = min(max(cy, 0), max_y)

    def world_to_screen(self, wx, wy):
        return wx - self.x, wy - self.y

    def visible_tile_range(self, map_w_tiles, map_h_tiles):
        start_x = max(0, int(self.x // settings.TILE_SIZE))
        start_y = max(0, int(self.y // settings.TILE_SIZE))
        end_x = min(map_w_tiles, start_x + self.viewport_w // settings.TILE_SIZE + 2)
        end_y = min(map_h_tiles, start_y + self.viewport_h // settings.TILE_SIZE + 2)
        return start_x, start_y, end_x, end_y
