import random

from battle.battle_state import Battle, BattleSide, Battler
from battle.items import ITEM_HANDLERS, ItemContext
from battle.natures import NATURES
from battle.pokemon import Gender, PokemonInstance, StatusCondition
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Item, ItemCategory, Move, MoveCategory,
    Species, Stat, StatBlock, Type,
)


def make_species():
    return Species(
        dex_number=1, name="Testmon", type1=Type.NORMAL, type2=None,
        base_stats=StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=64, ev_yield={Stat.SPEED: 1},
        growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=(),
    )


def make_pokemon(held_item=None, hp_fraction=1.0):
    mon = PokemonInstance(
        species=make_species(), level=50, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name="Keen Eye", flavor_text=""),
        held_item=held_item, current_hp=0, gender=Gender.GENDERLESS,
    )
    max_hp = mon.get_stats().hp
    mon.current_hp = max(1, int(max_hp * hp_fraction))
    return mon


def make_battle(player_item=None, player_hp_frac=1.0):
    player = Battler(pokemon=make_pokemon(player_item, hp_fraction=player_hp_frac))
    enemy = Battler(pokemon=make_pokemon())
    battle = Battle(BattleSide(active=player, bench=[]), BattleSide(active=enemy, bench=[]), random.Random(1))
    return battle, player, enemy


def item(name, hook, category=ItemCategory.HELD):
    return Item(name=name, category=category, flavor_text="", effect_hook=hook)


FIRE_MOVE = Move(name="Ember", type=Type.FIRE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25)


# --- held-item hooks ---

