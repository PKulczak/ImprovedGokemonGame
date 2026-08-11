import os
import pygame
from game.engine import balance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SFX_DIR = '{}/Sound/sfx'.format(BASE_DIR)
_MUSIC_DIR = '{}/Sound/music'.format(BASE_DIR)

#code-only pass (feature-ideas.md item 10) - every call site below is wired up ahead of the
#actual audio assets landing, so a missing .wav/.ogg is the expected, silent-by-design state,
#not a bug. Expected filenames once assets are added:
#  SFX (Sound/sfx/<name>.wav): menu_move, select, hit, catch, catch_fail, level_up, low_hp, save
#  Music (Sound/music/<name>.ogg): town, route, pokecenter, gym, boss, battle
_mixer_ready = False
_sfx_cache = {}
_current_music = None
_volume = balance.DEFAULT_VOLUME

#pygame.mixer needs its own init (separate from pygame.init()) and can fail outright if the
#machine has no audio device at all - caught here so a missing/broken audio backend degrades to
#silence instead of crashing the whole game
def init():
    global _mixer_ready
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(_volume)
        _mixer_ready = True
    except pygame.error:
        _mixer_ready = False

def get_volume():
    return _volume

#0.0-1.0, applied to every SFX played from here on and to the currently-playing music track -
#the single volume knob the pause menu's Left/Right control adjusts
def set_volume(volume):
    global _volume
    _volume = max(0.0, min(1.0, volume))
    if _mixer_ready:
        pygame.mixer.music.set_volume(_volume)

#plays a one-shot sound effect by name (e.g. "hit"), looked up at Sound/sfx/<name>.wav and
#cached (including a failed/missing lookup, so a missing asset only costs one failed disk read
#per name, not one per call)
def play_sfx(name):
    if not _mixer_ready:
        return
    if name not in _sfx_cache:
        path = '{}/{}.wav'.format(_SFX_DIR, name)
        try:
            _sfx_cache[name] = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            _sfx_cache[name] = None
    sound = _sfx_cache[name]
    if sound is not None:
        sound.set_volume(_volume)
        sound.play()

#loops a named background track (Sound/music/<name>.ogg) unless it's already the one playing.
#Missing assets fail silently the same way play_sfx does, but aren't cached - if the file
#appears later (assets dropped in mid-session), the very next call picks it up automatically
def play_music(name):
    global _current_music
    if not _mixer_ready or name == _current_music:
        return
    path = '{}/{}.ogg'.format(_MUSIC_DIR, name)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_volume)
        pygame.mixer.music.play(-1)
        _current_music = name
    except (pygame.error, FileNotFoundError):
        _current_music = None

def stop_music():
    global _current_music
    if _mixer_ready:
        pygame.mixer.music.stop()
    _current_music = None
