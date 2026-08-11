#named game-balance constants, pulled out of fight.py/gokemon_game.py so tuning pacing/difficulty
#doesn't mean hunting through logic code for bare numbers. Pure UI layout coordinates and
#sprite-sheet layout numbers (column/row counts, tied to the actual asset files) are deliberately
#left alone - those aren't balance knobs.

#wild encounters & catching
WILD_ENCOUNTER_CHANCE = 0.007  # chance per frame-equivalent of a wild encounter while walking
                                # through grass (scaled by dt, same unit as the timers below)
CATCH_SUCCESS_ROLL_MAX = 5     # base catch chance is 1-in-this before the ball-tier/target-HP
                                # scaling battle_rules.catch_succeeds applies on top
MAX_CATCH_CHANCE = 0.9         # hard cap on catch_succeeds' final probability, however favourable
                                # the ball tier/target HP - a catch should never be a lock
ESCAPE_SUCCESS_ROLL_MAX = 4    # random.randint(1, this); a roll of 1 succeeds

#items
POTION_HEAL_AMOUNT = 20        # HP restored by using a Potion mid-battle, capped at the target's fullhp

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

#message/animation timing - all in "frame-equivalents" at the nominal 60fps design rate (see
#frame.py's dt calculation), NOT raw call counts - the main loop scales real elapsed time onto
#this unit so these durations stay real-time-correct regardless of the actual frame rate
SHORT_MESSAGE_FRAMES = 70          # intro "X vs Y", successful escape, and fight-loss messages
PLAYER_TURN_MESSAGE_FRAMES = 130
MONSTER_TURN_MESSAGE_FRAMES = 110
POKEMON_IDLE_ANIMATION_CADENCE = 10
ATTACK_EFFECT_ANIMATION_CADENCE = 4
WALK_ANIMATION_CADENCE_FRAMES = 6
YACHT_ACCELERATION_INTERVAL_FRAMES = 20
DIALOGUE_LINE_FRAMES = 140
CREDITS_AND_COMPLETION_FRAMES = 200

#caps how many frame-equivalents a single real gap can count for, so a one-off stall (a long
#GC/OS pause, alt-tabbing away and back) can't move the player through walls in one jump, dump a
#fight message straight to its end, or spike the wild-encounter roll to near-certain that frame
MAX_DT_FRAMES = 5

#holding the fast-forward key (see frame.py) multiplies dt by this before the MAX_DT_FRAMES cap
#above is applied, so fast-forwarding through a real stall still can't exceed the normal cap
FAST_FORWARD_MULTIPLIER = 2
