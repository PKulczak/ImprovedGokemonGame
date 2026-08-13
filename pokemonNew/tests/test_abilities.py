import random

from battle.abilities import ABILITY_HANDLERS, AbilityContext
from battle.battle_state import Battle, BattleSide, Battler
from battle.natures import NATURES
from battle.pokemon import Gender, PokemonInstance, StatusCondition
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Move, MoveCategory, Species, Stat,
    StatBlock, Target, Type,
)
from battle.status import Weather


def make_species(name="Testmon", type1=Type.NORMAL, type2=None, base_stats=None):
    return Species(
        dex_number=1, name=name, type1=type1, type2=type2,
        base_stats=base_stats or StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=64, ev_yield={Stat.SPEED: 1},
        growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=(),
    )


def make_pokemon(ability_name="Keen Eye", species=None, level=50, hp_fraction=1.0):
    species = species or make_species()
    mon = PokemonInstance(
        species=species, level=level, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name=ability_name, flavor_text="", effect_hook=_hook_for(ability_name)),
        held_item=None, current_hp=0, gender=Gender.GENDERLESS,
    )
    max_hp = mon.get_stats().hp
    mon.current_hp = max(1, int(max_hp * hp_fraction))
    return mon


_HOOKS = {
    "Blaze": "blaze", "Torrent": "torrent", "Overgrow": "overgrow", "Levitate": "levitate",
    "Intimidate": "intimidate", "Static": "static", "Flame Body": "flame_body",
    "Rough Skin": "rough_skin", "Sturdy": "sturdy", "Flash Fire": "flash_fire",
    "Immunity": "immunity", "Limber": "limber", "Insomnia": "insomnia",
    "Water Veil": "water_veil", "Synchronize": "synchronize", "Speed Boost": "speed_boost",
    "Shed Skin": "shed_skin", "Drizzle": "drizzle", "Drought": "drought", "Guts": "guts",
    "Marvel Scale": "marvel_scale", "Keen Eye": "keen_eye",
}


def _hook_for(name):
    return _HOOKS.get(name)


def make_battle(player_ability="Keen Eye", enemy_ability="Keen Eye", player_hp_frac=1.0, rng=None):
    player = Battler(pokemon=make_pokemon(player_ability, hp_fraction=player_hp_frac))
    enemy = Battler(pokemon=make_pokemon(enemy_ability))
    battle = Battle(BattleSide(active=player, bench=[]), BattleSide(active=enemy, bench=[]), rng or random.Random(1))
    return battle, player, enemy


FIRE_MOVE = Move(name="Ember", type=Type.FIRE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25, makes_contact=False)
TACKLE = Move(name="Tackle", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, makes_contact=True)
GROUND_MOVE = Move(name="Earthquake", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=100, accuracy=100, pp=10, makes_contact=False)


