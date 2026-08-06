import sys
import pygame

from .project import Project, Placement, MAP_WIDTH, MAP_HEIGHT
from .export import export_project
from .tileset import Tileset, list_tilesets

WINDOW_SIZE = (1280, 760)

CANVAS_RECT = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
BOTTOM_BAR_RECT = pygame.Rect(0, MAP_HEIGHT, MAP_WIDTH, WINDOW_SIZE[1] - MAP_HEIGHT)
TILESET_PANEL_RECT = pygame.Rect(MAP_WIDTH, 0, WINDOW_SIZE[0] - MAP_WIDTH, 500)
PALETTE_PANEL_RECT = pygame.Rect(MAP_WIDTH, 500, WINDOW_SIZE[0] - MAP_WIDTH, WINDOW_SIZE[1] - 500)

TAB_BAR_HEIGHT = 26
#one clickable tab per tileset, above the sheet viewer - lets you switch sheets without
#hunting for the [ ] hotkeys, which matters more now there's more than one tileset to pick from
TILESET_TABS_RECT = pygame.Rect(TILESET_PANEL_RECT.x, TILESET_PANEL_RECT.y, TILESET_PANEL_RECT.width, TAB_BAR_HEIGHT)
TILESET_VIEW_RECT = pygame.Rect(TILESET_PANEL_RECT.x, TILESET_PANEL_RECT.y + TAB_BAR_HEIGHT,
                                 TILESET_PANEL_RECT.width, TILESET_PANEL_RECT.height - TAB_BAR_HEIGHT)

PALETTE_CELL = 52
GRID_SIZE = 32

#collision brush hotkeys - matches the type vocabulary gokemon_game.py already understands
BRUSH_KEYS = {
    pygame.K_0: None,
    pygame.K_1: "tree",
    pygame.K_2: "wall_up_a",
    pygame.K_3: "wall_up_b",
    pygame.K_4: "wall_left_a",
    pygame.K_5: "wall_left_b",
    pygame.K_6: "fight",
    pygame.K_7: "heal",
    pygame.K_8: "interact",
    pygame.K_9: "boss_gate",
    pygame.K_n: "npc",
    pygame.K_y: "yacht",
}
#types that resolve their real sprite through the game's existing per-map NPC lookup -
#never attach a decorative stamp to these, or it'd double up with the game's own NPC sprite
NO_SPRITE_TYPES = ("npc", "yacht")
#types that need extra typed-in fields once placed
TARGET_TYPES = ("interact", "boss_gate")

#ordered (hotkey, brush) legend - also drives the color each collision box is drawn with, so it's
#easy to tell walls/interactions/triggers apart at a glance while building
BRUSH_LEGEND = [
    ("0", None), ("1", "tree"), ("2", "wall_up_a"), ("3", "wall_up_b"),
    ("4", "wall_left_a"), ("5", "wall_left_b"), ("6", "fight"), ("7", "heal"),
    ("8", "interact"), ("9", "boss_gate"), ("n", "npc"), ("y", "yacht"),
]
COLLISION_COLORS = {
    None: (120, 120, 255),
    "tree": (0, 220, 0),
    "wall_up_a": (220, 0, 0),
    "wall_up_b": (255, 140, 0),
    "wall_left_a": (255, 0, 255),
    "wall_left_b": (0, 200, 255),
    "fight": (255, 255, 0),
    "heal": (255, 255, 255),
    "interact": (0, 120, 255),
    "boss_gate": (170, 0, 255),
    "npc": (255, 105, 180),
    "yacht": (139, 90, 43),
}


def prompt_text(screen, label, default=""):
    font = pygame.font.SysFont(None, 28)
    text = default
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text += event.unicode
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render(label, True, (255, 255, 255)), (40, 40))
        screen.blit(font.render(text + "_", True, (255, 255, 0)), (40, 80))
        screen.blit(font.render("Enter to confirm, Esc to cancel", True, (200, 200, 200)), (40, 130))
        pygame.display.flip()
        clock.tick(30)


class PaletteEntry:
    def __init__(self, tileset_name, rect, surface):
        self.tileset_name = tileset_name
        self.rect = rect
        self.surface = surface