def test_leftovers_heals_one_sixteenth_end_of_turn():
    battle, player, _ = make_battle(item("Leftovers", "leftovers"), player_hp_frac=0.5)
    hp_before = player.pokemon.current_hp
    ctx = ItemContext(event="end_of_turn", battle=battle, battler=player)
    ITEM_HANDLERS["leftovers"](ctx)
    max_hp = player.pokemon.get_stats().hp
    assert player.pokemon.current_hp == hp_before + max(1, max_hp // 16)


def test_sitrus_berry_heals_30_at_half_hp_and_is_single_use():
    battle, player, _ = make_battle(item("Sitrus Berry", "sitrus_berry"), player_hp_frac=0.5)
    hp_before = player.pokemon.current_hp
    ctx = ItemContext(event="hp_threshold", battle=battle, battler=player)
    ITEM_HANDLERS["sitrus_berry"](ctx)
    assert player.pokemon.current_hp == hp_before + 30
    assert player.pokemon.held_item is None  # single-use, consumed


def test_sitrus_berry_does_not_trigger_above_half_hp():
    battle, player, _ = make_battle(item("Sitrus Berry", "sitrus_berry"), player_hp_frac=1.0)
    ctx = ItemContext(event="hp_threshold", battle=battle, battler=player)
    ITEM_HANDLERS["sitrus_berry"](ctx)
    assert player.pokemon.held_item is not None


def test_lum_berry_cures_status_and_confusion_single_use():
    battle, player, _ = make_battle(item("Lum Berry", "lum_berry"))
    player.pokemon.status = StatusCondition.PARALYSIS
    ctx = ItemContext(event="on_status_or_confusion_inflicted", battle=battle, battler=player, value=StatusCondition.PARALYSIS)
    ITEM_HANDLERS["lum_berry"](ctx)
    assert player.pokemon.status == StatusCondition.NONE
    assert player.pokemon.held_item is None


def test_lum_berry_cures_confusion():
    battle, player, _ = make_battle(item("Lum Berry", "lum_berry"))
    player.confusion_turns_remaining = 4
    ctx = ItemContext(event="on_status_or_confusion_inflicted", battle=battle, battler=player, value="confusion")
    ITEM_HANDLERS["lum_berry"](ctx)
    assert player.confusion_turns_remaining == 0
    assert player.pokemon.held_item is None


def test_choice_band_boosts_attack_and_locks_move():
    battle, player, _ = make_battle(item("Choice Band", "choice_band"))
    ctx = ItemContext(event="modify_stat", battler=player, extra={"stat_name": "attack"})
    assert ITEM_HANDLERS["choice_band"](ctx) == 1.5
    lock_ctx = ItemContext(event="on_move_used", battler=player, value="Tackle")
    ITEM_HANDLERS["choice_band"](lock_ctx)
    assert player.choice_locked_move == "Tackle"
    # second move used shouldn't override the lock
    lock_ctx2 = ItemContext(event="on_move_used", battler=player, value="Growl")
    ITEM_HANDLERS["choice_band"](lock_ctx2)
    assert player.choice_locked_move == "Tackle"


def test_choice_specs_boosts_sp_atk():
    battle, player, _ = make_battle(item("Choice Specs", "choice_specs"))
    ctx = ItemContext(event="modify_stat", battler=player, extra={"stat_name": "sp_atk"})
    assert ITEM_HANDLERS["choice_specs"](ctx) == 1.5
    ctx_wrong_stat = ItemContext(event="modify_stat", battler=player, extra={"stat_name": "attack"})
    assert ITEM_HANDLERS["choice_specs"](ctx_wrong_stat) is None


def test_type_boosting_items_give_20_percent():
    for hook, move_type in [("charcoal", Type.FIRE), ("mystic_water", Type.WATER),
                            ("miracle_seed", Type.GRASS), ("magnet", Type.ELECTRIC)]:
        move = Move(name="Move", type=move_type, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=10)
        ctx = ItemContext(event="modify_power", move=move)
        assert ITEM_HANDLERS[hook](ctx) == 1.2
        wrong_move = Move(name="Move2", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=10)
        ctx2 = ItemContext(event="modify_power", move=wrong_move)
        assert ITEM_HANDLERS[hook](ctx2) is None


def test_kings_rock_can_cause_flinch():
    battle, player, enemy = make_battle(item("King's Rock", "kings_rock"))

    class AlwaysProc:
        def random(self):
            return 0.0

    ctx = ItemContext(event="on_hit_landed", battle=battle, battler=player, other=enemy, rng=AlwaysProc())
    ITEM_HANDLERS["kings_rock"](ctx)
    assert enemy.flinched is True


def test_scope_lens_adds_one_crit_stage():
    ctx = ItemContext(event="modify_crit_stage", value=0)
    assert ITEM_HANDLERS["scope_lens"](ctx) == 1


def test_quick_claw_rolls_20_percent_chance():
    class AlwaysProc:
        def random(self):
            return 0.0
    ctx = ItemContext(event="roll_priority_bonus", rng=AlwaysProc())
    assert ITEM_HANDLERS["quick_claw"](ctx) is True

    class NeverProc:
        def random(self):
            return 0.99
    ctx2 = ItemContext(event="roll_priority_bonus", rng=NeverProc())
    assert ITEM_HANDLERS["quick_claw"](ctx2) is False


def test_focus_sash_survives_lethal_from_full_hp_single_use():
    battle, player, _ = make_battle(item("Focus Sash", "focus_sash"))
    ctx = ItemContext(event="check_survive_lethal", battler=player, extra={"was_full_hp": True})
    assert ITEM_HANDLERS["focus_sash"](ctx) is True
    assert player.pokemon.held_item is None
    # not full HP -> no protection
    battle2, player2, _ = make_battle(item("Focus Sash", "focus_sash"), player_hp_frac=0.5)
    ctx2 = ItemContext(event="check_survive_lethal", battler=player2, extra={"was_full_hp": False})
    assert ITEM_HANDLERS["focus_sash"](ctx2) is None


def test_focus_band_10_percent_not_single_use():
    class AlwaysProc:
        def random(self):
            return 0.0
    battle, player, _ = make_battle(item("Focus Band", "focus_band"))
    ctx = ItemContext(event="check_survive_lethal", battler=player, extra={"was_full_hp": False}, rng=AlwaysProc())
    assert ITEM_HANDLERS["focus_band"](ctx) is True
    assert player.pokemon.held_item is not None  # NOT single-use


# --- consumables (handler(pokemon) -> bool) ---

def test_potion_family_heal_amounts():
    mon = make_pokemon(hp_fraction=0.1)
    mon.current_hp = 1
    assert ITEM_HANDLERS["potion"](mon) is True
    assert mon.current_hp == 21


def test_super_hyper_max_potion():
    mon = make_pokemon(hp_fraction=0.1)
    mon.current_hp = 1
    ITEM_HANDLERS["super_potion"](mon)
    assert mon.current_hp == 51

    mon2 = make_pokemon(hp_fraction=0.1)
    mon2.current_hp = 1
    ITEM_HANDLERS["hyper_potion"](mon2)
    # 200 HP would overheal past this Pokemon's max (175), so it clamps to max
    assert mon2.current_hp == mon2.get_stats().hp

    mon3 = make_pokemon(hp_fraction=0.1)
    mon3.current_hp = 1
    ITEM_HANDLERS["max_potion"](mon3)
    assert mon3.current_hp == mon3.get_stats().hp


def test_potion_no_effect_at_full_hp():
    mon = make_pokemon(hp_fraction=1.0)
    assert ITEM_HANDLERS["potion"](mon) is False


def test_revive_and_max_revive_only_work_on_fainted():
    mon = make_pokemon()
    mon.current_hp = 0
    assert ITEM_HANDLERS["revive"](mon) is True
    assert mon.current_hp == max(1, mon.get_stats().hp // 2)

    mon2 = make_pokemon()
    assert ITEM_HANDLERS["revive"](mon2) is False  # not fainted -> no effect

    mon3 = make_pokemon()
    mon3.current_hp = 0
    assert ITEM_HANDLERS["max_revive"](mon3) is True
    assert mon3.current_hp == mon3.get_stats().hp


def test_status_cure_items():
    mon = make_pokemon()
    mon.status = StatusCondition.POISON
    assert ITEM_HANDLERS["antidote"](mon) is True
    assert mon.status == StatusCondition.NONE

    mon.status = StatusCondition.TOXIC
    assert ITEM_HANDLERS["antidote"](mon) is True

    mon.status = StatusCondition.PARALYSIS
    assert ITEM_HANDLERS["paralyze_heal"](mon) is True

    mon.status = StatusCondition.SLEEP
    assert ITEM_HANDLERS["awakening"](mon) is True

    mon.status = StatusCondition.BURN
    assert ITEM_HANDLERS["burn_heal"](mon) is True

    mon.status = StatusCondition.FREEZE
    assert ITEM_HANDLERS["ice_heal"](mon) is True

    mon.status = StatusCondition.PARALYSIS
    assert ITEM_HANDLERS["full_heal"](mon) is True
    assert mon.status == StatusCondition.NONE


def test_full_restore_heals_and_cures():
    mon = make_pokemon(hp_fraction=0.1)
    mon.current_hp = 1
    mon.status = StatusCondition.BURN
    assert ITEM_HANDLERS["full_restore"](mon) is True
    assert mon.current_hp == mon.get_stats().hp
    assert mon.status == StatusCondition.NONE


def test_all_essential_consumables_present():
    expected = {
        "potion", "super_potion", "hyper_potion", "max_potion", "revive",
        "max_revive", "full_heal", "antidote", "paralyze_heal", "awakening",
        "burn_heal", "ice_heal", "full_restore",
    }
    assert expected <= set(ITEM_HANDLERS.keys())


def test_all_14_curated_held_item_hooks_present():
    expected = {
        "leftovers", "sitrus_berry", "lum_berry", "choice_band", "choice_specs",
        "charcoal", "mystic_water", "miracle_seed", "magnet", "kings_rock",
        "scope_lens", "quick_claw", "focus_sash", "focus_band",
    }
    assert expected <= set(ITEM_HANDLERS.keys())