def test_blaze_boosts_fire_move_at_low_hp_only():
    battle, player, _ = make_battle("Blaze", player_hp_frac=1.0)
    ctx = AbilityContext(event="modify_power", battle=battle, battler=player, move=FIRE_MOVE, value=1.0)
    assert ABILITY_HANDLERS["blaze"](ctx) is None
    player.pokemon.current_hp = max(1, player.pokemon.get_stats().hp // 4)
    ctx2 = AbilityContext(event="modify_power", battle=battle, battler=player, move=FIRE_MOVE, value=1.0)
    assert ABILITY_HANDLERS["blaze"](ctx2) == 1.5


def test_levitate_immune_to_ground_only():
    ctx = AbilityContext(event="check_immunity", battler=None, move=GROUND_MOVE)
    assert ABILITY_HANDLERS["levitate"](ctx) is True
    ctx2 = AbilityContext(event="check_immunity", battler=None, move=TACKLE)
    assert not ABILITY_HANDLERS["levitate"](ctx2)


def test_intimidate_lowers_opposing_attack_on_battle_start():
    battle, player, enemy = make_battle(player_ability="Intimidate", enemy_ability="Keen Eye")
    assert enemy.stages.attack == -1
    assert player.stages.attack == 0


def test_sturdy_blocks_ohko_only():
    ctx = AbilityContext(event="check_ohko_immunity")
    assert ABILITY_HANDLERS["sturdy"](ctx) is True
    ctx2 = AbilityContext(event="modify_power")
    assert ABILITY_HANDLERS["sturdy"](ctx2) is None


def test_flash_fire_grants_immunity_and_then_boosts_own_fire_moves():
    battle, player, _ = make_battle("Flash Fire")
    immune_ctx = AbilityContext(event="check_immunity", battle=battle, battler=player, move=FIRE_MOVE)
    assert ABILITY_HANDLERS["flash_fire"](immune_ctx) is True
    assert player.flags.get("flash_fire_active") is True
    boost_ctx = AbilityContext(event="modify_power", battle=battle, battler=player, move=FIRE_MOVE, value=1.0)
    assert ABILITY_HANDLERS["flash_fire"](boost_ctx) == 1.5


def test_status_immunity_abilities_block_only_their_status():
    immunity_ctx = AbilityContext(event="prevent_status", value=StatusCondition.POISON)
    assert ABILITY_HANDLERS["immunity"](immunity_ctx) is True
    immunity_ctx_burn = AbilityContext(event="prevent_status", value=StatusCondition.BURN)
    assert ABILITY_HANDLERS["immunity"](immunity_ctx_burn) is None

    limber_ctx = AbilityContext(event="prevent_status", value=StatusCondition.PARALYSIS)
    assert ABILITY_HANDLERS["limber"](limber_ctx) is True

    insomnia_ctx = AbilityContext(event="prevent_status", value=StatusCondition.SLEEP)
    assert ABILITY_HANDLERS["insomnia"](insomnia_ctx) is True

    water_veil_ctx = AbilityContext(event="prevent_status", value=StatusCondition.BURN)
    assert ABILITY_HANDLERS["water_veil"](water_veil_ctx) is True


def test_static_can_paralyze_attacker_on_contact():
    battle, player, enemy = make_battle(player_ability="Static")

    class AlwaysHit:
        def random(self):
            return 0.0
        def randint(self, a, b):
            return a

    ctx = AbilityContext(event="on_contact_received", battle=battle, battler=player, other=enemy, move=TACKLE, rng=AlwaysHit())
    ABILITY_HANDLERS["static"](ctx)
    assert enemy.pokemon.status == StatusCondition.PARALYSIS


def test_rough_skin_damages_attacker_on_contact():
    battle, player, enemy = make_battle(player_ability="Rough Skin")
    hp_before = enemy.pokemon.current_hp
    ctx = AbilityContext(event="on_contact_received", battle=battle, battler=player, other=enemy, move=TACKLE)
    ABILITY_HANDLERS["rough_skin"](ctx)
    assert enemy.pokemon.current_hp < hp_before


def test_synchronize_reflects_status_to_source():
    battle, player, enemy = make_battle(player_ability="Synchronize")
    # enemy (source) inflicts poison on player (has Synchronize) -> should reflect back to enemy
    battle.try_inflict_status(player, StatusCondition.POISON, source_battler=enemy)
    assert player.pokemon.status == StatusCondition.POISON
    assert enemy.pokemon.status == StatusCondition.POISON


def test_speed_boost_increases_speed_stage_each_end_of_turn():
    battle, player, _ = make_battle(player_ability="Speed Boost")
    ctx = AbilityContext(event="end_of_turn", battle=battle, battler=player, rng=random.Random(1))
    ABILITY_HANDLERS["speed_boost"](ctx)
    assert player.stages.speed == 1


def test_shed_skin_can_cure_status_end_of_turn():
    battle, player, _ = make_battle(player_ability="Shed Skin")
    player.pokemon.status = StatusCondition.PARALYSIS

    class AlwaysProc:
        def random(self):
            return 0.0
        def randint(self, a, b):
            return a

    ctx = AbilityContext(event="end_of_turn", battle=battle, battler=player, rng=AlwaysProc())
    ABILITY_HANDLERS["shed_skin"](ctx)
    assert player.pokemon.status == StatusCondition.NONE


def test_drizzle_sets_rain_with_house_rule_duration_on_switch_in():
    battle, player, _ = make_battle(player_ability="Drizzle")
    assert battle.weather == Weather.RAIN
    assert battle.weather_turns_remaining == 8


def test_drought_sets_sun_with_house_rule_duration_on_switch_in():
    battle, player, _ = make_battle(player_ability="Drought")
    assert battle.weather == Weather.SUN
    assert battle.weather_turns_remaining == 8


def test_guts_boosts_attack_while_statused_and_negates_burn_halving():
    battle, player, _ = make_battle("Guts")
    ctx = AbilityContext(event="modify_stat", battler=player, extra={"stat_name": "attack"})
    assert ABILITY_HANDLERS["guts"](ctx) is None
    player.pokemon.status = StatusCondition.BURN
    ctx2 = AbilityContext(event="modify_stat", battler=player, extra={"stat_name": "attack"})
    assert ABILITY_HANDLERS["guts"](ctx2) == 1.5
    halve_ctx = AbilityContext(event="check_burn_halving", battler=player)
    assert ABILITY_HANDLERS["guts"](halve_ctx) is False


def test_marvel_scale_boosts_defense_while_statused():
    battle, player, _ = make_battle("Marvel Scale")
    player.pokemon.status = StatusCondition.PARALYSIS
    ctx = AbilityContext(event="modify_stat", battler=player, extra={"stat_name": "defense"})
    assert ABILITY_HANDLERS["marvel_scale"](ctx) == 1.5


def test_keen_eye_blocks_accuracy_drop_and_ignores_evasion():
    ctx = AbilityContext(event="prevent_stat_stage_change", extra={"stat": "accuracy", "stages": -1})
    assert ABILITY_HANDLERS["keen_eye"](ctx) is True
    ctx2 = AbilityContext(event="prevent_stat_stage_change", extra={"stat": "attack", "stages": -1})
    assert ABILITY_HANDLERS["keen_eye"](ctx2) is None
    ctx3 = AbilityContext(event="check_ignore_evasion")
    assert ABILITY_HANDLERS["keen_eye"](ctx3) is True


def test_all_22_curated_abilities_present():
    expected = set(_HOOKS.values())
    assert set(ABILITY_HANDLERS.keys()) == expected
    assert len(expected) == 22
