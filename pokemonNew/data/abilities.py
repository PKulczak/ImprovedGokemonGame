"""ABILITIES: dict[str, Ability] -- keyed by display name (the same strings
`Species.abilities`/`hidden_ability` reference, and the same strings
`PokemonInstance.to_dict()` persists for round-tripping).

Two kinds of entries:
  1. The 22 curated abilities with a working `effect_hook` that matches a key
     in `battle.abilities.ABILITY_HANDLERS` exactly.
  2. ~80 additional real Gen 1-5 ability names as flavor-only entries
     (`effect_hook=None`) so the roster-content workstream has plenty of
     authentic-sounding options for species outside the curated 22.
"""

from battle.schemas import Ability

# --- 1. Curated, mechanically-implemented abilities (must match battle/abilities.py) ---

_CURATED = [
    ("Blaze", "blaze", "Powers up Fire-type moves when the Pokemon's HP is low."),
    ("Torrent", "torrent", "Powers up Water-type moves when the Pokemon's HP is low."),
    ("Overgrow", "overgrow", "Powers up Grass-type moves when the Pokemon's HP is low."),
    ("Levitate", "levitate", "Gives full immunity to Ground-type moves."),
    ("Intimidate", "intimidate", "Lowers the opposing Pokemon's Attack stat upon entering battle."),
    ("Static", "static", "Contact with the Pokemon may cause paralysis."),
    ("Flame Body", "flame_body", "Contact with the Pokemon may cause a burn."),
    ("Rough Skin", "rough_skin", "Contact with the Pokemon damages the attacker."),
    ("Sturdy", "sturdy", "Gives immunity to one-hit KO moves."),
    ("Flash Fire", "flash_fire", "Powers up the Pokemon's Fire-type moves if it's hit by one."),
    ("Immunity", "immunity", "Prevents the Pokemon from getting poisoned."),
    ("Limber", "limber", "Prevents the Pokemon from being paralyzed."),
    ("Insomnia", "insomnia", "Prevents the Pokemon from falling asleep."),
    ("Water Veil", "water_veil", "Prevents the Pokemon from getting a burn."),
    ("Synchronize", "synchronize", "Passes a burn, poison, or paralysis it suffers to the Pokemon that inflicted it."),
    ("Speed Boost", "speed_boost", "Its Speed stat is boosted every turn."),
    ("Shed Skin", "shed_skin", "The Pokemon may heal its own status conditions by shedding its skin."),
    ("Drizzle", "drizzle", "The Pokemon makes it rain when it enters a battle."),
    ("Drought", "drought", "Turns the sunlight harsh when the Pokemon enters a battle."),
    ("Guts", "guts", "Boosts Attack if the Pokemon has a status condition; also ignores burn's damage penalty."),
    ("Marvel Scale", "marvel_scale", "Boosts Defense if the Pokemon has a status condition."),
    ("Keen Eye", "keen_eye", "Prevents other Pokemon from lowering accuracy; ignores their evasiveness too."),
]

ABILITIES = {
    name: Ability(name=name, flavor_text=flavor, effect_hook=hook)
    for name, hook, flavor in _CURATED
}

# --- 2. Flavor-only abilities: real Gen 1-5 names, effect_hook=None ---

_FLAVOR_NAMES = [
    "Chlorophyll", "Swarm", "Shield Dust", "Run Away", "Illuminate", "Pressure",
    "Damp", "Cute Charm", "Truant", "Hustle", "Serene Grace", "Early Bird",
    "Rock Head", "Sand Veil", "Swift Swim", "Thick Fat", "Clear Body",
    "Natural Cure", "Magic Guard", "Adaptability", "Technician", "Skill Link",
    "Klutz", "Anticipation", "Forewarn", "Frisk", "Heavy Metal", "Light Metal",
    "Multiscale", "Poison Point", "Effect Spore", "Trace", "Own Tempo",
    "Inner Focus", "Oblivious", "Soundproof", "Sticky Hold", "Suction Cups",
    "Big Pecks", "Tinted Lens", "Unburden", "Analytic", "Contrary", "Defiant",
    "Iron Fist", "Justified", "Moxie", "Reckless", "Regenerator", "Sap Sipper",
    "Solar Power", "Steadfast", "Telepathy", "Unaware", "Victory Star",
    "Weak Armor", "White Smoke", "Wonder Skin",
    # extra variety beyond the illustrative list
    "Battle Armor", "Compound Eyes", "Cursed Body", "Download", "Flower Gift",
    "Harvest", "Healer", "Hydration", "Hyper Cutter", "Ice Body", "Iron Barbs",
    "Leaf Guard", "Liquid Ooze", "Magic Bounce", "Mold Breaker", "Moody",
    "Overcoat", "Prankster", "Quick Feet", "Sand Stream", "Shell Armor",
    "Simple", "Snow Warning", "Solid Rock", "Water Absorb",
    # added to cover every ability name actually referenced by data/species.py
    "Vital Spirit", "Pickup", "Unnerve", "Super Luck", "Toxic Boost", "Competitive",
    "Sand Rush", "Poison Heal", "Scrappy", "Arena Trap", "Teravolt", "Rattled",
    "Infiltrator", "Cloud Nine", "Sheer Force", "Sniper", "Rivalry", "Snow Cloak",
    "Slow Start", "Rain Dish", "Sand Force", "Stall", "Turboblaze", "Stench",
    "Poison Touch", "Aftermath", "Lightning Rod", "Gluttony", "Dry Skin", "Air Lock",
    "Pickpocket",
]

for _name in _FLAVOR_NAMES:
    ABILITIES[_name] = Ability(name=_name, flavor_text=f"{_name}. (flavor entry, no battle effect implemented)", effect_hook=None)

del _name