class MapBuilderApp:
    def __init__(self, project_name):
        pygame.init()
        pygame.display.set_caption("Gokemon Map Builder - {}".format(project_name))
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.font = pygame.font.SysFont(None, 22)
        self.clock = pygame.time.Clock()

        if Project.exists(project_name):
            self.project = Project.load(project_name)
        else:
            self.project = Project(project_name)

        self.tileset_names = list_tilesets()
        self.tileset_index = 0
        self.tileset = Tileset(self.tileset_names[self.tileset_index])
        self.tileset_scroll_y = 0

        self.palette = []
        self.active_stamp = None  # PaletteEntry or None
        self.active_brush = None  # collision type string or None

        self.layer = "object"  # "object" or "ground"
        self.snap_to_grid = True

        self.drag_start = None  # tileset rectangle-select in progress
        self.painting = False  # left button held over the canvas
        self.erasing = False  # right button held over the canvas
        self.last_paint_key = None  # last cell/spacing-bucket painted this drag, to avoid overlap
        self.last_erase_key = None
        self.running = True

    #------------------------------------------------------------------ main loop
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    #------------------------------------------------------------------ events
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mousedown(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouseup(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mousemotion(event)
        elif event.type == pygame.MOUSEWHEEL:
            self.handle_wheel(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_TAB:
            self.layer = "ground" if self.layer == "object" else "object"
        elif event.key == pygame.K_g:
            self.snap_to_grid = not self.snap_to_grid
        elif event.key == pygame.K_LEFTBRACKET:
            self.switch_tileset(-1)
        elif event.key == pygame.K_RIGHTBRACKET:
            self.switch_tileset(1)
        elif event.key == pygame.K_F5 or (event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL)):
            self.project.save()
        elif event.key == pygame.K_F9:
            self.project.save()
            out_dir = export_project(self.project)
            print("Exported to", out_dir)
        elif event.key in BRUSH_KEYS:
            self.active_brush = BRUSH_KEYS[event.key]

    def handle_mousedown(self, event):
        if event.button == 1:
            if TILESET_TABS_RECT.collidepoint(event.pos):
                self.click_tileset_tab(event.pos)
            elif TILESET_VIEW_RECT.collidepoint(event.pos):
                self.drag_start = event.pos
            elif PALETTE_PANEL_RECT.collidepoint(event.pos):
                self.click_palette(event.pos)
            elif CANVAS_RECT.collidepoint(event.pos):
                self.painting = True
                self.last_paint_key = None
                self._continue_paint(event.pos)
        elif event.button == 3:
            if CANVAS_RECT.collidepoint(event.pos):
                self.erasing = True
                self.last_erase_key = None
                self._continue_erase(event.pos)

    def handle_mouseup(self, event):
        if event.button == 1:
            if self.drag_start is not None and TILESET_VIEW_RECT.collidepoint(event.pos):
                self.finish_tileset_selection(self.drag_start, event.pos)
            self.drag_start = None
            self.painting = False
        elif event.button == 3:
            self.erasing = False

    def handle_mousemotion(self, event):
        if self.painting and CANVAS_RECT.collidepoint(event.pos):
            self._continue_paint(event.pos)
        if self.erasing and CANVAS_RECT.collidepoint(event.pos):
            self._continue_erase(event.pos)

    def handle_wheel(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if TILESET_VIEW_RECT.collidepoint(mouse_pos):
            max_scroll = max(0, self.tileset.height - TILESET_VIEW_RECT.height)
            self.tileset_scroll_y = max(0, min(max_scroll, self.tileset_scroll_y - event.y * 40))

    #------------------------------------------------------------------ actions
    def switch_tileset(self, direction):
        self._select_tileset((self.tileset_index + direction) % len(self.tileset_names))

    def click_tileset_tab(self, pos):
        tab_width = TILESET_TABS_RECT.width / max(1, len(self.tileset_names))
        index = int((pos[0] - TILESET_TABS_RECT.x) // tab_width)
        self._select_tileset(index)

    def _select_tileset(self, index):
        if 0 <= index < len(self.tileset_names):
            self.tileset_index = index
            self.tileset = Tileset(self.tileset_names[self.tileset_index])
            self.tileset_scroll_y = 0

    def finish_tileset_selection(self, start, end):
        x0 = min(start[0], end[0]) - TILESET_VIEW_RECT.x
        x1 = max(start[0], end[0]) - TILESET_VIEW_RECT.x
        y0 = min(start[1], end[1]) - TILESET_VIEW_RECT.y + self.tileset_scroll_y
        y1 = max(start[1], end[1]) - TILESET_VIEW_RECT.y + self.tileset_scroll_y
        x0 = max(0, min(self.tileset.width, x0))
        x1 = max(0, min(self.tileset.width, x1))
        y0 = max(0, min(self.tileset.height, y0))
        y1 = max(0, min(self.tileset.height, y1))
        w, h = x1 - x0, y1 - y0
        if w < 2 or h < 2:
            return  # treat as a click, not a real selection
        rect = (x0, y0, w, h)
        surface = self.tileset.crop(rect)
        entry = PaletteEntry(self.tileset.filename, rect, surface)
        self.palette.append(entry)
        self.active_stamp = entry

    def click_palette(self, pos):
        col = (pos[0] - PALETTE_PANEL_RECT.x) // PALETTE_CELL
        row = (pos[1] - PALETTE_PANEL_RECT.y) // PALETTE_CELL
        cols = max(1, PALETTE_PANEL_RECT.width // PALETTE_CELL)
        index = int(row) * cols + int(col)
        if 0 <= index < len(self.palette):
            self.active_stamp = self.palette[index]

    def canvas_pos(self, screen_pos):
        return screen_pos[0] - CANVAS_RECT.x, screen_pos[1] - CANVAS_RECT.y

    #the width/height that would be used if something were stamped/placed right now. The
    #no-sprite override only matters for object-layer collision markers (npc/yacht) - on the
    #ground layer the active brush is irrelevant, so it's ignored there.
    def _pending_size(self):
        suppress_sprite = self.layer == "object" and self.active_brush in NO_SPRITE_TYPES
        if self.active_stamp is not None and not suppress_sprite:
            return self.active_stamp.surface.get_size()
        return GRID_SIZE, GRID_SIZE

    #spacing to use along one axis: always the object's own size, never a fixed 32 - flooring
    #this at 32 (an earlier attempt) fixed overlap for objects bigger than a tile but left visible
    #gaps for anything smaller, since a 16px-tall object would still get pushed 32px apart
    def _grid_unit(self, dim):
        return max(1, dim)

    #snaps a center position to the grid, using the per-axis unit above - shared by ground and
    #object placement so both layers snap the same way
    def _snap_position(self, x, y, width, height):
        unit_x, unit_y = self._grid_unit(width), self._grid_unit(height)
        return (x // unit_x) * unit_x + unit_x // 2, (y // unit_y) * unit_y + unit_y // 2

    #buckets (x,y) into cells sized to whatever's about to be stamped there, so repeated calls
    #while dragging land in adjacent cells instead of piling up in the same spot - this is the
    #same regardless of grid-snap, which only affects whether the final position also gets rounded
    def _paint_key(self, x, y):
        width, height = self._pending_size()
        unit_x, unit_y = self._grid_unit(width), self._grid_unit(height)
        return (x // unit_x, y // unit_y)

    #called on mouse-down and every mouse-motion while the button stays held, so holding and
    #dragging lays down a non-overlapping run of stamps instead of one-at-a-time clicking
    def _continue_paint(self, screen_pos):
        if self.layer == "object" and self.active_brush in TARGET_TYPES and self.last_paint_key is not None:
            return  # interact/boss_gate need their own typed-in target - one per click, not per drag
        x, y = self.canvas_pos(screen_pos)
        key = self._paint_key(x, y)
        if key == self.last_paint_key:
            return
        self.last_paint_key = key
        self.paint_at(screen_pos)

    def _continue_erase(self, screen_pos):
        x, y = self.canvas_pos(screen_pos)
        key = self._paint_key(x, y)
        if key == self.last_erase_key:
            return
        self.last_erase_key = key
        self.erase_at(screen_pos)

    def paint_at(self, screen_pos):
        x, y = self.canvas_pos(screen_pos)
        if self.layer == "ground":
            if self.active_stamp is not None:
                w, h = self.active_stamp.surface.get_size()
                if self.snap_to_grid:
                    x, y = self._snap_position(x, y, w, h)
                self.project.ground_surface.blit(self.active_stamp.surface, (x - w // 2, y - h // 2))
        else:
            self.place_object(x, y)

    def place_object(self, x, y):
        width, height = self._pending_size()
        if self.snap_to_grid:
            x, y = self._snap_position(x, y, width, height)

        use_sprite = self.active_stamp is not None and self.active_brush not in NO_SPRITE_TYPES
        if use_sprite:
            tileset_name, rect = self.active_stamp.tileset_name, self.active_stamp.rect
        else:
            tileset_name, rect = None, None

        collision = None
        if self.active_brush is not None:
            collision = {"type": self.active_brush}
            if self.active_brush in TARGET_TYPES:
                fields = prompt_text(self.screen, "target_map,x,y" +
                                      (",requires_defeated" if self.active_brush == "boss_gate" else ""))
                if fields is None:
                    return
                parts = [p.strip() for p in fields.split(",")]
                try:
                    collision["target_map"] = parts[0]
                    collision["target_pos"] = [int(parts[1]), int(parts[2])]
                    if self.active_brush == "boss_gate":
                        collision["requires_defeated"] = parts[3]
                except (IndexError, ValueError):
                    print("Invalid input for {} - placement cancelled".format(self.active_brush))
                    return

        self.project.placements.append(
            Placement(x, y, width, height, tileset_name=tileset_name, rect=rect, collision=collision))

    def erase_at(self, screen_pos):
        x, y = self.canvas_pos(screen_pos)
        if self.layer == "ground":
            if self.snap_to_grid:
                x, y = self._snap_position(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.project.ground_surface, (40, 40, 40), (x - 16, y - 16, 32, 32))
            return
        for placement in reversed(self.project.placements):
            left = placement.x - placement.width / 2
            right = placement.x + placement.width / 2
            top = placement.y - placement.height / 2
            bottom = placement.y + placement.height / 2
            if left <= x <= right and top <= y <= bottom:
                self.project.placements.remove(placement)
                return

    #------------------------------------------------------------------ drawing
    def draw(self):
        self.screen.fill((30, 30, 30))
        self.draw_canvas()
        self.draw_tileset_panel()
        self.draw_palette_panel()
        self.draw_bottom_bar()
        pygame.display.flip()

    def draw_canvas(self):
        self.screen.blit(self.project.ground_surface, CANVAS_RECT.topleft)
        for placement in self.project.placements:
            if placement.tileset_name is not None:
                surface = Tileset(placement.tileset_name).crop(placement.rect) \
                    if placement.tileset_name != self.tileset.filename else self.tileset.crop(placement.rect)
                self.screen.blit(surface, (CANVAS_RECT.x + placement.x - placement.width / 2,
                                            CANVAS_RECT.y + placement.y - placement.height / 2))
            ttype = placement.collision["type"] if placement.collision else None
            box_color = COLLISION_COLORS.get(ttype, COLLISION_COLORS[None])
            rect = pygame.Rect(0, 0, placement.width, placement.height)
            rect.center = (CANVAS_RECT.x + placement.x, CANVAS_RECT.y + placement.y)
            pygame.draw.rect(self.screen, box_color, rect, 1)
        pygame.draw.rect(self.screen, (255, 255, 255), CANVAS_RECT, 1)

    def draw_tileset_panel(self):
        pygame.draw.rect(self.screen, (50, 50, 50), TILESET_PANEL_RECT)
        self.draw_tileset_tabs()

        view = pygame.Surface((TILESET_VIEW_RECT.width, TILESET_VIEW_RECT.height))
        view.fill((50, 50, 50))
        view.blit(self.tileset.surface, (0, -self.tileset_scroll_y))
        self.screen.blit(view, TILESET_VIEW_RECT.topleft)
        label = "{} ({}/{})".format(self.tileset.filename, self.tileset_index + 1, len(self.tileset_names))
        self.screen.blit(self.font.render(label, True, (255, 255, 255)), (TILESET_VIEW_RECT.x + 4, TILESET_VIEW_RECT.bottom - 20))

        if self.drag_start is not None:
            mouse = pygame.mouse.get_pos()
            if TILESET_VIEW_RECT.collidepoint(mouse):
                x0, y0 = min(self.drag_start[0], mouse[0]), min(self.drag_start[1], mouse[1])
                w, h = abs(mouse[0] - self.drag_start[0]), abs(mouse[1] - self.drag_start[1])
                pygame.draw.rect(self.screen, (255, 255, 0), (x0, y0, w, h), 2)

    def draw_tileset_tabs(self):
        pygame.draw.rect(self.screen, (35, 35, 35), TILESET_TABS_RECT)
        count = max(1, len(self.tileset_names))
        tab_width = TILESET_TABS_RECT.width / count
        for i in range(len(self.tileset_names)):
            rect = pygame.Rect(TILESET_TABS_RECT.x + round(i * tab_width), TILESET_TABS_RECT.y,
                                round(tab_width), TILESET_TABS_RECT.height)
            active = i == self.tileset_index
            pygame.draw.rect(self.screen, (90, 90, 150) if active else (55, 55, 55), rect)
            pygame.draw.rect(self.screen, (255, 255, 0) if active else (100, 100, 100), rect, 1)
            label = self.font.render(str(i + 1), True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_palette_panel(self):
        pygame.draw.rect(self.screen, (40, 40, 40), PALETTE_PANEL_RECT)
        cols = max(1, PALETTE_PANEL_RECT.width // PALETTE_CELL)
        for i, entry in enumerate(self.palette):
            col, row = i % cols, i // cols
            cell_x = PALETTE_PANEL_RECT.x + col * PALETTE_CELL
            cell_y = PALETTE_PANEL_RECT.y + row * PALETTE_CELL
            if cell_y > PALETTE_PANEL_RECT.bottom:
                break
            thumb = pygame.transform.smoothscale(entry.surface, (PALETTE_CELL - 8, PALETTE_CELL - 8)) \
                if entry.surface.get_width() > PALETTE_CELL - 8 or entry.surface.get_height() > PALETTE_CELL - 8 \
                else entry.surface
            self.screen.blit(thumb, (cell_x + 4, cell_y + 4))
            border = (255, 255, 0) if entry is self.active_stamp else (100, 100, 100)
            pygame.draw.rect(self.screen, border, (cell_x, cell_y, PALETTE_CELL, PALETTE_CELL), 1)

    def draw_bottom_bar(self):
        pygame.draw.rect(self.screen, (20, 20, 20), BOTTOM_BAR_RECT)
        header = "Project: {}   Layer [Tab]: {}   Snap [G]: {}   Active brush: {}".format(
            self.project.name, self.layer.upper(), self.snap_to_grid, self.active_brush or "none (visual only)")
        self.screen.blit(self.font.render(header, True, (220, 220, 220)), (BOTTOM_BAR_RECT.x + 6, BOTTOM_BAR_RECT.y + 6))

        legend_x = BOTTOM_BAR_RECT.x + 6
        legend_y = BOTTOM_BAR_RECT.y + 32
        for key_label, brush in BRUSH_LEGEND:
            label_text = "{} {}".format(key_label, brush or "none")
            label_surf = self.font.render(label_text, True, (220, 220, 220))
            entry_width = 16 + label_surf.get_width() + 14
            if legend_x + entry_width > BOTTOM_BAR_RECT.right - 6:
                legend_x = BOTTOM_BAR_RECT.x + 6
                legend_y += 20
            chip = pygame.Rect(legend_x, legend_y + 3, 12, 12)
            pygame.draw.rect(self.screen, COLLISION_COLORS[brush], chip)
            pygame.draw.rect(self.screen, (255, 255, 0) if brush == self.active_brush else (255, 255, 255), chip, 2 if brush == self.active_brush else 1)
            self.screen.blit(label_surf, (legend_x + 16, legend_y))
            legend_x += entry_width

        instructions = "Left click/drag: paint or place a row   Right click/drag: erase   [ ]: switch tileset   F5/Ctrl+S: save   F9: export   Esc: quit"
        self.screen.blit(self.font.render(instructions, True, (180, 180, 180)), (BOTTOM_BAR_RECT.x + 6, BOTTOM_BAR_RECT.bottom - 24))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "untitled"
    app = MapBuilderApp(name)
    app.run()


if __name__ == "__main__":
    main()
