"""The 25 real Gen 3 natures.

Row = stat raised (x1.1), column = stat lowered (x0.9). The 5 diagonal
entries are neutral (increased_stat == decreased_stat == None).
"""

from .schemas import Nature, Stat

_RAISED_LOWERED = {
    # (raised, lowered) -> name
    (Stat.ATTACK, Stat.ATTACK): "Hardy",
    (Stat.ATTACK, Stat.DEFENSE): "Lonely",
    (Stat.ATTACK, Stat.SP_ATK): "Adamant",
    (Stat.ATTACK, Stat.SP_DEF): "Naughty",
    (Stat.ATTACK, Stat.SPEED): "Brave",

    (Stat.DEFENSE, Stat.ATTACK): "Bold",
    (Stat.DEFENSE, Stat.DEFENSE): "Docile",
    (Stat.DEFENSE, Stat.SP_ATK): "Impish",
    (Stat.DEFENSE, Stat.SP_DEF): "Lax",
    (Stat.DEFENSE, Stat.SPEED): "Relaxed",

    (Stat.SP_ATK, Stat.ATTACK): "Modest",
    (Stat.SP_ATK, Stat.DEFENSE): "Mild",
    (Stat.SP_ATK, Stat.SP_ATK): "Bashful",
    (Stat.SP_ATK, Stat.SP_DEF): "Rash",
    (Stat.SP_ATK, Stat.SPEED): "Quiet",

    (Stat.SP_DEF, Stat.ATTACK): "Calm",
    (Stat.SP_DEF, Stat.DEFENSE): "Gentle",
    (Stat.SP_DEF, Stat.SP_ATK): "Careful",
    (Stat.SP_DEF, Stat.SP_DEF): "Quirky",
    (Stat.SP_DEF, Stat.SPEED): "Sassy",

    (Stat.SPEED, Stat.ATTACK): "Timid",
    (Stat.SPEED, Stat.DEFENSE): "Hasty",
    (Stat.SPEED, Stat.SP_ATK): "Jolly",
    (Stat.SPEED, Stat.SP_DEF): "Naive",
    (Stat.SPEED, Stat.SPEED): "Serious",
}

_NEUTRAL_NAMES = {"Hardy", "Docile", "Bashful", "Quirky", "Serious"}

NATURES = {}
for (raised, lowered), name in _RAISED_LOWERED.items():
    if name in _NEUTRAL_NAMES:
        NATURES[name] = Nature(name=name, increased_stat=None, decreased_stat=None)
    else:
        NATURES[name] = Nature(name=name, increased_stat=raised, decreased_stat=lowered)

assert len(NATURES) == 25
