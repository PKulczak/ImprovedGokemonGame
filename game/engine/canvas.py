import pygame

pygame.font.init()

_FONT_NAMES = "timesnewroman,georgia,garamond"
_font_cache = {}


def _get_font(size):
    font = _font_cache.get(size)
    if font is None:
        font = pygame.font.SysFont(_FONT_NAMES, size)
        _font_cache[size] = font
    return font


#drop-in replacement for SimpleGUICS2Pygame's Canvas - draw_image/draw_text covered every
#need until the fast-travel map screen (FastTravel, ui.py) needed to highlight a node at
#runtime without a separate pre-rendered image per highlight colour/position combination,
#hence draw_rect below
class Canvas:
    def __init__(self, surface):
        self.surface = surface
        self._crop_cache = {}

    #grayscale=True desaturates the cropped/scaled result (cached separately from the colour
    #version under the same key+flag) - used to grey out a fainted Pokemon's party-slot icon
    #(see party_grid.draw_party_slot) without a second grayscale copy of every sprite on disk
    def draw_image(self, image, center_source, dim_source, center_dest, dim_dest, grayscale=False):
        src_w, src_h = int(round(dim_source[0])), int(round(dim_source[1]))
        if src_w > image.get_width() or src_h > image.get_height():
            return
        x0 = int(round(center_source[0] - dim_source[0] / 2))
        y0 = int(round(center_source[1] - dim_source[1] / 2))
        dest_w, dest_h = int(round(dim_dest[0])), int(round(dim_dest[1]))

        key = (id(image), x0, y0, src_w, src_h, dest_w, dest_h, grayscale)
        prepared = self._crop_cache.get(key)
        if prepared is None:
            crop = pygame.Surface((src_w, src_h), pygame.SRCALPHA)
            crop.blit(image, (0, 0), area=pygame.Rect(x0, y0, src_w, src_h))
            if (dest_w, dest_h) != (src_w, src_h):
                crop = pygame.transform.scale(crop, (dest_w, dest_h))
            if grayscale:
                crop = pygame.transform.grayscale(crop)
            prepared = crop
            self._crop_cache[key] = prepared

        dest_x = center_dest[0] - prepared.get_width() / 2
        dest_y = center_dest[1] - prepared.get_height() / 2
        self.surface.blit(prepared, (dest_x, dest_y))

    def draw_text(self, text, point, font_size, font_color, font_face='serif'):
        font = _get_font(font_size)
        rendered = font.render(text, True, pygame.Color(font_color))
        self.surface.blit(rendered, (point[0], point[1] - rendered.get_height() * 3 / 4))

    #true-centered text (both axes) at center, unlike draw_text's point-is-roughly-baseline
    #convention - needed for FastTravel's box labels, which get redrawn over a highlight rect
    #at varying lengths ("map" vs "route1") and need to land centered regardless
    def draw_text_centered(self, text, center, font_size, font_color):
        font = _get_font(font_size)
        rendered = font.render(text, True, pygame.Color(font_color))
        x = center[0] - rendered.get_width() / 2
        y = center[1] - rendered.get_height() / 2
        self.surface.blit(rendered, (x, y))

    #a filled, optionally rounded rectangle centered at center_dest - same center+dim
    #convention as draw_image, rather than pygame.Rect's own top-left+size, so call sites
    #don't have to convert between the two
    def draw_rect(self, center, dim, color, border_radius=0):
        w, h = int(round(dim[0])), int(round(dim[1]))
        x = int(round(center[0] - w / 2))
        y = int(round(center[1] - h / 2))
        pygame.draw.rect(self.surface, pygame.Color(color), pygame.Rect(x, y, w, h),
                          border_radius=border_radius)
