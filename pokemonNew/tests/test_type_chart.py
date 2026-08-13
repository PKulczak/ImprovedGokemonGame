from battle.schemas import Type
from battle.type_chart import (
    TYPE_CHART, type_effectiveness, type_effectiveness_components,
)


def test_seventeen_types_no_fairy():
    assert len(Type) == 17
    assert not any(t.value == "fairy" for t in Type)


def test_super_effective():
    assert type_effectiveness(Type.WATER, [Type.FIRE]) == 2.0
    assert type_effectiveness(Type.ELECTRIC, [Type.WATER]) == 2.0
    assert type_effectiveness(Type.GRASS, [Type.WATER]) == 2.0


def test_resisted():
    assert type_effectiveness(Type.FIRE, [Type.WATER]) == 0.5
    assert type_effectiveness(Type.NORMAL, [Type.ROCK]) == 0.5


def test_seven_immunities():
    immunities = [
        (Type.NORMAL, Type.GHOST),
        (Type.FIGHTING, Type.GHOST),
        (Type.GHOST, Type.NORMAL),
        (Type.GROUND, Type.FLYING),
        (Type.ELECTRIC, Type.GROUND),
        (Type.PSYCHIC, Type.DARK),
        (Type.POISON, Type.STEEL),
    ]
    for atk, dfn in immunities:
        assert type_effectiveness(atk, [dfn]) == 0.0
    assert len(immunities) == 7


def test_dual_type_combines_multiplicatively():
    # Water vs Ground/Rock (Rhydon-like): Water is 2x vs Ground AND 2x vs Rock -> 4x
    assert type_effectiveness(Type.WATER, [Type.GROUND, Type.ROCK]) == 4.0
    # Electric vs Water/Ground (immune via Ground) -> 0
    assert type_effectiveness(Type.ELECTRIC, [Type.WATER, Type.GROUND]) == 0.0


def test_neutral_default():
    assert type_effectiveness(Type.NORMAL, [Type.NORMAL]) == 1.0


def test_components_match_float_table():
    assert type_effectiveness_components(Type.FIRE, Type.WATER) == (1, 2)
    assert type_effectiveness_components(Type.WATER, Type.FIRE) == (2, 1)
    assert type_effectiveness_components(Type.NORMAL, Type.GHOST) == (0, 1)
    assert type_effectiveness_components(Type.NORMAL, Type.NORMAL) == (1, 1)


def test_chart_only_has_seventeen_attacking_rows():
    assert len(TYPE_CHART) == 17
