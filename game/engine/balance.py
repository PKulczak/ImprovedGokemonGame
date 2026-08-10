#named game-balance constants, pulled out of fight.py/gokemon_game.py so tuning pacing/difficulty
#doesn't mean hunting through logic code for bare numbers. Pure UI layout coordinates and
#sprite-sheet layout numbers (column/row counts, tied to the actual asset files) are deliberately
#left alone - those aren't balance knobs.

#wild encounters & catching
WILD_ENCOUNTER_CHANCE = 0.007  # per-frame chance of a wild encounter while walking through grass
CATCH_SUCCESS_ROLL_MAX = 5     # random.randint(1, this); a roll of 1 succeeds. Also doubles as a
                                # forced-fail sentinel for NPC trainer battles (their pokemon can't be caught)
ESCAPE_SUCCESS_ROLL_MAX = 4    # random.randint(1, this); a roll of 1 succeeds

#party & leveling
MAX_PARTY_SIZE = 6
MAX_LEVEL = 25
ATK_GROWTH_RATE = 0.1
DEF_GROWTH_RATE = 0.01
HP_GROWTH_RATE = 0.1
BASE_MAX_EXP = 100
MAX_EXP_PER_LEVEL = 10
BASE_GIVE_EXP = 30
GIVE_EXP_PER_LEVEL = 3

#player
STARTING_LIVES = 6

#message/animation timing - all in frames, at the fixed 60fps main loop (see frame.py)
SHORT_MESSAGE_FRAMES = 70          # intro "X vs Y", successful escape, and fight-loss messages
PLAYER_TURN_MESSAGE_FRAMES = 130
MONSTER_TURN_MESSAGE_FRAMES = 110
POKEMON_IDLE_ANIMATION_CADENCE = 10
ATTACK_EFFECT_ANIMATION_CADENCE = 4
WALK_ANIMATION_CADENCE_FRAMES = 6
YACHT_ACCELERATION_INTERVAL_FRAMES = 20
DIALOGUE_LINE_FRAMES = 140
CREDITS_AND_COMPLETION_FRAMES = 200
