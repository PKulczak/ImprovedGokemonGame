"""SPECIES: dict[str, Species] -- one entry per name in data.roster_dex_map.ROSTER.

Covers Gens 1-5 with real (to the best of available knowledge) types, base
stats, abilities, growth rates and evolution chains. Every trade-based
evolution in the real games (Graveler->Golem, Haunter->Gengar, Seadra->
Kingdra, Rhydon->Rhyperior, Dusclops->Dusknoir) and every friendship-based
evolution (Budew->Roselia, Togepi->Togetic, Woobat->Swoobat, Riolu->Lucario)
has been converted to a plain LEVEL_UP or ITEM rule per the design doc, so
nothing is ever permanently unobtainable in a single-player, no-trading game.

dex_number is always pulled from ROSTER (never retyped) so the species'
sprite folder name (assets/pokemon/<lowercased name>/) always matches.
"""

from battle.schemas import (
    Type, Stat, StatBlock, GenderRatio, GrowthRate,
    EvolutionTrigger, EvolutionRule, Species,
)
from data.roster_dex_map import ROSTER

SPECIES: dict[str, Species] = {}


def _lvl(target: str, level: int) -> EvolutionRule:
    return EvolutionRule(trigger=EvolutionTrigger.LEVEL_UP, target_dex_number=ROSTER[target], min_level=level)


def _item(target: str, item: str, note: str = "") -> EvolutionRule:
    return EvolutionRule(trigger=EvolutionTrigger.ITEM, target_dex_number=ROSTER[target], item_name=item, note=note)


def _other(target: str, level: int, note: str) -> EvolutionRule:
    return EvolutionRule(trigger=EvolutionTrigger.OTHER, target_dex_number=ROSTER[target], min_level=level, note=note)


def _add(name, type1, type2, stats, abilities, hidden, gender, catch, exp, ev, growth, learnset, evolutions=(), flavor=""):
    SPECIES[name] = Species(
        dex_number=ROSTER[name], name=name, type1=type1, type2=type2,
        base_stats=stats, abilities=abilities, hidden_ability=hidden,
        gender_ratio=gender, base_catch_rate=catch, base_exp_yield=exp,
        ev_yield=ev, growth_rate=growth, learnset=learnset,
        evolutions=evolutions, flavor_text=flavor,
    )


# ======================================================================
# Starters
# ======================================================================
_add("Chikorita", Type.GRASS, None, StatBlock(45, 49, 65, 49, 65, 45), ("Overgrow",), "Leaf Guard", GenderRatio.MOSTLY_MALE, 45, 64, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (7, "Vine Whip"), (13, "Synthesis"), (19, "Razor Leaf"), (25, "Body Slam"), (31, "Solar Beam")),
     (_lvl("Bayleef", 16),), "A gentle Grass-type Pokemon whose leaf-crown fragrance calms those around it.")
