class ListMenu:
    """Generic cursor/list widget reused by party/bag/pokedex/pause menus."""

    def __init__(self, options, wrap=True):
        self.options = list(options)
        self.index = 0
        self.wrap = wrap

    def set_options(self, options):
        self.options = list(options)
        self.index = min(self.index, max(0, len(self.options) - 1))

    def move(self, delta):
        if not self.options:
            return
        if self.wrap:
            self.index = (self.index + delta) % len(self.options)
        else:
            self.index = max(0, min(len(self.options) - 1, self.index + delta))

    @property
    def selected(self):
        if not self.options:
            return None
        return self.options[self.index]

    def draw(self, surface, assets, pos, font_size=14, line_height=16,
              color=(255, 255, 255), selected_color=(255, 210, 70)):
        font = assets.font(font_size)
        x, y = pos
        for i, option in enumerate(self.options):
            label = option if isinstance(option, str) else str(option)
            col = selected_color if i == self.index else color
            rendered = font.render(label, True, col)
            surface.blit(rendered, (x, y + i * line_height))
