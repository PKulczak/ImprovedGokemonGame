"""ITEMS: dict[str, Item] -- the full curated + essential + flavor item list.

Sections:
  (a) curated held items with real hooks (matching battle.items.ITEM_HANDLERS)
  (b) every basic bag consumable, fully working (not flavor stubs)
  (c) the 4 Poke Balls, using `catch_multiplier` (Master Ball = 255.0
      sentinel that battle/catching.py treats as "always succeeds")
  (d) ~25 additional real held-item names as flavor-only entries
"""

from battle.schemas import Item, ItemCategory

ITEMS = {}


def _add(name, category, flavor, *, effect_hook=None, catch_multiplier=None, teaches_move=None):
    ITEMS[name] = Item(
        name=name, category=category, flavor_text=flavor, effect_hook=effect_hook,
        catch_multiplier=catch_multiplier, teaches_move=teaches_move,
    )


# --- (a) curated held items with real battle hooks ---

_add("Leftovers", ItemCategory.HELD, "Gradually restores HP during battle.", effect_hook="leftovers")
_add("Sitrus Berry", ItemCategory.HELD, "Restores a flat chunk of HP once it's about half or less.", effect_hook="sitrus_berry")
_add("Lum Berry", ItemCategory.HELD, "Cures any one status condition, including confusion.", effect_hook="lum_berry")
_add("Choice Band", ItemCategory.HELD, "Boosts Attack but allows the use of only one move.", effect_hook="choice_band")
_add("Choice Specs", ItemCategory.HELD, "Boosts Sp. Atk but allows the use of only one move.", effect_hook="choice_specs")
_add("Charcoal", ItemCategory.HELD, "Powers up Fire-type moves.", effect_hook="charcoal")
_add("Mystic Water", ItemCategory.HELD, "Powers up Water-type moves.", effect_hook="mystic_water")
_add("Miracle Seed", ItemCategory.HELD, "Powers up Grass-type moves.", effect_hook="miracle_seed")
_add("Magnet", ItemCategory.HELD, "Powers up Electric-type moves.", effect_hook="magnet")
_add("King's Rock", ItemCategory.HELD, "May cause the target to flinch when the holder lands a hit.", effect_hook="kings_rock")
_add("Scope Lens", ItemCategory.HELD, "Boosts the holder's critical-hit ratio.", effect_hook="scope_lens")
_add("Quick Claw", ItemCategory.HELD, "Occasionally allows the holder to act first.", effect_hook="quick_claw")
_add("Focus Sash", ItemCategory.HELD, "If at full HP, survives an otherwise-KO hit with 1 HP left. Single use.", effect_hook="focus_sash")
_add("Focus Band", ItemCategory.HELD, "The holder may endure a potential KO hit, leaving 1 HP.", effect_hook="focus_band")

# --- (b) essential bag consumables, all fully working ---

_add("Potion", ItemCategory.CONSUMABLE, "Restores 20 HP.", effect_hook="potion")
_add("Super Potion", ItemCategory.CONSUMABLE, "Restores 50 HP.", effect_hook="super_potion")
_add("Hyper Potion", ItemCategory.CONSUMABLE, "Restores 200 HP.", effect_hook="hyper_potion")
_add("Max Potion", ItemCategory.CONSUMABLE, "Fully restores HP.", effect_hook="max_potion")
_add("Revive", ItemCategory.CONSUMABLE, "Revives a fainted Pokemon with half its max HP.", effect_hook="revive")
_add("Max Revive", ItemCategory.CONSUMABLE, "Revives a fainted Pokemon with its max HP.", effect_hook="max_revive")
_add("Full Heal", ItemCategory.CONSUMABLE, "Heals any status condition.", effect_hook="full_heal")
_add("Antidote", ItemCategory.CONSUMABLE, "Cures poison (including toxic).", effect_hook="antidote")
_add("Paralyze Heal", ItemCategory.CONSUMABLE, "Cures paralysis.", effect_hook="paralyze_heal")
_add("Awakening", ItemCategory.CONSUMABLE, "Awakens a sleeping Pokemon.", effect_hook="awakening")
_add("Burn Heal", ItemCategory.CONSUMABLE, "Cures a burn.", effect_hook="burn_heal")
_add("Ice Heal", ItemCategory.CONSUMABLE, "Defrosts a frozen Pokemon.", effect_hook="ice_heal")
_add("Full Restore", ItemCategory.CONSUMABLE, "Fully restores HP and heals any status condition.", effect_hook="full_restore")

# --- (c) Poke Balls ---

_add("Poke Ball", ItemCategory.BALL, "A device for catching wild Pokemon.", catch_multiplier=1.0)
_add("Great Ball", ItemCategory.BALL, "A good, high-performance Ball with a higher catch rate than a Poke Ball.", catch_multiplier=1.5)
_add("Ultra Ball", ItemCategory.BALL, "An ultra-high-performance Ball with a higher catch rate than a Great Ball.", catch_multiplier=2.0)
_add("Master Ball", ItemCategory.BALL, "The best Ball with the ultimate performance. It will catch any wild Pokemon without fail.", catch_multiplier=255.0)

# --- (d) flavor-only held items for roster variety ---

_FLAVOR_HELD_ITEMS = [
    "Silk Scarf", "Black Belt", "Sharp Beak", "Poison Barb", "Soft Sand",
    "Hard Stone", "Silver Powder", "Spell Tag", "Dragon Fang", "Metal Coat",
    "Never-Melt Ice", "Twisted Spoon", "Black Glasses", "Sea Incense",
    "Shell Bell", "Amulet Coin",
    "Lucky Egg", "Soothe Bell", "Bright Powder", "Wide Lens", "Muscle Band",
    "Smooth Rock", "Heat Rock", "Icy Rock", "Damp Rock",
]

for _name in _FLAVOR_HELD_ITEMS:
    _add(_name, ItemCategory.HELD, f"{_name}. (flavor entry, no battle effect implemented)")

del _name