_add("Bayleef", Type.GRASS, None, StatBlock(60, 62, 80, 63, 80, 60), ("Overgrow",), "Leaf Guard", GenderRatio.MOSTLY_MALE, 45, 142, {Stat.SP_DEF: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Vine Whip"), (13, "Synthesis"), (19, "Razor Leaf"), (27, "Body Slam"), (33, "Solar Beam")),
     (_lvl("Meganium", 32),), "Its neck-ringed leaves release a pleasant aroma that boosts friendliness.")
_add("Meganium", Type.GRASS, None, StatBlock(80, 82, 100, 83, 100, 80), ("Overgrow",), "Leaf Guard", GenderRatio.MOSTLY_MALE, 45, 236, {Stat.SP_DEF: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Vine Whip"), (13, "Synthesis"), (19, "Razor Leaf"), (27, "Body Slam"), (33, "Solar Beam"), (41, "Growth")),
     (), "The aroma of its enormous flower petals calms an entire battlefield.")

_add("Torchic", Type.FIRE, None, StatBlock(45, 60, 40, 70, 50, 45), ("Blaze",), "Speed Boost", GenderRatio.MOSTLY_MALE, 45, 62, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Growl"), (7, "Ember"), (13, "Sand Attack"), (19, "Fire Punch"), (25, "Slash"), (31, "Flamethrower")),
     (_lvl("Combusken", 16),), "A downy chick Pokemon that keeps a small flame burning in its belly.")
_add("Combusken", Type.FIRE, Type.FIGHTING, StatBlock(60, 85, 60, 85, 60, 55), ("Blaze",), "Speed Boost", GenderRatio.MOSTLY_MALE, 45, 142, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Growl"), (1, "Ember"), (13, "Rock Smash"), (19, "Fire Punch"), (27, "Slash"), (33, "Flamethrower")),
     (_lvl("Blaziken", 36),), "It shatters rocks with a swift roundhouse kick honed by its fiery spirit.")
_add("Blaziken", Type.FIRE, Type.FIGHTING, StatBlock(80, 120, 70, 110, 70, 80), ("Blaze",), "Speed Boost", GenderRatio.MOSTLY_MALE, 45, 240, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Growl"), (1, "Ember"), (13, "Rock Smash"), (19, "Fire Punch"), (27, "Slash"), (33, "Flamethrower"), (43, "Close Combat")),
     (), "Its powerful legs let it clear a 30-story building in a single leap.")

_add("Oshawott", Type.WATER, None, StatBlock(55, 55, 45, 63, 45, 45), ("Torrent",), "Shell Armor", GenderRatio.MOSTLY_MALE, 45, 62, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Tail Whip"), (7, "Water Gun"), (13, "Withdraw"), (19, "Aqua Jet"), (25, "Slash"), (31, "Surf")),
     (_lvl("Dewott", 17),), "The scalchop on its stomach isn't just a shell -- it doubles as a blade.")
_add("Dewott", Type.WATER, None, StatBlock(75, 75, 60, 83, 60, 60), ("Torrent",), "Shell Armor", GenderRatio.MOSTLY_MALE, 45, 145, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Tail Whip"), (1, "Water Gun"), (13, "Withdraw"), (19, "Aqua Jet"), (27, "Slash"), (33, "Surf")),
     (_lvl("Samurott", 36),), "It wields a pair of scalchops as blades in a self-taught two-sword style.")
_add("Samurott", Type.WATER, None, StatBlock(95, 100, 85, 108, 70, 70), ("Torrent",), "Shell Armor", GenderRatio.MOSTLY_MALE, 45, 238, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Tail Whip"), (1, "Water Gun"), (13, "Withdraw"), (19, "Aqua Jet"), (27, "Slash"), (33, "Surf"), (43, "Hydro Pump")),
     (), "Its imposing bladed armor and calm dignity have made it a favorite of Trainers everywhere.")

# ======================================================================
# Gym 1 -- Bug -- Wren (Bramblegate Town)
# ======================================================================
_add("Ledyba", Type.BUG, Type.FLYING, StatBlock(40, 20, 30, 40, 80, 55), ("Swarm", "Early Bird"), "Rattled", GenderRatio.EVEN, 255, 53, {Stat.SP_DEF: 1}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Supersonic"), (9, "Bug Bite"), (15, "String Shot"), (21, "Agility"), ), (_lvl("Ledian", 18),), "It communicates with others by drumming rhythms on leaves with its foreleg.")
_add("Ledian", Type.BUG, Type.FLYING, StatBlock(55, 35, 50, 55, 110, 85), ("Swarm", "Early Bird"), "Iron Fist", GenderRatio.EVEN, 90, 137, {Stat.SP_DEF: 2}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Supersonic"), (1, "Bug Bite"), (15, "String Shot"), (21, "Agility"), (29, "Signal Beam"), (37, "Megahorn")),
     (), "Said to descend from the stars on clear nights, dancing under starlight.")

_add("Wurmple", Type.BUG, None, StatBlock(45, 45, 35, 20, 30, 20), ("Shield Dust",), "Run Away", GenderRatio.EVEN, 255, 56, {Stat.HP: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "String Shot")),
     (_other("Silcoon", 7, "Random split at level 7 based on Wurmple's hidden trait -- becomes Silcoon or Cascoon."),
      _other("Cascoon", 7, "Random split at level 7 based on Wurmple's hidden trait -- becomes Silcoon or Cascoon.")),
     "Its bright colors warn predators of the sharp, poisonous spike hidden on its tail.")
_add("Silcoon", Type.BUG, None, StatBlock(50, 35, 55, 25, 25, 15), ("Shed Skin",), "Shed Skin", GenderRatio.EVEN, 120, 72, {Stat.DEFENSE: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Defense Curl")), (_lvl("Beautifly", 10),), "It stays motionless inside its silk cocoon, waiting patiently to evolve.")
_add("Beautifly", Type.BUG, Type.FLYING, StatBlock(60, 70, 50, 90, 50, 65), ("Swarm",), "Rivalry", GenderRatio.EVEN, 45, 178, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Absorb"), (10, "Gust"), (17, "Stun Spore"), (24, "Signal Beam"), (31, "Giga Drain")),
     (), "Its long, thin mouthpart is ideal for sipping nectar from flowers.")
_add("Cascoon", Type.BUG, None, StatBlock(50, 35, 55, 25, 25, 15), ("Shed Skin",), "Shed Skin", GenderRatio.EVEN, 120, 72, {Stat.DEFENSE: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Defense Curl")), (_lvl("Dustox", 10),), "It hangs motionless from a branch, watching its surroundings through a gap in its shell.")
_add("Dustox", Type.BUG, Type.POISON, StatBlock(60, 50, 70, 50, 90, 65), ("Shield Dust",), "Compound Eyes", GenderRatio.EVEN, 45, 178, {Stat.SP_DEF: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Absorb"), (10, "Gust"), (17, "Poison Sting"), (24, "Sludge"), (31, "Sludge Bomb")),
     (), "It is drawn to light at night, and the toxic scales that cover its wings deter attackers.")

# ======================================================================
# Gym 2 -- Normal -- Bartle (Corvid Hollow)
# ======================================================================
_add("Bidoof", Type.NORMAL, None, StatBlock(59, 45, 40, 35, 40, 31), ("Simple", "Unaware"), "Moody", GenderRatio.EVEN, 255, 59, {Stat.HP: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Growl"), (7, "Defense Curl"), (13, "Take Down"), (19, "Slam")), (_lvl("Bibarel", 15),), "Its front teeth grow constantly, so it gnaws on logs to wear them down.")
_add("Bibarel", Type.NORMAL, Type.WATER, StatBlock(79, 85, 60, 55, 60, 71), ("Simple", "Unaware"), "Moody", GenderRatio.EVEN, 127, 145, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Growl"), (1, "Defense Curl"), (13, "Take Down"), (19, "Slam"), (25, "Water Gun"), (33, "Body Slam")),
     (), "A hard-working Pokemon that builds elaborate dams across rivers, log by log.")

_add("Lillipup", Type.NORMAL, None, StatBlock(45, 60, 45, 25, 45, 55), ("Vital Spirit", "Pickup"), "Run Away", GenderRatio.EVEN, 255, 55, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (9, "Take Down"), (17, "Crunch")), (_lvl("Herdier", 16),), "Its keen sense of smell lets it read the moods of its Trainer and opponents alike.")
_add("Herdier", Type.NORMAL, None, StatBlock(65, 80, 65, 35, 65, 60), ("Vital Spirit", "Pickup"), "Scrappy", GenderRatio.EVEN, 120, 130, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Take Down"), (17, "Crunch"), (25, "Body Slam")), (_lvl("Stoutland", 32),), "Its thick, wiry coat protects it well and once marked it as a noble's guardian.")
_add("Stoutland", Type.NORMAL, None, StatBlock(85, 100, 90, 45, 90, 80), ("Intimidate",), "Scrappy", GenderRatio.EVEN, 45, 225, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Take Down"), (17, "Crunch"), (25, "Body Slam"), (37, "Double-Edge")),
     (), "Its magnificent mustache detects subtle changes in the wind and weather.")

_add("Girafarig", Type.NORMAL, Type.PSYCHIC, StatBlock(70, 80, 65, 90, 65, 85), ("Inner Focus", "Early Bird"), "Sap Sipper", GenderRatio.EVEN, 60, 159, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Growl"), (9, "Confusion"), (17, "Astonish"), (25, "Psybeam"), (33, "Psychic")),
     (), "Its tail has a rudimentary brain, and is even more alert than the head when danger is near.")

# ======================================================================
# Gym 3 -- Electric -- Talia (Ferroport City)
# ======================================================================
_add("Voltorb", Type.ELECTRIC, None, StatBlock(40, 30, 50, 55, 55, 100), ("Soundproof", "Static"), "Aftermath", GenderRatio.GENDERLESS, 190, 66, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Charge Beam"), (1, "Tackle"), (11, "Spark"), (21, "Discharge"), (31, "Thunderbolt")), (_lvl("Electrode", 30),), "So similar to a Poke Ball in shape that it's regularly mistaken for one.")
_add("Electrode", Type.ELECTRIC, None, StatBlock(60, 50, 70, 80, 80, 150), ("Soundproof", "Static"), "Aftermath", GenderRatio.GENDERLESS, 60, 172, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Charge Beam"), (1, "Tackle"), (1, "Spark"), (21, "Discharge"), (31, "Thunderbolt"), (41, "Thunder")),
     (), "It stores electricity gathered from the atmosphere, then rolls at tremendous speed.")

_add("Shinx", Type.ELECTRIC, None, StatBlock(45, 65, 34, 40, 34, 45), ("Rivalry", "Intimidate"), "Guts", GenderRatio.EVEN, 235, 60, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Charge Beam"), (9, "Spark"), (17, "Leer")), (_lvl("Luxio", 15),), "Its body glows faintly, an early-warning sign whenever danger approaches.")
_add("Luxio", Type.ELECTRIC, None, StatBlock(60, 85, 49, 60, 49, 60), ("Rivalry", "Intimidate"), "Guts", GenderRatio.EVEN, 120, 127, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Charge Beam"), (1, "Spark"), (17, "Leer"), (25, "Thunder Fang")), (_lvl("Luxray", 30),), "Claws that store static electricity spark whenever it flexes them.")
_add("Luxray", Type.ELECTRIC, None, StatBlock(80, 120, 79, 95, 79, 70), ("Rivalry", "Intimidate"), "Guts", GenderRatio.EVEN, 45, 235, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Charge Beam"), (1, "Spark"), (17, "Leer"), (25, "Thunder Fang"), (37, "Thunderbolt"), (45, "Discharge")),
     (), "Its X-ray vision can see clean through obstacles to spot prey from far away.")

_add("Joltik", Type.BUG, Type.ELECTRIC, StatBlock(50, 47, 50, 57, 50, 65), ("Compound Eyes", "Unnerve"), "Swarm", GenderRatio.EVEN, 190, 64, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Thunder Shock"), (1, "String Shot"), (9, "Bug Bite"), (17, "Spark"), (25, "Signal Beam")), (_lvl("Galvantula", 36),), "It clings to bigger creatures and drains static electricity from their fur.")
_add("Galvantula", Type.BUG, Type.ELECTRIC, StatBlock(70, 77, 60, 97, 60, 108), ("Compound Eyes", "Unnerve"), "Swarm", GenderRatio.EVEN, 75, 165, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Thunder Shock"), (1, "String Shot"), (1, "Bug Bite"), (17, "Spark"), (25, "Signal Beam"), (33, "Discharge"), (41, "X-Scissor")),
     (), "It spins electrified webs across trails to snare and shock its prey.")

# ======================================================================
# Gym 4 -- Poison -- Orin (Mossvale)
# ======================================================================
_add("Spinarak", Type.BUG, Type.POISON, StatBlock(40, 60, 40, 40, 40, 30), ("Swarm", "Insomnia"), "Sniper", GenderRatio.EVEN, 255, 58, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Poison Sting"), (1, "String Shot"), (9, "Bug Bite"), (17, "Leech Life")), (_lvl("Ariados", 22),), "It spins a web across a trail and waits, unmoving, for hours at a time.")
_add("Ariados", Type.BUG, Type.POISON, StatBlock(70, 90, 70, 60, 70, 40), ("Swarm", "Insomnia"), "Sniper", GenderRatio.EVEN, 90, 140, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Poison Sting"), (1, "String Shot"), (1, "Bug Bite"), (17, "Leech Life"), (27, "Poison Jab"), (35, "X-Scissor")),
     (), "It has four extra eyes on its abdomen, watching for any sign of prey.")

_add("Koffing", Type.POISON, None, StatBlock(40, 65, 95, 60, 45, 35), ("Levitate",), "Stench", GenderRatio.EVEN, 190, 68, {Stat.DEFENSE: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Smog"), (9, "Sludge"), (17, "Acid"), (25, "Sludge Bomb")), (_lvl("Weezing", 35),), "Full of toxic gas, it will explode without warning if exposed to a flame.")
_add("Weezing", Type.POISON, None, StatBlock(65, 90, 120, 85, 70, 60), ("Levitate",), "Stench", GenderRatio.EVEN, 60, 172, {Stat.DEFENSE: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Smog"), (1, "Sludge"), (17, "Acid"), (25, "Sludge Bomb"), (37, "Gunk Shot")),
     (), "Two gas bags fused together; the poisonous gases inside never mix.")

_add("Croagunk", Type.POISON, Type.FIGHTING, StatBlock(48, 61, 40, 61, 40, 50), ("Anticipation", "Dry Skin"), "Poison Touch", GenderRatio.MOSTLY_MALE, 140, 65, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Poison Sting"), (1, "Astonish"), (9, "Rock Smash"), (17, "Poison Jab"), (25, "Brick Break")), (_lvl("Toxicroak", 37),), "The poison sacs on its cheeks swell ominously right before it strikes.")
_add("Toxicroak", Type.POISON, Type.FIGHTING, StatBlock(83, 106, 65, 86, 65, 85), ("Anticipation", "Dry Skin"), "Poison Touch", GenderRatio.MOSTLY_MALE, 75, 172, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Poison Sting"), (1, "Astonish"), (1, "Rock Smash"), (17, "Poison Jab"), (25, "Brick Break"), (37, "Close Combat"), (45, "Gunk Shot")),
     (), "The poison-filled sac on its throat lets it deliver a debilitating jab.")

# ======================================================================
# Gym 5 -- Ghost -- Priscilla (Duskmere)
# ======================================================================
_add("Misdreavus", Type.GHOST, None, StatBlock(60, 60, 60, 85, 85, 85), ("Levitate",), "Levitate", GenderRatio.EVEN, 45, 87, {Stat.SP_DEF: 1}, GrowthRate.FAST,
     ((1, "Growl"), (1, "Astonish"), (9, "Confuse Ray"), (17, "Lick"), (25, "Shadow Ball")), (_item("Mismagius", "Dusk Stone"),), "It loves to startle people with a creepy, sobbing cry in the dead of night.")
_add("Mismagius", Type.GHOST, None, StatBlock(60, 60, 60, 105, 105, 105), ("Levitate",), "Levitate", GenderRatio.EVEN, 45, 173, {Stat.SP_ATK: 2}, GrowthRate.FAST,
     ((1, "Growl"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Lick"), (25, "Shadow Ball"), (33, "Dark Pulse")),
     (), "Its eerie chanting is said to summon good fortune, if it likes the listener.")

_add("Duskull", Type.GHOST, None, StatBlock(20, 40, 90, 30, 90, 25), ("Levitate",), "Frisk", GenderRatio.EVEN, 190, 59, {Stat.DEFENSE: 1}, GrowthRate.FAST,
     ((1, "Leer"), (1, "Astonish"), (9, "Confuse Ray"), (17, "Shadow Punch"), (25, "Hex")), (_lvl("Dusclops", 37),), "It is said to lead lost children home -- or somewhere else entirely.")
_add("Dusclops", Type.GHOST, None, StatBlock(40, 70, 130, 60, 130, 25), ("Pressure",), "Frisk", GenderRatio.EVEN, 90, 149, {Stat.DEFENSE: 2}, GrowthRate.FAST,
     ((1, "Leer"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Shadow Punch"), (25, "Hex"), (37, "Shadow Ball")), (_item("Dusknoir", "Reaper Cloth"),), "Anything that peers into the black hole in its body is said to never return.")
_add("Dusknoir", Type.GHOST, None, StatBlock(45, 100, 135, 65, 135, 45), ("Pressure",), "Frisk", GenderRatio.EVEN, 45, 236, {Stat.DEFENSE: 3}, GrowthRate.FAST,
     ((1, "Leer"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Shadow Punch"), (25, "Hex"), (37, "Shadow Ball"), (45, "Ice Punch")),
     (), "It receives signals from an unknown realm on the antenna sprouting from its head.")

_add("Snorunt", Type.ICE, None, StatBlock(50, 50, 50, 50, 50, 50), ("Inner Focus",), "Moody", GenderRatio.EVEN, 190, 60, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Powder Snow"), (1, "Leer"), (9, "Icy Wind"), (17, "Confuse Ray")), (_item("Froslass", "Dawn Stone"),), "Legend says a village prospers if one lives near it, so long as it isn't teased.")
_add("Froslass", Type.ICE, Type.GHOST, StatBlock(70, 80, 70, 80, 70, 110), ("Snow Cloak",), "Cursed Body", GenderRatio.ALWAYS_FEMALE, 75, 168, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Powder Snow"), (1, "Leer"), (1, "Icy Wind"), (17, "Confuse Ray"), (25, "Ice Beam"), (33, "Shadow Ball")),
     (), "Legend holds it was once a woman lost in a blizzard, now frozen and forever chilling passersby.")

# ======================================================================
# Gym 6 -- Ice -- Kade (Frostholm)
# ======================================================================
_add("Sneasel", Type.DARK, Type.ICE, StatBlock(55, 95, 55, 35, 75, 115), ("Inner Focus", "Keen Eye"), "Pickpocket", GenderRatio.MOSTLY_MALE, 60, 114, {Stat.SPEED: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Icy Wind"), (17, "Bite"), (25, "Ice Punch")), (_item("Weavile", "Razor Claw", note="Levels up holding Razor Claw at night in the real games; simplified to a direct item use here."),), "It shreds fruit into ribbons with its claws just to sharpen them for battle.")
_add("Weavile", Type.DARK, Type.ICE, StatBlock(70, 120, 65, 45, 85, 125), ("Pressure",), "Pickpocket", GenderRatio.MOSTLY_MALE, 45, 179, {Stat.SPEED: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Icy Wind"), (17, "Bite"), (25, "Ice Punch"), (37, "Night Slash"), (45, "Dark Pulse")),
     (), "It works with others in a pack to corner prey, then finishes the job with sharp claws.")

_add("Vanillite", Type.ICE, None, StatBlock(36, 50, 50, 65, 60, 44), ("Ice Body", "Snow Cloak"), "Weak Armor", GenderRatio.EVEN, 255, 61, {Stat.SP_ATK: 1}, GrowthRate.SLOW,
     ((1, "Icy Wind"), (1, "Growl"), (9, "Avalanche"), (17, "Ice Punch")), (_lvl("Vanillish", 35),), "Born from snow clouds, it is said to have first appeared during a bitter winter.")
_add("Vanillish", Type.ICE, None, StatBlock(51, 65, 65, 80, 75, 59), ("Ice Body", "Snow Cloak"), "Weak Armor", GenderRatio.EVEN, 120, 138, {Stat.SP_ATK: 2}, GrowthRate.SLOW,
     ((1, "Icy Wind"), (1, "Growl"), (1, "Avalanche"), (17, "Ice Punch"), (27, "Blizzard")), (_lvl("Vanilluxe", 47),), "Twin faces glare from its body of pure hardened snow and ice crystal.")
_add("Vanilluxe", Type.ICE, None, StatBlock(71, 95, 85, 110, 95, 79), ("Ice Body", "Snow Cloak"), "Weak Armor", GenderRatio.EVEN, 45, 241, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Icy Wind"), (1, "Growl"), (1, "Avalanche"), (17, "Ice Punch"), (27, "Blizzard"), (41, "Ice Beam")),
     (), "Made of two Vanillish that fused together; the cold front where they meet spawns snow clouds.")

_add("Snover", Type.GRASS, Type.ICE, StatBlock(60, 62, 50, 62, 60, 40), ("Snow Warning",), "Soundproof", GenderRatio.EVEN, 120, 67, {Stat.SP_ATK: 1}, GrowthRate.SLOW,
     ((1, "Powder Snow"), (1, "Leer"), (9, "Icy Wind"), (17, "Razor Leaf")), (_lvl("Abomasnow", 40),), "It appears in legends as a snowy mountain guardian, dropping down to villages in winter.")
_add("Abomasnow", Type.GRASS, Type.ICE, StatBlock(90, 92, 75, 92, 85, 60), ("Snow Warning",), "Soundproof", GenderRatio.EVEN, 60, 173, {Stat.SP_ATK: 2}, GrowthRate.SLOW,
     ((1, "Powder Snow"), (1, "Leer"), (1, "Icy Wind"), (17, "Razor Leaf"), (27, "Ice Punch"), (37, "Blizzard")),
     (), "It whips up fierce blizzards by shaking its whole body, burying travelers in snow.")

# ======================================================================
# Gym 7 -- Ground/Rock -- Garrick (Terracalda)
# ======================================================================
_add("Geodude", Type.ROCK, Type.GROUND, StatBlock(40, 80, 100, 30, 30, 20), ("Rock Head", "Sturdy"), "Sand Veil", GenderRatio.EVEN, 255, 60, {Stat.DEFENSE: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Defense Curl"), (9, "Rock Throw"), (17, "Mud Slap"), (25, "Rock Tomb")), (_lvl("Graveler", 25),), "Found in mountains and vacant lots, it is often mistaken for a plain round rock.")
_add("Graveler", Type.ROCK, Type.GROUND, StatBlock(55, 95, 115, 45, 45, 35), ("Rock Head", "Sturdy"), "Sand Veil", GenderRatio.EVEN, 120, 137, {Stat.DEFENSE: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Defense Curl"), (1, "Rock Throw"), (17, "Mud Slap"), (25, "Rock Tomb"), (33, "Rock Slide")),
     (_lvl("Golem", 32, ), ), "It loves to roll down hills and mountainsides, crushing anything in its path.")
_add("Golem", Type.ROCK, Type.GROUND, StatBlock(80, 120, 130, 55, 65, 45), ("Rock Head", "Sturdy"), "Sand Veil", GenderRatio.EVEN, 45, 223, {Stat.DEFENSE: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Defense Curl"), (1, "Rock Throw"), (17, "Mud Slap"), (25, "Rock Tomb"), (33, "Rock Slide"), (45, "Earthquake")),
     (), "Once it sheds its skin annually, its new shell is even harder than before.")

_add("Drilbur", Type.GROUND, None, StatBlock(60, 85, 40, 30, 45, 68), ("Sand Rush", "Sand Force"), "Mold Breaker", GenderRatio.EVEN, 255, 74, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Mud Slap"), (9, "Rock Smash"), (17, "Dig"), (25, "Metal Claw")), (_lvl("Excadrill", 31),), "Its claws can dig through even solid rock, tunneling at speeds over 90 mph.")
_add("Excadrill", Type.GROUND, Type.STEEL, StatBlock(110, 135, 60, 50, 65, 88), ("Sand Rush", "Sand Force"), "Mold Breaker", GenderRatio.EVEN, 60, 178, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Mud Slap"), (1, "Rock Smash"), (17, "Dig"), (25, "Metal Claw"), (37, "Iron Head"), (45, "Earthquake")),
     (), "It can dig through the earth at speeds rivaling a jet, drilling with its steel claws.")

_add("Rhyhorn", Type.GROUND, Type.ROCK, StatBlock(80, 85, 95, 30, 30, 25), ("Lightning Rod", "Rock Head"), "Reckless", GenderRatio.MOSTLY_MALE, 120, 69, {Stat.DEFENSE: 1}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Stomp"), (9, "Rock Throw"), (17, "Mud Slap"), (25, "Bulldoze")), (_lvl("Rhydon", 42),), "Its massive bones are a thousand times harder than a human's, so it never worries about injury.")
_add("Rhydon", Type.GROUND, Type.ROCK, StatBlock(105, 130, 120, 45, 45, 40), ("Lightning Rod", "Rock Head"), "Reckless", GenderRatio.MOSTLY_MALE, 60, 170, {Stat.DEFENSE: 2}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Stomp"), (1, "Rock Throw"), (17, "Mud Slap"), (25, "Bulldoze"), (37, "Megahorn"), (45, "Earthquake")),
     (_item("Rhyperior", "Protector", note="Trades holding Protector in the real games; converted to a direct item use here."),), "Standing on hind legs, it can demolish a house with one swing of its tail.")
_add("Rhyperior", Type.GROUND, Type.ROCK, StatBlock(115, 140, 130, 55, 55, 40), ("Lightning Rod", "Rock Head"), "Reckless", GenderRatio.MOSTLY_MALE, 30, 240, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Stomp"), (1, "Rock Throw"), (17, "Mud Slap"), (25, "Bulldoze"), (37, "Megahorn"), (45, "Earthquake"), (50, "Rock Slide")),
     (), "Its forearms house rocket-like launchers that fling geode shells at prey.")

# ======================================================================
# Gym 8 -- Dragon -- Serath (Skyreach Summit)
# ======================================================================
_add("Druddigon", Type.DRAGON, None, StatBlock(77, 120, 90, 60, 90, 48), ("Rough Skin", "Sheer Force"), "Mold Breaker", GenderRatio.EVEN, 45, 170, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Scratch"), (1, "Leer"), (9, "Bite"), (17, "Dragon Claw"), (25, "Crunch"), (33, "Superpower")),
     (), "A solitary cave dweller, it hoards treasure and guards its territory ferociously.")

_add("Trapinch", Type.GROUND, None, StatBlock(45, 100, 45, 45, 45, 10), ("Hyper Cutter", "Arena Trap"), "Sheer Force", GenderRatio.EVEN, 255, 58, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Bite"), (1, "Sand Attack"), (9, "Mud Slap"), (17, "Dig")), (_lvl("Vibrava", 35),), "It builds a nest shaped like a funnel of sand and waits at the bottom for prey to slip in.")
_add("Vibrava", Type.GROUND, Type.DRAGON, StatBlock(50, 70, 50, 50, 50, 70), ("Levitate",), "Levitate", GenderRatio.EVEN, 120, 119, {Stat.SPEED: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Bite"), (1, "Sand Attack"), (1, "Mud Slap"), (17, "Dig"), (25, "Dragon Breath")), (_lvl("Flygon", 45),), "Its wings beat at a frequency that generates an eerie, ultrasonic drone.")
_add("Flygon", Type.GROUND, Type.DRAGON, StatBlock(80, 100, 80, 80, 80, 100), ("Levitate",), "Levitate", GenderRatio.EVEN, 45, 234, {Stat.SPEED: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Bite"), (1, "Sand Attack"), (1, "Mud Slap"), (17, "Dig"), (25, "Dragon Breath"), (37, "Dragon Claw"), (45, "Earthquake")),
     (), "Called the Desert Spirit, it kicks up sandstorms with its wings as it flies.")

_add("Gible", Type.DRAGON, Type.GROUND, StatBlock(58, 70, 45, 40, 45, 42), ("Sand Veil",), "Rough Skin", GenderRatio.EVEN, 45, 60, {Stat.ATTACK: 1}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Sand Attack"), (9, "Dragon Breath"), (17, "Dig")), (_lvl("Gabite", 24),), "It lives in caves, digging tunnels that snake through the underground for miles.")
_add("Gabite", Type.DRAGON, Type.GROUND, StatBlock(68, 90, 65, 50, 55, 82), ("Sand Veil",), "Rough Skin", GenderRatio.EVEN, 45, 144, {Stat.ATTACK: 2}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Sand Attack"), (1, "Dragon Breath"), (17, "Dig"), (27, "Dragon Claw")), (_lvl("Garchomp", 48),), "It collects glittering minerals and gems, hoarding them deep in its cave.")
_add("Garchomp", Type.DRAGON, Type.GROUND, StatBlock(108, 130, 95, 80, 85, 102), ("Sand Veil",), "Rough Skin", GenderRatio.EVEN, 45, 270, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Sand Attack"), (1, "Dragon Breath"), (17, "Dig"), (27, "Dragon Claw"), (43, "Dragon Dance"), (49, "Earthquake")),
     (), "Said to be able to fly faster than a jet plane despite its enormous, armored bulk.")

# ======================================================================
# Elite Four #1 -- Fire -- Ivor
# ======================================================================
_add("Vulpix", Type.FIRE, None, StatBlock(38, 41, 40, 50, 65, 65), ("Flash Fire",), "Drought", GenderRatio.MOSTLY_FEMALE, 190, 60, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Ember"), (1, "Tail Whip"), (9, "Will-O-Wisp"), (17, "Flame Wheel")), (_item("Ninetales", "Fire Stone"),), "Legend says a fox is born with one tail that splits into more as it ages and grows in power.")
_add("Ninetales", Type.FIRE, None, StatBlock(73, 76, 75, 81, 100, 100), ("Flash Fire",), "Drought", GenderRatio.MOSTLY_FEMALE, 75, 178, {Stat.SP_DEF: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Ember"), (1, "Tail Whip"), (1, "Will-O-Wisp"), (17, "Flame Wheel"), (27, "Fire Blast"), (37, "Extreme Speed")),
     (), "Each of its nine tails is said to hold a mystical power of its own.")

_add("Cyndaquil", Type.FIRE, None, StatBlock(39, 52, 43, 60, 50, 65), ("Blaze",), "Flash Fire", GenderRatio.MOSTLY_MALE, 45, 62, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (9, "Ember"), (17, "Quick Attack"), (25, "Flame Wheel")), (_lvl("Quilava", 14),), "Flames burst from its back when it is angry or startled, driving off predators.")
_add("Quilava", Type.FIRE, None, StatBlock(58, 64, 58, 80, 65, 80), ("Blaze",), "Flash Fire", GenderRatio.MOSTLY_MALE, 45, 146, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Ember"), (17, "Quick Attack"), (25, "Flame Wheel"), (33, "Flamethrower")), (_lvl("Typhlosion", 36),), "It shrugs off any attack thanks to a coat of fur that flares up under stress.")
_add("Typhlosion", Type.FIRE, None, StatBlock(78, 84, 78, 109, 85, 100), ("Blaze",), "Flash Fire", GenderRatio.MOSTLY_MALE, 45, 240, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Ember"), (17, "Quick Attack"), (25, "Flame Wheel"), (33, "Flamethrower"), (45, "Fire Blast")),
     (), "It hides its face with flame so opponents can't read its next move.")

_add("Chimchar", Type.FIRE, None, StatBlock(44, 58, 44, 58, 44, 61), ("Blaze",), "Iron Fist", GenderRatio.MOSTLY_MALE, 45, 62, {Stat.SPEED: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Ember"), (17, "Mach Punch"), (25, "Flame Wheel")), (_lvl("Monferno", 14),), "The flame on its tail burns from birth and is said to reveal its mood.")
_add("Monferno", Type.FIRE, Type.FIGHTING, StatBlock(64, 78, 52, 78, 52, 81), ("Blaze",), "Iron Fist", GenderRatio.MOSTLY_MALE, 45, 148, {Stat.SPEED: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Ember"), (17, "Mach Punch"), (25, "Flame Wheel"), (33, "Fire Punch")), (_lvl("Infernape", 36),), "It fights with acrobatic flair, using its tail flame to keep foes at bay.")
_add("Infernape", Type.FIRE, Type.FIGHTING, StatBlock(76, 104, 71, 104, 71, 108), ("Blaze",), "Iron Fist", GenderRatio.MOSTLY_MALE, 45, 240, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Ember"), (17, "Mach Punch"), (25, "Flame Wheel"), (33, "Fire Punch"), (45, "Close Combat")),
     (), "Its blazing crown of fire is said to be a symbol of pride among its kind.")

_add("Litwick", Type.GHOST, Type.FIRE, StatBlock(50, 30, 55, 65, 55, 20), ("Flash Fire", "Flame Body"), "Infiltrator", GenderRatio.EVEN, 190, 62, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Ember"), (1, "Astonish"), (9, "Confuse Ray"), (17, "Will-O-Wisp"), (25, "Shadow Ball")), (_lvl("Lampent", 41),), "It absorbs the lifespan of anyone whose path it lights with its flame.")
_add("Lampent", Type.GHOST, Type.FIRE, StatBlock(60, 40, 60, 95, 60, 55), ("Flash Fire", "Flame Body"), "Infiltrator", GenderRatio.EVEN, 90, 151, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Ember"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Will-O-Wisp"), (25, "Shadow Ball"), (33, "Flame Wheel")), (_item("Chandelure", "Dusk Stone"),), "It lingers around hospitals, waiting to guide departing souls with its lantern.")
_add("Chandelure", Type.GHOST, Type.FIRE, StatBlock(60, 55, 90, 145, 90, 80), ("Flash Fire", "Flame Body"), "Infiltrator", GenderRatio.EVEN, 45, 234, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Ember"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Will-O-Wisp"), (25, "Shadow Ball"), (33, "Flame Wheel"), (45, "Fire Blast")),
     (), "Its eerie flame is said to burn brightest around those with the longest lives left to take.")

# ======================================================================
# Elite Four #2 -- Water -- Maren
# ======================================================================
_add("Totodile", Type.WATER, None, StatBlock(50, 65, 64, 44, 48, 43), ("Torrent",), "Sheer Force", GenderRatio.MOSTLY_MALE, 45, 63, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Water Gun"), (17, "Bite"), (25, "Aqua Tail")), (_lvl("Croconaw", 18),), "Compact and sturdy, it snaps ferociously at anything with its powerful jaws.")
_add("Croconaw", Type.WATER, None, StatBlock(65, 80, 80, 59, 63, 58), ("Torrent",), "Sheer Force", GenderRatio.MOSTLY_MALE, 45, 148, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Water Gun"), (17, "Bite"), (25, "Aqua Tail"), (33, "Ice Punch")), (_lvl("Feraligatr", 30),), "Sharply pointed scales on its back and jaw mark it as a fearsome fighter.")
_add("Feraligatr", Type.WATER, None, StatBlock(85, 105, 100, 79, 83, 78), ("Torrent",), "Sheer Force", GenderRatio.MOSTLY_MALE, 45, 239, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Water Gun"), (17, "Bite"), (25, "Aqua Tail"), (33, "Ice Punch"), (45, "Hydro Pump")),
     (), "It intimidates rivals by opening its huge jaws wide, then charges with a fierce bellow.")

_add("Mudkip", Type.WATER, None, StatBlock(50, 70, 50, 50, 50, 40), ("Torrent",), "Damp", GenderRatio.MOSTLY_MALE, 45, 62, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (9, "Water Gun"), (17, "Mud Slap"), (25, "Bulldoze")), (_lvl("Marshtomp", 16),), "The fin on its head detects tiny vibrations in water and in the air alike.")
_add("Marshtomp", Type.WATER, Type.GROUND, StatBlock(70, 85, 70, 60, 70, 50), ("Torrent",), "Damp", GenderRatio.MOSTLY_MALE, 45, 143, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Water Gun"), (17, "Mud Slap"), (25, "Bulldoze"), (33, "Brine")), (_lvl("Swampert", 36),), "Able to move freely in both water and mud, it far outpaces others on rainy days.")
_add("Swampert", Type.WATER, Type.GROUND, StatBlock(100, 110, 90, 85, 90, 60), ("Torrent",), "Damp", GenderRatio.MOSTLY_MALE, 45, 241, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Water Gun"), (17, "Mud Slap"), (25, "Bulldoze"), (33, "Brine"), (45, "Earthquake")),
     (), "Its powerful arms can crush a boulder to gravel, and it senses storms coming from far away.")

_add("Piplup", Type.WATER, None, StatBlock(53, 51, 53, 61, 56, 40), ("Torrent",), "Competitive", GenderRatio.MOSTLY_MALE, 45, 63, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (9, "Water Gun"), (17, "Bubble Beam"), (25, "Metal Claw")), (_lvl("Prinplup", 16),), "Proud and a little stubborn, it dislikes taking food from anyone's hand.")
_add("Prinplup", Type.WATER, None, StatBlock(64, 66, 68, 81, 76, 50), ("Torrent",), "Competitive", GenderRatio.MOSTLY_MALE, 45, 151, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (1, "Water Gun"), (17, "Bubble Beam"), (25, "Metal Claw"), (33, "Aqua Jet")), (_lvl("Empoleon", 36),), "Fiercely territorial, it drives off any rival that dares enter its domain.")
_add("Empoleon", Type.WATER, Type.STEEL, StatBlock(84, 86, 88, 111, 101, 60), ("Torrent",), "Competitive", GenderRatio.MOSTLY_MALE, 45, 239, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (1, "Water Gun"), (17, "Bubble Beam"), (25, "Metal Claw"), (33, "Aqua Jet"), (45, "Hydro Pump")),
     (), "Its trident-shaped crest can slice through drift ice with ease.")

_add("Horsea", Type.WATER, None, StatBlock(30, 40, 70, 70, 25, 60), ("Swift Swim", "Sniper"), "Damp", GenderRatio.EVEN, 225, 59, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Bubble"), (1, "Water Gun"), (9, "Water Pulse"), (17, "Twister")), (_lvl("Seadra", 32),), "It can shoot down flying insects with a jet of ink from a distance of six feet.")
_add("Seadra", Type.WATER, None, StatBlock(55, 65, 95, 95, 45, 85), ("Swift Swim", "Sniper"), "Damp", GenderRatio.EVEN, 75, 154, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Bubble"), (1, "Water Gun"), (1, "Water Pulse"), (17, "Twister"), (27, "Brine")), (_item("Kingdra", "Dragon Scale", note="Trades holding Dragon Scale in the real games; converted to a direct item use here."),), "Its dorsal fins pulse rhythmically to pump a nerve toxin into its bloodstream.")
_add("Kingdra", Type.WATER, Type.DRAGON, StatBlock(75, 95, 95, 95, 95, 85), ("Swift Swim", "Sniper"), "Damp", GenderRatio.EVEN, 45, 243, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_FAST,
     ((1, "Bubble"), (1, "Water Gun"), (1, "Water Pulse"), (17, "Twister"), (27, "Brine"), (37, "Dragon Pulse"), (45, "Hydro Pump")),
     (), "Said to sleep on the sea floor, stirring only to whip up devastating whirlpools.")

# ======================================================================
# Elite Four #3 -- Flying/Psychic -- Zephyra
# ======================================================================
_add("Hoothoot", Type.NORMAL, Type.FLYING, StatBlock(60, 30, 30, 36, 56, 50), ("Insomnia", "Keen Eye"), "Tinted Lens", GenderRatio.EVEN, 255, 52, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Peck"), (1, "Growl"), (9, "Hypnosis"), (17, "Confusion")), (_lvl("Noctowl", 20),), "It stands on one leg for hours, watching prey while barely moving.")
_add("Noctowl", Type.NORMAL, Type.FLYING, StatBlock(100, 50, 50, 76, 96, 70), ("Insomnia", "Keen Eye"), "Tinted Lens", GenderRatio.EVEN, 90, 158, {Stat.SP_DEF: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Peck"), (1, "Growl"), (1, "Hypnosis"), (17, "Confusion"), (27, "Air Slash"), (35, "Psychic")),
     (), "Its eyes take in and store any available light, letting it see perfectly in darkness.")

_add("Swablu", Type.NORMAL, Type.FLYING, StatBlock(45, 40, 60, 40, 75, 50), ("Natural Cure",), "Cloud Nine", GenderRatio.EVEN, 255, 62, {Stat.SP_DEF: 1}, GrowthRate.SLOW,
     ((1, "Peck"), (1, "Growl"), (9, "Astonish"), (17, "Aerial Ace")), (_lvl("Altaria", 35),), "Its cotton-soft wings are so downy that other Pokemon use them as pillows.")
_add("Altaria", Type.DRAGON, Type.FLYING, StatBlock(75, 70, 90, 70, 105, 80), ("Natural Cure",), "Cloud Nine", GenderRatio.EVEN, 45, 172, {Stat.SP_DEF: 2}, GrowthRate.SLOW,
     ((1, "Peck"), (1, "Growl"), (1, "Astonish"), (17, "Aerial Ace"), (27, "Dragon Breath"), (37, "Dragon Pulse")),
     (), "Its singing voice is said to be so beautiful that it's often mistaken for an angel's.")

_add("Ralts", Type.PSYCHIC, None, StatBlock(28, 25, 25, 45, 35, 40), ("Synchronize", "Trace"), "Telepathy", GenderRatio.EVEN, 235, 40, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Growl"), (1, "Confusion"), (9, "Double Team"), (17, "Psybeam")), (_lvl("Kirlia", 20),), "It emerges only in quiet, peaceful places, drawn there by calm emotions.")
_add("Kirlia", Type.PSYCHIC, None, StatBlock(38, 35, 35, 65, 55, 50), ("Synchronize", "Trace"), "Telepathy", GenderRatio.EVEN, 120, 97, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Growl"), (1, "Confusion"), (1, "Double Team"), (17, "Psybeam"), (27, "Calm Mind")), (_lvl("Gardevoir", 30),), "It can sense the emotions of people nearby and will dance to lift their spirits.")
_add("Gardevoir", Type.PSYCHIC, None, StatBlock(68, 65, 65, 125, 115, 80), ("Synchronize", "Trace"), "Telepathy", GenderRatio.EVEN, 45, 233, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Growl"), (1, "Confusion"), (1, "Double Team"), (17, "Psybeam"), (27, "Calm Mind"), (37, "Psychic"), (45, "Shadow Ball")),
     (), "It will put itself between its Trainer and danger without a moment's hesitation.")

_add("Togepi", Type.NORMAL, None, StatBlock(35, 20, 65, 40, 65, 20), ("Hustle", "Serene Grace"), "Super Luck", GenderRatio.EVEN, 45, 49, {Stat.SP_DEF: 1}, GrowthRate.FAST,
     ((1, "Growl"), (1, "Charm"), (9, "Sing"), (17, "Ancient Power")), (_lvl("Togetic", 20, ), ), "Its shell is said to be packed with joy; being kind to it brings good luck.")
_add("Togetic", Type.NORMAL, Type.FLYING, StatBlock(55, 40, 85, 80, 105, 40), ("Hustle", "Serene Grace"), "Super Luck", GenderRatio.EVEN, 45, 142, {Stat.SP_DEF: 2}, GrowthRate.FAST,
     ((1, "Growl"), (1, "Charm"), (1, "Sing"), (17, "Ancient Power"), (27, "Air Slash")), (_item("Togekiss", "Shiny Stone"),), "It only appears before kindhearted people, showering them with happiness.")
_add("Togekiss", Type.NORMAL, Type.FLYING, StatBlock(85, 50, 95, 120, 115, 80), ("Hustle", "Serene Grace"), "Super Luck", GenderRatio.EVEN, 45, 245, {Stat.SP_ATK: 3}, GrowthRate.FAST,
     ((1, "Growl"), (1, "Charm"), (1, "Sing"), (17, "Ancient Power"), (27, "Air Slash"), (37, "Extreme Speed"), (45, "Air Slash")),
     (), "A legendary bringer of blessings, it is said to visit only the truly gentle of heart.")

# ======================================================================
# Elite Four #4 -- Dark/Dragon -- Draven
# ======================================================================
_add("Absol", Type.DARK, None, StatBlock(65, 130, 60, 75, 60, 75), ("Pressure", "Super Luck"), "Justified", GenderRatio.EVEN, 30, 163, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Bite"), (17, "Slash"), (25, "Night Slash"), (33, "Swords Dance")),
     (), "Its appearance is a fabled omen of coming disasters, though it only means to warn people of danger.")

_add("Houndour", Type.DARK, Type.FIRE, StatBlock(45, 60, 30, 80, 50, 65), ("Early Bird", "Flash Fire"), "Unnerve", GenderRatio.EVEN, 120, 66, {Stat.SP_ATK: 1}, GrowthRate.SLOW,
     ((1, "Leer"), (1, "Ember"), (9, "Bite"), (17, "Will-O-Wisp")), (_lvl("Houndoom", 24),), "It hunts in packs, communicating through eerie howls that echo for miles.")
_add("Houndoom", Type.DARK, Type.FIRE, StatBlock(75, 90, 50, 110, 80, 95), ("Early Bird", "Flash Fire"), "Unnerve", GenderRatio.EVEN, 45, 175, {Stat.SP_ATK: 2}, GrowthRate.SLOW,
     ((1, "Leer"), (1, "Ember"), (1, "Bite"), (17, "Will-O-Wisp"), (27, "Crunch"), (37, "Fire Blast")),
     (), "Its ominous howl is said to be a portent of death in some region's folklore.")

_add("Deino", Type.DARK, Type.DRAGON, StatBlock(52, 65, 50, 45, 50, 38), ("Hustle",), "Hustle", GenderRatio.EVEN, 45, 60, {Stat.ATTACK: 1}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Bite"), (9, "Dragon Breath"), (17, "Dark Pulse")), (_lvl("Zweilous", 50),), "Blind from birth, it thrashes wildly at anything that gets close.")
_add("Zweilous", Type.DARK, Type.DRAGON, StatBlock(72, 85, 70, 65, 70, 58), ("Hustle",), "Hustle", GenderRatio.EVEN, 45, 149, {Stat.ATTACK: 2}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Bite"), (1, "Dragon Breath"), (17, "Dark Pulse"), (27, "Crunch")), (_lvl("Hydreigon", 64),), "Its two heads squabble constantly over food, snapping at each other as often as at foes.")
_add("Hydreigon", Type.DARK, Type.DRAGON, StatBlock(92, 105, 90, 125, 90, 98), ("Levitate",), "Levitate", GenderRatio.EVEN, 45, 270, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Bite"), (1, "Dragon Breath"), (17, "Dark Pulse"), (27, "Crunch"), (41, "Dragon Pulse"), (49, "Draco Meteor")),
     (), "Its two extra heads are said to swallow anything that moves, given the chance.")

_add("Larvitar", Type.ROCK, Type.GROUND, StatBlock(50, 64, 50, 45, 50, 41), ("Guts",), "Sand Veil", GenderRatio.EVEN, 45, 60, {Stat.ATTACK: 1}, GrowthRate.SLOW,
     ((1, "Bite"), (1, "Leer"), (9, "Rock Throw"), (17, "Sand Attack")), (_lvl("Pupitar", 30),), "Born from an egg, it feeds on soil as it slowly grows into the mountains it will one day become.")
_add("Pupitar", Type.ROCK, Type.GROUND, StatBlock(70, 84, 70, 65, 70, 51), ("Shed Skin",), "Shed Skin", GenderRatio.EVEN, 45, 142, {Stat.ATTACK: 2}, GrowthRate.SLOW,
     ((1, "Bite"), (1, "Leer"), (1, "Rock Throw"), (17, "Sand Attack"), (27, "Rock Slide")), (_lvl("Tyranitar", 55),), "Intense energy roiling inside its hard shell is said to reshape the land around it.")
_add("Tyranitar", Type.ROCK, Type.DARK, StatBlock(100, 134, 110, 95, 100, 61), ("Sand Stream",), "Unnerve", GenderRatio.EVEN, 45, 270, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Bite"), (1, "Leer"), (1, "Rock Throw"), (17, "Sand Attack"), (27, "Rock Slide"), (41, "Crunch"), (49, "Stone Edge")),
     (), "So overwhelmingly powerful it can bring down a mountain in search of a place to nest.")

# ======================================================================
# Champion -- Astra
# ======================================================================
_add("Budew", Type.GRASS, Type.POISON, StatBlock(40, 30, 35, 50, 70, 55), ("Natural Cure", "Poison Point"), "Leaf Guard", GenderRatio.EVEN, 255, 56, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Absorb"), (1, "Growl"), (9, "Stun Spore"), (17, "Sleep Powder")), (_lvl("Roselia", 12, ), ), "Petals ringing its head open only when it senses warmth nearby.")
_add("Roselia", Type.GRASS, Type.POISON, StatBlock(50, 60, 45, 100, 80, 65), ("Natural Cure", "Poison Point"), "Leaf Guard", GenderRatio.EVEN, 150, 140, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Absorb"), (1, "Growl"), (1, "Stun Spore"), (17, "Sleep Powder"), (27, "Giga Drain"), (35, "Sludge Bomb")), (_item("Roserade", "Shiny Stone"),), "The aroma of the flowers on its arms grows sweeter the more it battles.")
_add("Roserade", Type.GRASS, Type.POISON, StatBlock(60, 70, 55, 125, 105, 90), ("Natural Cure", "Poison Point"), "Leaf Guard", GenderRatio.EVEN, 75, 232, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Absorb"), (1, "Growl"), (1, "Stun Spore"), (17, "Sleep Powder"), (27, "Giga Drain"), (35, "Sludge Bomb"), (45, "Energy Ball")),
     (), "It conceals a poisonous thorn whip inside each bouquet-like hand.")

_add("Feebas", Type.WATER, None, StatBlock(20, 15, 20, 10, 55, 80), ("Swift Swim", "Oblivious"), "Adaptability", GenderRatio.EVEN, 255, 40, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Tail Whip"), (9, "Water Pulse")), (_item("Milotic", "Prism Scale"),), "Its drab, shabby scales make it an object of ridicule, hiding a beauty yet to bloom.")
_add("Milotic", Type.WATER, None, StatBlock(95, 60, 79, 100, 125, 81), ("Marvel Scale",), "Cute Charm", GenderRatio.EVEN, 60, 189, {Stat.SP_DEF: 3}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Tail Whip"), (1, "Water Pulse"), (17, "Aqua Tail"), (27, "Withdraw"), (37, "Hydro Pump")),
     (), "Said to be the most beautiful of all Pokemon, its serene form is said to calm quarreling hearts.")

_add("Gastly", Type.GHOST, Type.POISON, StatBlock(30, 35, 30, 100, 35, 80), ("Levitate",), "Levitate", GenderRatio.EVEN, 190, 62, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Lick"), (1, "Astonish"), (9, "Confuse Ray"), (17, "Sludge"), (25, "Shadow Ball")), (_lvl("Haunter", 25),), "Almost entirely gaseous, it can slip through even the tiniest gap to envelop a target.")
_add("Haunter", Type.GHOST, Type.POISON, StatBlock(45, 50, 45, 115, 55, 95), ("Levitate",), "Levitate", GenderRatio.EVEN, 90, 142, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Lick"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Sludge"), (25, "Shadow Ball"), (33, "Dark Pulse")),
     (_lvl("Gengar", 38, ), ), "A lick from its gaseous tongue is said to cause endless shuddering.")
_add("Gengar", Type.GHOST, Type.POISON, StatBlock(60, 65, 60, 130, 75, 110), ("Levitate",), "Levitate", GenderRatio.EVEN, 45, 225, {Stat.SP_ATK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Lick"), (1, "Astonish"), (1, "Confuse Ray"), (17, "Sludge"), (25, "Shadow Ball"), (33, "Dark Pulse"), (45, "Sludge Bomb")),
     (), "On the night of a full moon, it is said to mimic shadows and steal one's life force.")

_add("Pawniard", Type.DARK, Type.STEEL, StatBlock(45, 85, 70, 40, 40, 60), ("Defiant", "Inner Focus"), "Pressure", GenderRatio.MOSTLY_MALE, 120, 68, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Metal Claw"), (17, "Night Slash")), (_lvl("Bisharp", 52),), "It hones the blades on its arms against rocks each night before sleeping.")
_add("Bisharp", Type.DARK, Type.STEEL, StatBlock(65, 125, 100, 60, 70, 70), ("Defiant", "Inner Focus"), "Pressure", GenderRatio.MOSTLY_MALE, 45, 172, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (1, "Metal Claw"), (17, "Night Slash"), (27, "Iron Head"), (37, "Crunch"), (45, "Swords Dance")),
     (), "It commands lesser Pawniard as a general leads troops, striking with cold precision.")

_add("Dratini", Type.DRAGON, None, StatBlock(41, 64, 45, 50, 50, 50), ("Shed Skin",), "Marvel Scale", GenderRatio.EVEN, 45, 60, {Stat.ATTACK: 1}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (9, "Dragon Breath"), (17, "Aqua Tail")), (_lvl("Dragonair", 30),), "Long dismissed as a myth, it is said to shed its skin countless times as it grows.")
_add("Dragonair", Type.DRAGON, None, StatBlock(61, 84, 65, 70, 70, 70), ("Shed Skin",), "Marvel Scale", GenderRatio.EVEN, 45, 147, {Stat.ATTACK: 2}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Dragon Breath"), (17, "Aqua Tail"), (27, "Dragon Claw")), (_lvl("Dragonite", 55),), "Crystalline orbs along its body are said to hold the power to control the weather.")
_add("Dragonite", Type.DRAGON, Type.FLYING, StatBlock(91, 134, 95, 100, 100, 80), ("Inner Focus",), "Multiscale", GenderRatio.EVEN, 45, 270, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Dragon Breath"), (17, "Aqua Tail"), (27, "Dragon Claw"), (41, "Dragon Dance"), (49, "Hyper Beam")),
     (), "Despite its tremendous power, it is famously kind and will guide lost sailors safely to shore.")

# ======================================================================
# Team Eclipse
# ======================================================================
_add("Zubat", Type.POISON, Type.FLYING, StatBlock(40, 45, 35, 30, 40, 55), ("Inner Focus",), "Infiltrator", GenderRatio.EVEN, 255, 49, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Leer"), (1, "Supersonic"), (9, "Bite"), (17, "Poison Fang")), (_lvl("Golbat", 22),), "Lacking eyes, it navigates entirely by the echo of its own ultrasonic cries.")
_add("Golbat", Type.POISON, Type.FLYING, StatBlock(75, 80, 70, 65, 75, 90), ("Inner Focus",), "Infiltrator", GenderRatio.EVEN, 90, 159, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Leer"), (1, "Supersonic"), (1, "Bite"), (17, "Poison Fang"), (27, "Air Slash"), (35, "Crunch")),
     (), "So relentlessly hungry that it will drain blood from prey until both can barely fly.")

_add("Poochyena", Type.DARK, None, StatBlock(35, 55, 35, 30, 30, 35), ("Run Away", "Quick Feet"), "Rattled", GenderRatio.EVEN, 255, 56, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (9, "Bite"), (17, "Sand Attack")), (_lvl("Mightyena", 18),), "It travels in a pack, relentlessly stalking prey until it tires out.")
_add("Mightyena", Type.DARK, None, StatBlock(70, 90, 70, 60, 60, 70), ("Intimidate", "Quick Feet"), "Moxie", GenderRatio.EVEN, 127, 179, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Bite"), (17, "Sand Attack"), (27, "Crunch"), (35, "Take Down")),
     (), "It obeys only a Trainer it has judged to be a stronger leader than itself.")

_add("Murkrow", Type.DARK, Type.FLYING, StatBlock(60, 85, 42, 85, 42, 91), ("Insomnia", "Super Luck"), "Prankster", GenderRatio.EVEN, 30, 81, {Stat.SPEED: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Peck"), (1, "Astonish"), (9, "Night Slash"), (17, "Feint Attack")), (_item("Honchkrow", "Dusk Stone"),), "Regarded as a bringer of misfortune, it is drawn to shiny trinkets like a magpie.")
_add("Honchkrow", Type.DARK, Type.FLYING, StatBlock(100, 125, 52, 105, 52, 71), ("Insomnia", "Super Luck"), "Moxie", GenderRatio.EVEN, 30, 177, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Peck"), (1, "Astonish"), (1, "Night Slash"), (17, "Feint Attack"), (27, "Dark Pulse"), (37, "Sucker Punch")),
     (), "It commands a flock of Murkrow as its personal henchmen, never lifting a wing itself until it must.")

_add("Sableye", Type.DARK, Type.GHOST, StatBlock(50, 75, 75, 65, 65, 50), ("Keen Eye", "Stall"), "Prankster", GenderRatio.EVEN, 45, 133, {Stat.DEFENSE: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Scratch"), (1, "Leer"), (9, "Astonish"), (17, "Night Slash"), (27, "Shadow Ball"), (35, "Payback")),
     (), "The gems in its eyes are said to hypnotize anyone who peers into them for too long.")

# ======================================================================
# Wild route filler
# ======================================================================
_add("Rattata", Type.NORMAL, None, StatBlock(30, 56, 35, 25, 35, 72), ("Run Away", "Guts"), "Hustle", GenderRatio.EVEN, 255, 51, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Tail Whip"), (7, "Quick Attack"), (13, "Hyper Fang")), (_lvl("Raticate", 20),), "It gnaws on anything, and its teeth never stop growing throughout its life.")
_add("Raticate", Type.NORMAL, None, StatBlock(55, 81, 60, 50, 70, 97), ("Run Away", "Guts"), "Hustle", GenderRatio.EVEN, 127, 145, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Tail Whip"), (1, "Quick Attack"), (13, "Hyper Fang"), (25, "Double-Edge")),
     (), "It multiplies rapidly, and a large swarm can level an entire field of crops overnight.")

_add("Zigzagoon", Type.NORMAL, None, StatBlock(38, 30, 41, 30, 41, 60), ("Pickup", "Gluttony"), "Quick Feet", GenderRatio.EVEN, 255, 56, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Growl"), (9, "Take Down"), (17, "Sand Attack")), (_lvl("Linoone", 20),), "It zigzags erratically as it runs, making it hard to predict where it's headed.")
_add("Linoone", Type.NORMAL, None, StatBlock(78, 70, 61, 50, 61, 100), ("Pickup", "Gluttony"), "Quick Feet", GenderRatio.EVEN, 90, 158, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Growl"), (1, "Take Down"), (17, "Sand Attack"), (27, "Slash"), (35, "Double-Edge")),
     (), "Once it starts running, it can only go in a straight line, reaching astonishing speed.")

_add("Hoppip", Type.GRASS, Type.FLYING, StatBlock(35, 35, 40, 35, 55, 50), ("Chlorophyll", "Leaf Guard"), "Infiltrator", GenderRatio.EVEN, 255, 50, {Stat.SP_DEF: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (9, "Cotton Spore"), (17, "Stun Spore")), (_lvl("Skiploom", 18),), "So light that it drifts wherever the wind carries it, sometimes very far from home.")
_add("Skiploom", Type.GRASS, Type.FLYING, StatBlock(55, 45, 50, 45, 65, 80), ("Chlorophyll", "Leaf Guard"), "Infiltrator", GenderRatio.EVEN, 120, 119, {Stat.SP_DEF: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Cotton Spore"), (17, "Stun Spore"), (27, "Magical Leaf")), (_lvl("Jumpluff", 27),), "Its round flowers open and close depending on humidity in the surrounding air.")
_add("Jumpluff", Type.GRASS, Type.FLYING, StatBlock(75, 55, 70, 55, 95, 110), ("Chlorophyll", "Leaf Guard"), "Infiltrator", GenderRatio.EVEN, 45, 176, {Stat.SPEED: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Growl"), (1, "Cotton Spore"), (17, "Stun Spore"), (27, "Magical Leaf"), (37, "Giga Drain")),
     (), "It rides the wind currents around the globe, dropping fluff-covered seeds as it goes.")

_add("Taillow", Type.NORMAL, Type.FLYING, StatBlock(40, 55, 30, 30, 30, 85), ("Guts",), "Scrappy", GenderRatio.EVEN, 200, 54, {Stat.SPEED: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Peck"), (1, "Growl"), (9, "Quick Attack"), (17, "Wing Attack")), (_lvl("Swellow", 22),), "Though bold enough to challenge far bigger foes, it retreats the instant it gets hungry.")
_add("Swellow", Type.NORMAL, Type.FLYING, StatBlock(60, 85, 60, 50, 50, 125), ("Guts",), "Scrappy", GenderRatio.EVEN, 45, 174, {Stat.SPEED: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Peck"), (1, "Growl"), (1, "Quick Attack"), (17, "Wing Attack"), (27, "Aerial Ace"), (37, "Brave Bird")),
     (), "It dives at astonishing speed to catch prey, folding its wings back like a jet.")

_add("Whismur", Type.NORMAL, None, StatBlock(64, 51, 23, 51, 23, 28), ("Soundproof",), "Rattled", GenderRatio.EVEN, 190, 48, {Stat.HP: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (9, "Astonish"), (17, "Stomp")), (_lvl("Loudred", 20),), "It cries loudly whenever startled, which unfortunately means it's often startled by its own cries.")
_add("Loudred", Type.NORMAL, None, StatBlock(84, 71, 43, 71, 43, 48), ("Soundproof",), "Scrappy", GenderRatio.EVEN, 120, 126, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (1, "Astonish"), (17, "Stomp"), (27, "Hyper Voice")), (_lvl("Exploud", 40),), "Its booming voice can shatter windows a block away when it really lets loose.")
_add("Exploud", Type.NORMAL, None, StatBlock(104, 91, 63, 91, 73, 68), ("Soundproof",), "Scrappy", GenderRatio.EVEN, 45, 221, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Growl"), (1, "Astonish"), (17, "Stomp"), (27, "Hyper Voice"), (37, "Take Down"), (45, "Double-Edge")),
     (), "The many holes across its body resonate together to produce a deafening roar.")

_add("Woobat", Type.PSYCHIC, Type.FLYING, StatBlock(65, 45, 43, 55, 43, 72), ("Unaware", "Klutz"), "Simple", GenderRatio.EVEN, 190, 60, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Confusion"), (1, "Astonish"), (9, "Air Slash"), (17, "Psybeam")), (_lvl("Swoobat", 30, ), ), "It sticks to cave walls with its heart-shaped nose, only letting go to swoop at prey.")
_add("Swoobat", Type.PSYCHIC, Type.FLYING, StatBlock(67, 57, 55, 77, 55, 114), ("Unaware", "Klutz"), "Simple", GenderRatio.EVEN, 45, 149, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Confusion"), (1, "Astonish"), (1, "Air Slash"), (17, "Psybeam"), (27, "Amnesia"), (35, "Psychic")),
     (), "It releases ultrasonic waves from its nose that can addle the mind of anyone nearby.")

_add("Magikarp", Type.WATER, None, StatBlock(20, 10, 55, 15, 20, 80), ("Swift Swim",), "Rattled", GenderRatio.EVEN, 255, 40, {Stat.SPEED: 1}, GrowthRate.SLOW,
     ((1, "Tackle"),), (_lvl("Gyarados", 20),), "Nearly useless in a fight, it is famous for flopping about and doing little else.")
_add("Gyarados", Type.WATER, Type.FLYING, StatBlock(95, 125, 79, 60, 100, 81), ("Intimidate",), "Moxie", GenderRatio.EVEN, 45, 189, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Bite"), (1, "Dragon Breath"), (20, "Aqua Tail"), (30, "Crunch"), (40, "Hydro Pump")),
     (), "Once it evolves, its temperament flips entirely, becoming ferociously violent and destructive.")

_add("Wingull", Type.WATER, Type.FLYING, StatBlock(40, 30, 30, 55, 30, 85), ("Keen Eye", "Hydration"), "Rain Dish", GenderRatio.EVEN, 190, 54, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Growl"), (1, "Water Gun"), (9, "Wing Attack"), (17, "Water Pulse")), (_lvl("Pelipper", 25),), "It rides updrafts along cliffs and rarely flaps its wings while gliding for hours.")
_add("Pelipper", Type.WATER, Type.FLYING, StatBlock(60, 50, 100, 85, 70, 65), ("Keen Eye", "Hydration"), "Rain Dish", GenderRatio.EVEN, 45, 145, {Stat.DEFENSE: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Growl"), (1, "Water Gun"), (1, "Wing Attack"), (17, "Water Pulse"), (27, "Brine"), (35, "Hydro Pump")),
     (), "It carries food and even small Pokemon for long distances in its enormous beak pouch.")

_add("Buizel", Type.WATER, None, StatBlock(55, 65, 35, 60, 30, 85), ("Swift Swim",), "Water Veil", GenderRatio.EVEN, 190, 61, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Water Gun"), (1, "Growl"), (9, "Aqua Jet"), (17, "Swift")), (_lvl("Floatzel", 26),), "The flotation sac around its neck lets it bob effortlessly along fast river currents.")
_add("Floatzel", Type.WATER, None, StatBlock(85, 105, 55, 85, 50, 115), ("Swift Swim",), "Water Veil", GenderRatio.EVEN, 75, 173, {Stat.SPEED: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Water Gun"), (1, "Growl"), (1, "Aqua Jet"), (17, "Swift"), (27, "Aqua Tail"), (37, "Hydro Pump")),
     (), "It's employed by fishing crews to herd shoals of prey fish right into their nets.")

_add("Skarmory", Type.STEEL, Type.FLYING, StatBlock(65, 80, 140, 40, 70, 70), ("Keen Eye", "Sturdy"), "Weak Armor", GenderRatio.EVEN, 25, 163, {Stat.DEFENSE: 2}, GrowthRate.SLOW,
     ((1, "Peck"), (1, "Leer"), (9, "Metal Claw"), (17, "Steel Wing"), (27, "Air Slash"), (37, "Iron Head")),
     (), "Its steel feathers are so sharp that they were once forged into swords.")

_add("Roggenrola", Type.ROCK, None, StatBlock(55, 75, 85, 25, 25, 15), ("Sturdy", "Weak Armor"), "Sand Force", GenderRatio.EVEN, 255, 56, {Stat.DEFENSE: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Rock Throw"), (9, "Rock Tomb"), (17, "Rock Blast")), (_lvl("Boldore", 25),), "A hard, jagged core of energy rattles inside its rocky shell.")
_add("Boldore", Type.ROCK, None, StatBlock(70, 105, 105, 50, 40, 20), ("Sturdy", "Weak Armor"), "Sand Force", GenderRatio.EVEN, 120, 137, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Rock Throw"), (1, "Rock Tomb"), (17, "Rock Blast"), (27, "Rock Slide")), (_lvl("Gigalith", 40),), "Its glowing orange core lights up caves and can even melt surrounding rock.")
_add("Gigalith", Type.ROCK, None, StatBlock(85, 135, 130, 60, 80, 25), ("Sturdy", "Weak Armor"), "Sand Force", GenderRatio.EVEN, 60, 232, {Stat.ATTACK: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Rock Throw"), (1, "Rock Tomb"), (17, "Rock Blast"), (27, "Rock Slide"), (37, "Stone Edge"), (45, "Superpower")),
     (), "It fires condensed solar energy from its chest core, powerful enough to shatter boulders.")

_add("Yanma", Type.BUG, Type.FLYING, StatBlock(65, 65, 45, 75, 45, 95), ("Speed Boost", "Compound Eyes"), "Frisk", GenderRatio.EVEN, 75, 78, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Sand Attack"), (9, "Ancient Power"), (17, "Air Slash")), (_lvl("Yanmega", 33),), "Its enormous compound eyes can see in every direction at once, missing nothing.")
_add("Yanmega", Type.BUG, Type.FLYING, StatBlock(86, 76, 86, 116, 56, 95), ("Speed Boost", "Tinted Lens"), "Frisk", GenderRatio.EVEN, 30, 180, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Tackle"), (1, "Sand Attack"), (1, "Ancient Power"), (17, "Air Slash"), (27, "Signal Beam"), (37, "X-Scissor")),
     (), "Ferociously predatory, it hunts in packs that pick clean any weaker Pokemon in the area.")

_add("Shroomish", Type.GRASS, None, StatBlock(60, 40, 60, 40, 60, 35), ("Effect Spore", "Poison Heal"), "Quick Feet", GenderRatio.EVEN, 255, 65, {Stat.DEFENSE: 1}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Stun Spore"), (9, "Absorb"), (17, "Giga Drain")), (_lvl("Breloom", 23),), "It releases toxic spores when stepped on, so travelers learn to give it a wide berth.")
_add("Breloom", Type.GRASS, Type.FIGHTING, StatBlock(60, 130, 80, 60, 60, 70), ("Effect Spore", "Poison Heal"), "Quick Feet", GenderRatio.EVEN, 90, 161, {Stat.ATTACK: 3}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Stun Spore"), (1, "Absorb"), (17, "Giga Drain"), (27, "Mach Punch"), (37, "Close Combat")),
     (), "Its punches come so fast that it's said to be able to land ten in the time it takes to blink.")

_add("Zangoose", Type.NORMAL, None, StatBlock(73, 115, 60, 60, 60, 90), ("Immunity",), "Toxic Boost", GenderRatio.EVEN, 90, 160, {Stat.ATTACK: 2}, GrowthRate.FAST,
     ((1, "Scratch"), (1, "Leer"), (9, "Quick Attack"), (17, "Slash"), (27, "Night Slash"), (37, "Close Combat")),
     (), "A bitter, ancient rivalry with Seviper drives it to attack on sight.")
_add("Seviper", Type.POISON, None, StatBlock(73, 100, 60, 100, 60, 65), ("Shed Skin",), "Infiltrator", GenderRatio.EVEN, 90, 160, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Bite"), (1, "Leer"), (9, "Poison Fang"), (17, "Crunch"), (27, "Sludge Bomb"), (37, "Poison Jab")),
     (), "Its tail blade is coated with a virulent poison, honed for its endless duel against Zangoose.")

_add("Numel", Type.FIRE, Type.GROUND, StatBlock(60, 60, 40, 65, 45, 35), ("Oblivious", "Simple"), "Own Tempo", GenderRatio.EVEN, 255, 66, {Stat.SP_ATK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Ember"), (9, "Mud Slap"), (17, "Flame Wheel")), (_lvl("Camerupt", 33),), "Magma churns within the humps on its back, occasionally venting in a burst of steam.")
_add("Camerupt", Type.FIRE, Type.GROUND, StatBlock(70, 100, 70, 105, 75, 40), ("Oblivious", "Simple"), "Own Tempo", GenderRatio.EVEN, 150, 161, {Stat.SP_ATK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Tackle"), (1, "Ember"), (1, "Mud Slap"), (17, "Flame Wheel"), (27, "Earth Power"), (37, "Fire Blast")),
     (), "The humps on its back erupt periodically, hurling ash and cinders skyward.")

_add("Spoink", Type.PSYCHIC, None, StatBlock(60, 25, 35, 70, 80, 60), ("Thick Fat", "Own Tempo"), "Gluttony", GenderRatio.EVEN, 255, 66, {Stat.SP_DEF: 1}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Confusion"), (9, "Psybeam"), (17, "Rock Tomb")), (_lvl("Grumpig", 32),), "It bounces on its tail constantly -- if it ever stops, its heart is said to stop too.")
_add("Grumpig", Type.PSYCHIC, None, StatBlock(80, 45, 65, 90, 110, 80), ("Thick Fat", "Own Tempo"), "Gluttony", GenderRatio.EVEN, 60, 174, {Stat.SP_DEF: 2}, GrowthRate.FAST,
     ((1, "Tackle"), (1, "Confusion"), (1, "Psybeam"), (17, "Rock Tomb"), (27, "Psychic"), (37, "Amnesia")),
     (), "It dances an odd little jig said to control the minds of anyone watching too closely.")

_add("Barboach", Type.WATER, Type.GROUND, StatBlock(50, 48, 43, 46, 41, 60), ("Oblivious", "Anticipation"), "Hydration", GenderRatio.EVEN, 255, 58, {Stat.SPEED: 1}, GrowthRate.MEDIUM_FAST,
     ((1, "Mud Slap"), (1, "Water Gun"), (9, "Mud Bomb"), (17, "Bulldoze")), (_lvl("Whiscash", 30),), "Its slippery, whiskered body lets it wriggle free of almost any grip.")
_add("Whiscash", Type.WATER, Type.GROUND, StatBlock(110, 78, 73, 76, 71, 60), ("Oblivious", "Anticipation"), "Hydration", GenderRatio.EVEN, 75, 164, {Stat.HP: 2}, GrowthRate.MEDIUM_FAST,
     ((1, "Mud Slap"), (1, "Water Gun"), (1, "Mud Bomb"), (17, "Bulldoze"), (27, "Earthquake"), (35, "Hydro Pump")),
     (), "Local legend says it warns of coming earthquakes by thrashing wildly in ponds.")

# ======================================================================
# Postgame / Victory Road rare
# ======================================================================
_add("Bagon", Type.DRAGON, None, StatBlock(45, 75, 60, 40, 30, 50), ("Rock Head",), "Sheer Force", GenderRatio.EVEN, 45, 60, {Stat.ATTACK: 1}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (9, "Bite"), (17, "Dragon Breath")), (_lvl("Shelgon", 30),), "Dreaming of flight someday, it hurls itself headfirst into boulders to toughen its skull.")
_add("Shelgon", Type.DRAGON, None, StatBlock(65, 95, 100, 60, 50, 50), ("Rock Head",), "Overcoat", GenderRatio.EVEN, 45, 158, {Stat.DEFENSE: 2}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Bite"), (17, "Dragon Breath"), (27, "Dragon Claw")), (_lvl("Salamence", 50),), "It encases itself in a heavy shell, remaining nearly motionless as its body restructures inside.")
_add("Salamence", Type.DRAGON, Type.FLYING, StatBlock(95, 135, 80, 110, 80, 100), ("Intimidate",), "Moxie", GenderRatio.EVEN, 45, 270, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Leer"), (1, "Bite"), (17, "Dragon Breath"), (27, "Dragon Claw"), (41, "Dragon Dance"), (49, "Draco Meteor")),
     (), "The instant it bursts from its shell, its wings roar to life, granting the flight it always dreamed of.")

_add("Beldum", Type.STEEL, Type.PSYCHIC, StatBlock(40, 55, 80, 35, 60, 30), ("Clear Body",), "Clear Body", GenderRatio.GENDERLESS, 3, 60, {Stat.DEFENSE: 1}, GrowthRate.SLOW,
     ((1, "Take Down"),), (_lvl("Metang", 20),), "Linked to others of its kind by magnetism, it moves only by sheer force of will.")
_add("Metang", Type.STEEL, Type.PSYCHIC, StatBlock(60, 75, 100, 55, 80, 50), ("Clear Body",), "Clear Body", GenderRatio.GENDERLESS, 3, 143, {Stat.DEFENSE: 2}, GrowthRate.SLOW,
     ((1, "Take Down"), (1, "Metal Claw"), (17, "Confusion"), (27, "Psychic")), (_lvl("Metagross", 45),), "Two Beldum fused together share a single unified mind, doubling their processing power.")
_add("Metagross", Type.STEEL, Type.PSYCHIC, StatBlock(80, 135, 130, 95, 90, 70), ("Clear Body",), "Light Metal", GenderRatio.GENDERLESS, 3, 270, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Take Down"), (1, "Metal Claw"), (1, "Confusion"), (27, "Psychic"), (37, "Meteor Mash"), (45, "Zen Headbutt")),
     (), "Its brain, formed from four fused computer-like minds, is said to out-calculate a supercomputer.")

_add("Riolu", Type.FIGHTING, None, StatBlock(40, 70, 40, 35, 40, 60), ("Steadfast", "Inner Focus"), "Prankster", GenderRatio.MOSTLY_MALE, 75, 70, {Stat.ATTACK: 1}, GrowthRate.MEDIUM_SLOW,
     ((1, "Quick Attack"), (1, "Rock Smash"), (9, "Low Sweep"), (17, "Drain Punch")), (_lvl("Lucario", 25),), "It communicates over great distances using waves of aura only its kind can sense.")
_add("Lucario", Type.FIGHTING, Type.STEEL, StatBlock(70, 110, 70, 115, 70, 90), ("Steadfast", "Inner Focus"), "Justified", GenderRatio.MOSTLY_MALE, 45, 184, {Stat.ATTACK: 2}, GrowthRate.MEDIUM_SLOW,
     ((1, "Quick Attack"), (1, "Rock Smash"), (1, "Low Sweep"), (17, "Drain Punch"), (27, "Dragon Pulse"), (37, "Close Combat"), (45, "Focus Blast")),
     (), "It can read the aura of any being to sense their emotions, and even see through walls.")

# ======================================================================
# Legendaries (postgame, one per "spot")
# ======================================================================
_add("Articuno", Type.ICE, Type.FLYING, StatBlock(90, 85, 100, 95, 125, 85), ("Pressure",), "Snow Cloak", GenderRatio.GENDERLESS, 3, 290, {Stat.SP_DEF: 3}, GrowthRate.SLOW,
     ((1, "Powder Snow"), (1, "Ice Shard"), (30, "Ice Beam"), (40, "Air Slash"), (50, "Blizzard"), (55, "Sheer Cold")),
     (), "A legendary bird said to bring snowfall wherever its icy wings carry it.")
_add("Zapdos", Type.ELECTRIC, Type.FLYING, StatBlock(90, 90, 85, 125, 90, 100), ("Pressure",), "Static", GenderRatio.GENDERLESS, 3, 290, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Thunder Shock"), (1, "Agility"), (30, "Discharge"), (40, "Air Slash"), (50, "Thunderbolt"), (55, "Thunder")),
     (), "A legendary bird that is said to descend from storm clouds to strike with lightning.")
_add("Moltres", Type.FIRE, Type.FLYING, StatBlock(90, 100, 90, 125, 85, 90), ("Pressure",), "Flame Body", GenderRatio.GENDERLESS, 3, 290, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Ember"), (1, "Agility"), (30, "Flame Wheel"), (40, "Air Slash"), (50, "Flamethrower"), (55, "Fire Blast")),
     (), "A legendary bird whose fiery wings are said to have granted fire to the ancient world.")

_add("Mew", Type.PSYCHIC, None, StatBlock(100, 100, 100, 100, 100, 100), ("Synchronize",), "Synchronize", GenderRatio.GENDERLESS, 45, 270, {Stat.HP: 3}, GrowthRate.MEDIUM_SLOW,
     ((1, "Pound"), (1, "Confusion"), (20, "Psybeam"), (30, "Swift"), (40, "Psychic"), (50, "Ancient Power"), (55, "Hyper Beam")),
     (), "So rare that it is said to carry the genetic code of every Pokemon within its cells.")

_add("Lugia", Type.PSYCHIC, Type.FLYING, StatBlock(106, 90, 130, 90, 154, 110), ("Pressure",), "Multiscale", GenderRatio.GENDERLESS, 3, 306, {Stat.SP_DEF: 3}, GrowthRate.SLOW,
     ((1, "Extreme Speed"), (1, "Confusion"), (30, "Air Slash"), (40, "Dragon Pulse"), (50, "Psychic"), (55, "Hydro Pump")),
     (), "Legend calls it the guardian of the seas, said to slumber at the bottom of a stormy strait.")
_add("Ho-Oh", Type.FIRE, Type.FLYING, StatBlock(106, 130, 90, 110, 154, 90), ("Pressure",), "Regenerator", GenderRatio.GENDERLESS, 3, 306, {Stat.SP_DEF: 3}, GrowthRate.SLOW,
     ((1, "Extreme Speed"), (1, "Ember"), (30, "Air Slash"), (40, "Flamethrower"), (50, "Fire Blast"), (55, "Sky Attack")),
     (), "A rainbow is said to trail its wings, and anyone who sees it is promised eternal happiness.")

_add("Suicune", Type.WATER, None, StatBlock(100, 75, 115, 90, 115, 85), ("Pressure",), "Inner Focus", GenderRatio.GENDERLESS, 3, 290, {Stat.SP_DEF: 3}, GrowthRate.SLOW,
     ((1, "Bite"), (1, "Aqua Jet"), (30, "Ice Beam"), (40, "Aqua Tail"), (50, "Hydro Pump"), (55, "Blizzard")),
     (), "A legendary beast said to purify any water it runs across, moving faster than a gale.")

_add("Groudon", Type.GROUND, None, StatBlock(100, 150, 140, 100, 90, 90), ("Drought",), "Drought", GenderRatio.GENDERLESS, 3, 302, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Mud Slap"), (1, "Bulldoze"), (30, "Earth Power"), (40, "Rock Slide"), (50, "Earthquake"), (55, "Fire Blast")),
     (), "Said to have raised continents from the sea, it slumbers deep underground, dreaming of sunlight.")
_add("Rayquaza", Type.DRAGON, Type.FLYING, StatBlock(105, 150, 90, 150, 90, 95), ("Air Lock",), "Air Lock", GenderRatio.GENDERLESS, 3, 306, {Stat.ATTACK: 2, Stat.SP_ATK: 1}, GrowthRate.SLOW,
     ((1, "Twister"), (1, "Extreme Speed"), (30, "Dragon Claw"), (40, "Air Slash"), (50, "Dragon Pulse"), (55, "Outrage")),
     (), "Legend says it descends from the ozone layer to calm any clash between the land and sea titans -- and to end a solar eclipse.")

_add("Dialga", Type.STEEL, Type.DRAGON, StatBlock(100, 120, 120, 150, 100, 90), ("Pressure",), "Telepathy", GenderRatio.GENDERLESS, 3, 306, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Metal Claw"), (1, "Dragon Breath"), (30, "Iron Head"), (40, "Dragon Claw"), (50, "Flash Cannon"), (55, "Draco Meteor")),
     (), "Said to be able to see the entire flow of time, from ancient past to distant future.")
_add("Palkia", Type.WATER, Type.DRAGON, StatBlock(90, 120, 100, 150, 120, 100), ("Pressure",), "Telepathy", GenderRatio.GENDERLESS, 3, 306, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Water Gun"), (1, "Dragon Breath"), (30, "Hydro Pump"), (40, "Dragon Claw"), (50, "Aqua Tail"), (55, "Draco Meteor")),
     (), "Said to command a parallel dimension, tearing space itself apart with its pearled claws.")
_add("Giratina", Type.GHOST, Type.DRAGON, StatBlock(150, 100, 120, 100, 120, 90), ("Pressure",), "Telepathy", GenderRatio.GENDERLESS, 3, 306, {Stat.HP: 3}, GrowthRate.SLOW,
     ((1, "Shadow Ball"), (1, "Dragon Breath"), (30, "Shadow Claw"), (40, "Dragon Claw"), (50, "Dark Pulse"), (55, "Draco Meteor")),
     (), "Banished to a distorted world for its violence, it is said to watch the living world through mirrors.")
_add("Regigigas", Type.NORMAL, None, StatBlock(110, 160, 110, 80, 110, 100), ("Slow Start",), "Slow Start", GenderRatio.GENDERLESS, 3, 302, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Tackle"), (1, "Stomp"), (30, "Rock Slide"), (40, "Superpower"), (50, "Crunch"), (55, "Hyper Beam")),
     (), "Legend says it dragged continents into place using nothing but ropes and its own titanic strength.")

_add("Reshiram", Type.DRAGON, Type.FIRE, StatBlock(100, 120, 100, 150, 120, 90), ("Turboblaze",), "Turboblaze", GenderRatio.GENDERLESS, 3, 306, {Stat.SP_ATK: 3}, GrowthRate.SLOW,
     ((1, "Ember"), (1, "Dragon Breath"), (30, "Flamethrower"), (40, "Dragon Claw"), (50, "Fusion Flare"), (55, "Fire Blast")),
     (), "Said to scorch the world in service of the ideal of truth, alongside its eternal opposite.")
_add("Zekrom", Type.DRAGON, Type.ELECTRIC, StatBlock(100, 150, 120, 120, 100, 90), ("Teravolt",), "Teravolt", GenderRatio.GENDERLESS, 3, 306, {Stat.ATTACK: 3}, GrowthRate.SLOW,
     ((1, "Thunder Shock"), (1, "Dragon Breath"), (30, "Thunderbolt"), (40, "Dragon Claw"), (50, "Fusion Bolt"), (55, "Thunder")),
     (), "Said to scorch the sky black in service of the ideal of ideals, alongside its eternal opposite.")

_add("Jirachi", Type.STEEL, Type.PSYCHIC, StatBlock(100, 100, 100, 100, 100, 100), ("Serene Grace",), "Serene Grace", GenderRatio.GENDERLESS, 3, 270, {Stat.HP: 1, Stat.ATTACK: 1, Stat.SP_ATK: 1}, GrowthRate.SLOW,
     ((1, "Confusion"), (1, "Iron Defense"), (20, "Psychic"), (30, "Flash Cannon"), (40, "Calm Mind"), (50, "Meteor Mash"), (55, "Iron Head")),
     (), "Said to awaken for just seven days every thousand years to grant a single true wish.")
