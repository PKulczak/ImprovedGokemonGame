try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

_cache = {}

#wraps simplegui._load_local_image with a path-keyed cache, so repeated loads of the same
#asset (e.g. every wall/NPC image getting reconstructed on a map reload) decode from disk once
def load_image(path):
    image = _cache.get(path)
    if image is None:
        image = simplegui._load_local_image(path)
        _cache[path] = image
    return image
