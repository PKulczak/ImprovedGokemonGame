"""17x17 Gen 1-5 (no Fairy) type effectiveness chart."""

from .schemas import Type

IMMUNE, RESIST, NEUTRAL, SUPER = 0.0, 0.5, 1.0, 2.0

N = Type.NORMAL
FIR = Type.FIRE
W = Type.WATER
E = Type.ELECTRIC
G = Type.GRASS
I = Type.ICE
F = Type.FIGHTING
P = Type.POISON
GD = Type.GROUND
FL = Type.FLYING
PS = Type.PSYCHIC
B = Type.BUG
R = Type.ROCK
GH = Type.GHOST
D = Type.DRAGON
DK = Type.DARK
S = Type.STEEL

TYPE_CHART = {
    N: {R: RESIST, GH: IMMUNE, S: RESIST},
    FIR: {FIR: RESIST, W: RESIST, G: SUPER, I: SUPER, B: SUPER,
          R: RESIST, D: RESIST, S: SUPER},
    W: {FIR: SUPER, W: RESIST, G: RESIST, GD: SUPER,
        R: SUPER, D: RESIST},
    E: {W: SUPER, E: RESIST, G: RESIST, GD: IMMUNE,
        FL: SUPER, D: RESIST},
    G: {FIR: RESIST, W: SUPER, G: RESIST, P: RESIST, GD: SUPER,
        FL: RESIST, B: RESIST, R: SUPER, D: RESIST, S: RESIST},
    I: {FIR: RESIST, W: RESIST, G: SUPER, I: RESIST, GD: SUPER,
        FL: SUPER, D: SUPER, S: RESIST},
    F: {N: SUPER, I: SUPER, P: RESIST, FL: RESIST, PS: RESIST,
        B: RESIST, R: SUPER, GH: IMMUNE, DK: SUPER, S: SUPER},
    P: {G: SUPER, P: RESIST, GD: RESIST, R: RESIST,
        GH: RESIST, S: IMMUNE},
    GD: {FIR: SUPER, E: SUPER, G: RESIST, P: SUPER, FL: IMMUNE,
         B: RESIST, R: SUPER, S: SUPER},
    FL: {E: RESIST, G: SUPER, F: SUPER, B: SUPER,
         R: RESIST, S: RESIST},
    PS: {F: SUPER, P: SUPER, PS: RESIST, DK: IMMUNE, S: RESIST},
    B: {FIR: RESIST, G: SUPER, F: RESIST, P: RESIST, FL: RESIST,
        PS: SUPER, GH: RESIST, DK: SUPER, S: RESIST},
    R: {FIR: SUPER, I: SUPER, F: RESIST, GD: RESIST, FL: SUPER,
        B: SUPER, S: RESIST},
    GH: {N: IMMUNE, PS: SUPER, GH: SUPER, DK: RESIST, S: RESIST},
    D: {D: SUPER, S: RESIST},
    DK: {F: RESIST, PS: SUPER, GH: SUPER, DK: RESIST, S: RESIST},
    S: {FIR: RESIST, W: RESIST, E: RESIST, I: SUPER,
        R: SUPER, S: RESIST},
}

# Multiplier -> exact integer (numerator, denominator), used by the damage
# pipeline which must apply each defending type's effectiveness step as its
# own integer (num, den) multiplication rather than a single float.
_MULT_TO_FRACTION = {
    IMMUNE: (0, 1),
    RESIST: (1, 2),
    NEUTRAL: (1, 1),
    SUPER: (2, 1),
}


def type_effectiveness(attacking_type, defending_types):
    """Return the combined float multiplier of attacking_type vs 1-2 defending types."""
    mult = 1.0
    row = TYPE_CHART.get(attacking_type, {})
    for def_type in defending_types:
        if def_type is None:
            continue
        mult *= row.get(def_type, 1.0)
    return mult


def type_effectiveness_components(attacking_type, defending_type):
    """Return the (numerator, denominator) pair for a single defending type."""
    row = TYPE_CHART.get(attacking_type, {})
    mult = row.get(defending_type, 1.0)
    return _MULT_TO_FRACTION[mult]
