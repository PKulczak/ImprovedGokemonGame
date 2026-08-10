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


#drop-in replacement for SimpleGUICS2Pygame's Canvas - only draw_image/draw_text are used
#anywhere in this codebase, so that's all that's implemented here, matching the shim's
#exact crop/scale/center semantics so existing call sites don't need to change
class Canvas:
    def __init__(self, surface):
        self.surface = surface
        self._crop_cache = {}

    def draw_image(self, image, center_source, dim_source, center_dest, dim_dest):
        src_w, src_h = int(round(dim_source[0])), int(round(dim_source[1]))
        if src_w > image.get_width() or src_h > image.get_height():
            return
        x0 = int(round(center_source[0] - dim_source[0] / 2))
        y0 = int(round(center_source[1] - dim_source[1] / 2))
        dest_w, dest_h = int(round(dim_dest[0])), int(round(dim_dest[1]))

        key = (id(image), x0, y0, src_w, src_h, dest_w, dest_h)
        prepared = self._crop_cache.get(key)
        if prepared is None:
            crop = pygame.Surface((src_w, src_h), pygame.SRCALPHA)
            crop.blit(image, (0, 0), area=pygame.Rect(x0, y0, src_w, src_h))
            if (dest_w, dest_h) != (src_w, src_h):
                crop = pygame.transform.scale(crop, (dest_w, dest_h))
            prepared = crop
            self._crop_cache[key] = prepared

        dest_x = center_dest[0] - prepared.get_width() / 2
        dest_y = center_dest[1] - prepared.get_height() / 2
        self.surface.blit(prepared, (dest_x, dest_y))

    def draw_text(self, text, point, font_size, font_color, font_face='serif'):
        font = _get_font(font_size)
        rendered = font.render(text, True, pygame.Color(font_color))
        self.surface.blit(rendered, (point[0], point[1] - rendered.get_height() * 3 / 4))
