import pygame

_cache = {}

#wraps pygame.image.load with a path-keyed cache, so repeated loads of the same
#asset (e.g. every wall/NPC image getting reconstructed on a map reload) decode from disk once
def load_image(path):
    image = _cache.get(path)
    if image is None:
        image = pygame.image.load(path)
        _cache[path] = image
    return image
