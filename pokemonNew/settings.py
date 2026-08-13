"""Pure constants shared across the engine. No pygame calls happen at import time."""

TILE_SIZE = 16

VIRTUAL_W = 240   # GBA-style internal resolution: 15 x 10 visible 16px tiles
VIRTUAL_H = 160
SCALE = 3
WINDOW_SIZE = (VIRTUAL_W * SCALE, VIRTUAL_H * SCALE)

FPS_CAP = 60
LOGIC_HZ = 60
LOGIC_DT = 1.0 / LOGIC_HZ
MAX_FRAME_DT = 0.25  # clamp to avoid the spiral of death after a long stall

STEP_DURATION = 0.15  # seconds to cross one tile while walking
RUN_STEP_DURATION = 0.09

CHAR_SOURCE_FRAME_W = 95   # source spritesheet frame size (player.png / bossN.png)
CHAR_SOURCE_FRAME_H = 118
CHAR_RENDER_W = 24         # scaled-down size actually drawn on a 16px tile grid
CHAR_RENDER_H = 30

SAVE_DIR_NAME = "save"
DEFAULT_SAVE_SLOT = 1
