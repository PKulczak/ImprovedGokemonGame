"""MOVES: dict[str, Move] -- every move referenced by data/species.py learnsets
and data/trainers.py TrainerPokemonPreset movesets, plus a broad spread of
well-known real moves for good type coverage.

Gen-3-style rules followed throughout (per the battle-mechanics workstream's
contract in battle/schemas.py):
  - Category is determined purely by TYPE, not by move name:
      PHYSICAL_TYPES = Normal, Fighting, Flying, Ground, Rock, Bug, Ghost, Poison, Steel
      SPECIAL_TYPES  = Fire, Water, Grass, Electric, Ice, Psychic, Dragon, Dark
    This means a handful of moves that are physical in the real modern games
    (e.g. Crunch, Bite, Leaf Blade, Flash Cannon, Focus Blast) are classified
    Special or Physical here strictly by their type, per the simplification
    the design doc calls for. This is deliberate, not an oversight.
  - secondary_effect uses ONLY the fixed hook-id vocabulary: burn, poison,
    toxic, paralyze, freeze, sleep, confuse, flinch, stat_change_self,
    stat_change_target, heal_self, recoil, drain, rest, ohko, multi_hit,
    high_crit.
  - Moves whose real effect needs more than one simultaneous hook (Swagger,
    Ancient Power's own all-stat boost handled as a single stat, Overheat,
    etc.) are simplified down to a single representative hook.
  - Moves that need engine mechanics outside this hook vocabulary entirely
    (Protect, Substitute, Leech Seed, entry hazards, screens, multi-turn
    trapping, Future Sight, weather-setting moves) are intentionally omitted
    -- nothing below references them.
"""

from battle.schemas import Type, MoveCategory, Target, Move

MOVES: dict[str, Move] = {
    # ------------------------------------------------------------------
    # NORMAL
    # ------------------------------------------------------------------
    "Tackle": Move(name="Tackle", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, makes_contact=True, flavor_text="A physical attack in which the user charges and slams into the target."),
    "Scratch": Move(name="Scratch", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, makes_contact=True, flavor_text="Hard, pointed, sharp claws rake the target."),
    "Pound": Move(name="Pound", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, makes_contact=True, flavor_text="The target is physically pounded with a long tail or a foreleg."),
    "Quick Attack": Move(name="Quick Attack", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=30, priority=1, makes_contact=True, flavor_text="The user lunges at the target at a speed that makes it almost invisible."),
    "Slam": Move(name="Slam", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=80, accuracy=75, pp=20, makes_contact=True, flavor_text="The target is slammed with a long tail, vines, or the like."),
    "Body Slam": Move(name="Body Slam", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=85, accuracy=100, pp=15, makes_contact=True, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="The user drops onto the target with its full body weight, maybe causing paralysis."),
    "Double-Edge": Move(name="Double-Edge", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=120, accuracy=100, pp=15, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.33}, flavor_text="A reckless, life-risking tackle that also damages the user."),
    "Hyper Beam": Move(name="Hyper Beam", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=150, accuracy=90, pp=5, flavor_text="A powerful attack that leaves the user unable to move on the next turn."),
    "Return": Move(name="Return", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=102, accuracy=100, pp=20, makes_contact=True, flavor_text="A full-power attack that grows more powerful the more the user trusts its Trainer."),
    "Facade": Move(name="Facade", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=70, accuracy=100, pp=20, makes_contact=True, flavor_text="Doubles in power if the user is poisoned, burned, or paralyzed."),
    "Swift": Move(name="Swift", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=60, accuracy=None, pp=20, flavor_text="Star-shaped rays are shot at the target, and they never miss."),
    "Extreme Speed": Move(name="Extreme Speed", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=5, priority=2, makes_contact=True, flavor_text="The user charges at the target at blinding speed."),
    "Take Down": Move(name="Take Down", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=90, accuracy=85, pp=20, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.25}, flavor_text="A reckless full-body charge that also hurts the user a little."),
    "Hyper Fang": Move(name="Hyper Fang", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=80, accuracy=90, pp=15, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=10, flavor_text="The user bites hard on the target with its sharp front fangs."),
    "Stomp": Move(name="Stomp", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=65, accuracy=100, pp=20, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="The target is stomped with a big foot, which may cause flinching."),
    "Hyper Voice": Move(name="Hyper Voice", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=90, accuracy=100, pp=10, flavor_text="The user lets loose a horribly echoing shout that can shake the earth."),
    "Slash": Move(name="Slash", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=70, accuracy=100, pp=20, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The target is attacked with a slash of claws or a blade, striking a critical hit more often."),
    "Struggle": Move(name="Struggle", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=50, accuracy=None, pp=1, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.25}, flavor_text="Used only when all other moves are out of PP; it also hurts the user."),
    "Growl": Move(name="Growl", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=40, secondary_effect="stat_change_target", secondary_effect_params={"stat": "attack", "stages": -1}, flavor_text="The user growls in an endearing way, lowering the target's Attack."),
    "Tail Whip": Move(name="Tail Whip", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=30, secondary_effect="stat_change_target", secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The user wags its tail cutely, lowering the target's Defense."),
    "Leer": Move(name="Leer", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=30, secondary_effect="stat_change_target", secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The user gives an intimidating leer, lowering the target's Defense."),
    "Double Team": Move(name="Double Team", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=15, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "evasion", "stages": 1}, flavor_text="By moving rapidly, the user makes illusory copies of itself to raise evasiveness."),
    "Rest": Move(name="Rest", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=10, target=Target.USER, secondary_effect="rest", secondary_effect_chance=100, flavor_text="The user goes to sleep for two turns, fully restoring HP and curing any status."),
    "Charm": Move(name="Charm", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=20, secondary_effect="stat_change_target", secondary_effect_params={"stat": "defense", "stages": -2}, flavor_text="The user gazes at the target rather charmingly, sharply lowering its Defense."),
    "Scary Face": Move(name="Scary Face", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_params={"stat": "speed", "stages": -2}, flavor_text="The user frightens the target with a scary face, sharply lowering its Speed."),
    "Belly Drum": Move(name="Belly Drum", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=10, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "attack", "stages": 6}, flavor_text="The user maximizes its Attack stat in exchange for HP."),
    "Howl": Move(name="Howl", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=40, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The user howls to raise its spirit, boosting its Attack."),
    "Defense Curl": Move(name="Defense Curl", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=40, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "defense", "stages": 1}, flavor_text="The user curls up to conceal weak points, raising its Defense."),
    "Sing": Move(name="Sing", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=55, pp=15, secondary_effect="sleep", secondary_effect_chance=100, flavor_text="A soothing lullaby is sung in a calming voice that lulls the target into a deep sleep."),
    "Supersonic": Move(name="Supersonic", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=55, pp=20, secondary_effect="confuse", secondary_effect_chance=100, flavor_text="The user generates odd sound waves that confuse the target."),
    "Swords Dance": Move(name="Swords Dance", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "attack", "stages": 2}, flavor_text="A frenetic dance to uplift the fighting spirit, sharply raising the user's Attack."),

    # ------------------------------------------------------------------
    # FIRE
    # ------------------------------------------------------------------
    "Ember": Move(name="Ember", type=Type.FIRE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The target is attacked with small flames that may inflict a burn."),
    "Flamethrower": Move(name="Flamethrower", type=Type.FIRE, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The target is scorched with an intense blast of fire that may inflict a burn."),
    "Fire Blast": Move(name="Fire Blast", type=Type.FIRE, category=MoveCategory.SPECIAL, power=110, accuracy=85, pp=5, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The target is attacked with an intense blast of all-consuming fire."),
    "Flame Wheel": Move(name="Flame Wheel", type=Type.FIRE, category=MoveCategory.SPECIAL, power=60, accuracy=100, pp=25, makes_contact=True, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The user cloaks itself in fire and charges at the target."),
    "Fire Fang": Move(name="Fire Fang", type=Type.FIRE, category=MoveCategory.SPECIAL, power=65, accuracy=95, pp=15, makes_contact=True, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The user bites with flame-cloaked fangs, which may inflict a burn."),
    "Fire Punch": Move(name="Fire Punch", type=Type.FIRE, category=MoveCategory.SPECIAL, power=75, accuracy=100, pp=15, makes_contact=True, secondary_effect="burn", secondary_effect_chance=10, flavor_text="The target is punched with a fiery fist that may leave it burned."),
    "Flare Blitz": Move(name="Flare Blitz", type=Type.FIRE, category=MoveCategory.SPECIAL, power=120, accuracy=100, pp=15, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.33}, flavor_text="The user cloaks itself in fire and charges, also damaging itself."),
    "Will-O-Wisp": Move(name="Will-O-Wisp", type=Type.FIRE, category=MoveCategory.STATUS, power=None, accuracy=85, pp=15, secondary_effect="burn", secondary_effect_chance=100, flavor_text="The user shoots a sinister, bluish-white flame to inflict a burn."),
    "Overheat": Move(name="Overheat", type=Type.FIRE, category=MoveCategory.SPECIAL, power=130, accuracy=90, pp=5, secondary_effect="stat_change_self", secondary_effect_chance=100, secondary_effect_params={"stat": "sp_atk", "stages": -2}, flavor_text="The user attacks with an intense blast of fire, sharply lowering its own Sp. Atk."),
    "Flame Charge": Move(name="Flame Charge", type=Type.FIRE, category=MoveCategory.SPECIAL, power=50, accuracy=100, pp=20, secondary_effect="stat_change_self", secondary_effect_chance=100, secondary_effect_params={"stat": "speed", "stages": 1}, flavor_text="Cloaking itself in flame, the user attacks, raising its own Speed."),
    "Fusion Flare": Move(name="Fusion Flare", type=Type.FIRE, category=MoveCategory.SPECIAL, power=100, accuracy=100, pp=5, flavor_text="The user attacks with a huge flame, amplified by an unseen counterpart."),

    # ------------------------------------------------------------------
    # WATER
    # ------------------------------------------------------------------
    "Water Gun": Move(name="Water Gun", type=Type.WATER, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25, flavor_text="The target is blasted with a forceful shot of water."),
    "Bubble": Move(name="Bubble", type=Type.WATER, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=30, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="A spray of countless bubbles is jetted at the target, which may lower its Speed."),
    "Surf": Move(name="Surf", type=Type.WATER, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15, flavor_text="The user attacks everything around it by swamping its surroundings with a giant wave."),
    "Hydro Pump": Move(name="Hydro Pump", type=Type.WATER, category=MoveCategory.SPECIAL, power=110, accuracy=80, pp=5, flavor_text="The target is blasted by a huge volume of water launched under great pressure."),
    "Aqua Tail": Move(name="Aqua Tail", type=Type.WATER, category=MoveCategory.SPECIAL, power=90, accuracy=90, pp=10, makes_contact=True, flavor_text="The user attacks by swinging its tail as if it were a vicious wave in a raging storm."),
    "Water Pulse": Move(name="Water Pulse", type=Type.WATER, category=MoveCategory.SPECIAL, power=60, accuracy=100, pp=20, secondary_effect="confuse", secondary_effect_chance=20, flavor_text="The user attacks with a pulsing blast of water that may confuse the target."),
    "Waterfall": Move(name="Waterfall", type=Type.WATER, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=20, flavor_text="The user charges at the target and may make it flinch."),
    "Bubble Beam": Move(name="Bubble Beam", type=Type.WATER, category=MoveCategory.SPECIAL, power=65, accuracy=100, pp=20, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="A strong jet of bubbles is forcefully sprayed at the target's face."),
    "Aqua Jet": Move(name="Aqua Jet", type=Type.WATER, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=20, priority=1, makes_contact=True, flavor_text="The user lunges at the target at a speed that makes it almost invisible."),
    "Brine": Move(name="Brine", type=Type.WATER, category=MoveCategory.SPECIAL, power=65, accuracy=100, pp=10, flavor_text="If the target's HP is down to about half, this attack hits with double the power."),
    "Scald": Move(name="Scald", type=Type.WATER, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, secondary_effect="burn", secondary_effect_chance=30, flavor_text="The user shoots boiling hot water at the target, which may inflict a burn."),
    "Withdraw": Move(name="Withdraw", type=Type.WATER, category=MoveCategory.STATUS, power=None, accuracy=None, pp=40, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "defense", "stages": 1}, flavor_text="The user withdraws its body into its hard shell, raising its Defense."),
    "Crabhammer": Move(name="Crabhammer", type=Type.WATER, category=MoveCategory.SPECIAL, power=90, accuracy=90, pp=10, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The target is hammered with a large pincer, striking a critical hit more often."),

    # ------------------------------------------------------------------
    # ELECTRIC
    # ------------------------------------------------------------------
    "Thunder Shock": Move(name="Thunder Shock", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=30, secondary_effect="paralyze", secondary_effect_chance=10, flavor_text="A jolt of electricity crashes down on the target, which may cause paralysis."),
    "Thunderbolt": Move(name="Thunderbolt", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15, secondary_effect="paralyze", secondary_effect_chance=10, flavor_text="A strong electric blast crashes down on the target, which may cause paralysis."),
    "Thunder": Move(name="Thunder", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=110, accuracy=70, pp=10, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="A wicked thunderbolt is dropped on the target, which may cause paralysis."),
    "Spark": Move(name="Spark", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=65, accuracy=100, pp=20, makes_contact=True, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="The user charges at the target, becoming electrified, which may cause paralysis."),
    "Discharge": Move(name="Discharge", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="An electric charge is loosed to strike everything around the user."),
    "Thunder Wave": Move(name="Thunder Wave", type=Type.ELECTRIC, category=MoveCategory.STATUS, power=None, accuracy=100, pp=20, secondary_effect="paralyze", secondary_effect_chance=100, flavor_text="A weak jolt of electricity is launched to paralyze the target."),
    "Thunder Fang": Move(name="Thunder Fang", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=65, accuracy=95, pp=15, makes_contact=True, secondary_effect="paralyze", secondary_effect_chance=10, flavor_text="The user bites with electrified fangs, which may cause paralysis."),
    "Volt Tackle": Move(name="Volt Tackle", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=120, accuracy=100, pp=15, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.33}, flavor_text="The user electrifies itself and charges, also damaging itself."),
    "Charge Beam": Move(name="Charge Beam", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=50, accuracy=90, pp=10, secondary_effect="stat_change_self", secondary_effect_chance=70, secondary_effect_params={"stat": "sp_atk", "stages": 1}, flavor_text="The user attacks with an electric charge, which may raise its own Sp. Atk."),
    "Shock Wave": Move(name="Shock Wave", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=60, accuracy=None, pp=20, flavor_text="A quick jolt of electricity strikes the target, and it never misses."),
    "Fusion Bolt": Move(name="Fusion Bolt", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=100, accuracy=100, pp=5, flavor_text="The user throws down a huge bolt of lightning, amplified by an unseen counterpart."),

    # ------------------------------------------------------------------
    # GRASS
    # ------------------------------------------------------------------
    "Vine Whip": Move(name="Vine Whip", type=Type.GRASS, category=MoveCategory.SPECIAL, power=45, accuracy=100, pp=25, makes_contact=True, flavor_text="The target is struck with slender, whiplike vines."),
    "Razor Leaf": Move(name="Razor Leaf", type=Type.GRASS, category=MoveCategory.SPECIAL, power=55, accuracy=95, pp=25, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="Sharp-edged leaves are launched to slash at the target, striking a critical hit more often."),
    "Giga Drain": Move(name="Giga Drain", type=Type.GRASS, category=MoveCategory.SPECIAL, power=75, accuracy=100, pp=10, secondary_effect="drain", secondary_effect_params={"fraction": 0.5}, flavor_text="A nutrient-draining attack that heals the user for half the damage dealt."),
    "Solar Beam": Move(name="Solar Beam", type=Type.GRASS, category=MoveCategory.SPECIAL, power=120, accuracy=100, pp=10, flavor_text="A two-turn attack that gathers light, then blasts a bundled beam."),
    "Leaf Blade": Move(name="Leaf Blade", type=Type.GRASS, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="A sharp leaf blade slashes the target, striking a critical hit more often."),
    "Energy Ball": Move(name="Energy Ball", type=Type.GRASS, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The user draws power from nature and fires it at the target."),
    "Synthesis": Move(name="Synthesis", type=Type.GRASS, category=MoveCategory.STATUS, power=None, accuracy=None, pp=5, target=Target.USER, secondary_effect="heal_self", secondary_effect_params={"fraction": 0.5}, flavor_text="The user restores its own HP by drawing on sunlight."),
    "Growth": Move(name="Growth", type=Type.GRASS, category=MoveCategory.STATUS, power=None, accuracy=None, pp=40, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "sp_atk", "stages": 1}, flavor_text="The user's body grows, raising its Sp. Atk."),
    "Cotton Spore": Move(name="Cotton Spore", type=Type.GRASS, category=MoveCategory.STATUS, power=None, accuracy=100, pp=40, secondary_effect="stat_change_target", secondary_effect_params={"stat": "speed", "stages": -2}, flavor_text="Fluffy cotton spores are scattered, sharply lowering the target's Speed."),
    "Seed Bomb": Move(name="Seed Bomb", type=Type.GRASS, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, makes_contact=True, flavor_text="The user slams a barrage of hard-shelled seeds down on the target."),
    "Magical Leaf": Move(name="Magical Leaf", type=Type.GRASS, category=MoveCategory.SPECIAL, power=60, accuracy=None, pp=20, flavor_text="Sharp leaves are launched in a way that they follow the target, and never miss."),
    "Stun Spore": Move(name="Stun Spore", type=Type.GRASS, category=MoveCategory.STATUS, power=None, accuracy=75, pp=30, secondary_effect="paralyze", secondary_effect_chance=100, flavor_text="The user scatters a cloud of paralyzing powder."),
    "Sleep Powder": Move(name="Sleep Powder", type=Type.GRASS, category=MoveCategory.STATUS, power=None, accuracy=75, pp=15, secondary_effect="sleep", secondary_effect_chance=100, flavor_text="The user scatters a big cloud of sleep-inducing dust around the target."),
    "Absorb": Move(name="Absorb", type=Type.GRASS, category=MoveCategory.SPECIAL, power=20, accuracy=100, pp=25, secondary_effect="drain", secondary_effect_params={"fraction": 0.5}, flavor_text="A nutrient-draining attack that heals the user for half the damage dealt."),

    # ------------------------------------------------------------------
    # ICE
    # ------------------------------------------------------------------
    "Icy Wind": Move(name="Icy Wind", type=Type.ICE, category=MoveCategory.SPECIAL, power=55, accuracy=95, pp=15, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="The user attacks with a chilling gust that slows the target down."),
    "Ice Beam": Move(name="Ice Beam", type=Type.ICE, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=10, secondary_effect="freeze", secondary_effect_chance=10, flavor_text="The target is struck with an icy-cold beam that may freeze it solid."),
    "Blizzard": Move(name="Blizzard", type=Type.ICE, category=MoveCategory.SPECIAL, power=110, accuracy=70, pp=5, secondary_effect="freeze", secondary_effect_chance=10, flavor_text="A howling blizzard is summoned to strike the target, which may freeze it."),
    "Ice Punch": Move(name="Ice Punch", type=Type.ICE, category=MoveCategory.SPECIAL, power=75, accuracy=100, pp=15, makes_contact=True, secondary_effect="freeze", secondary_effect_chance=10, flavor_text="The target is punched with an icy fist that may freeze it solid."),
    "Ice Shard": Move(name="Ice Shard", type=Type.ICE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=30, priority=1, flavor_text="The user flash-freezes chunks of ice and hurls them at the target."),
    "Avalanche": Move(name="Avalanche", type=Type.ICE, category=MoveCategory.SPECIAL, power=60, accuracy=100, pp=10, makes_contact=True, flavor_text="An avalanche of ice crashes down on the target."),
    "Powder Snow": Move(name="Powder Snow", type=Type.ICE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25, secondary_effect="freeze", secondary_effect_chance=10, flavor_text="The user attacks with a chilling gust of powdery snow that may freeze the target."),
    "Sheer Cold": Move(name="Sheer Cold", type=Type.ICE, category=MoveCategory.SPECIAL, power=None, accuracy=30, pp=5, secondary_effect="ohko", secondary_effect_chance=100, flavor_text="An attack that hits with a icy chill so cold that it knocks out the target if it hits."),

    # ------------------------------------------------------------------
    # FIGHTING
    # ------------------------------------------------------------------
    "Karate Chop": Move(name="Karate Chop", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=50, accuracy=100, pp=25, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The target is attacked with a sharp chop, striking a critical hit more often."),
    "Brick Break": Move(name="Brick Break", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=75, accuracy=100, pp=15, makes_contact=True, flavor_text="The user attacks with a swift chop that can shatter barriers."),
    "Close Combat": Move(name="Close Combat", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=120, accuracy=100, pp=5, makes_contact=True, secondary_effect="stat_change_self", secondary_effect_chance=100, secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The user fights the target up close without guarding itself, also lowering its own Defense."),
    "Focus Punch": Move(name="Focus Punch", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=150, accuracy=100, pp=20, makes_contact=True, flavor_text="The user focuses its mind before launching a punch with tremendous power."),
    "Cross Chop": Move(name="Cross Chop", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=100, accuracy=80, pp=5, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The user delivers a double chop with its forearms crossed, striking a critical hit more often."),
    "Low Sweep": Move(name="Low Sweep", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=65, accuracy=100, pp=20, makes_contact=True, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="The user attacks the target's legs swiftly, lowering the target's Speed."),
    "Superpower": Move(name="Superpower", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=120, accuracy=100, pp=5, makes_contact=True, secondary_effect="stat_change_self", secondary_effect_chance=100, secondary_effect_params={"stat": "attack", "stages": -1}, flavor_text="The target is attacked with muscle-packed power, but this also lowers the user's Attack."),
    "Focus Blast": Move(name="Focus Blast", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=120, accuracy=70, pp=5, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The user heightens its mental focus and unleashes its power."),
    "Drain Punch": Move(name="Drain Punch", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=75, accuracy=100, pp=10, makes_contact=True, secondary_effect="drain", secondary_effect_params={"fraction": 0.5}, flavor_text="An energy-draining punch that heals the user for half the damage dealt."),
    "Mach Punch": Move(name="Mach Punch", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=30, priority=1, makes_contact=True, flavor_text="The user throws a punch at blinding speed."),
    "Rock Smash": Move(name="Rock Smash", type=Type.FIGHTING, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=15, makes_contact=True, secondary_effect="stat_change_target", secondary_effect_chance=50, secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The user attacks with a punch that can shatter rocks, which may lower the target's Defense."),
    "Bulk Up": Move(name="Bulk Up", type=Type.FIGHTING, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The user tenses its muscles to bulk up its body, boosting its Attack."),

    # ------------------------------------------------------------------
    # POISON
    # ------------------------------------------------------------------
    "Poison Sting": Move(name="Poison Sting", type=Type.POISON, category=MoveCategory.PHYSICAL, power=15, accuracy=100, pp=35, secondary_effect="poison", secondary_effect_chance=30, flavor_text="The user stabs the target with a poisonous stinger, which may poison it."),
    "Sludge": Move(name="Sludge", type=Type.POISON, category=MoveCategory.PHYSICAL, power=65, accuracy=100, pp=20, secondary_effect="poison", secondary_effect_chance=30, flavor_text="Unsanitary sludge is hurled at the target, which may poison it."),
    "Sludge Bomb": Move(name="Sludge Bomb", type=Type.POISON, category=MoveCategory.PHYSICAL, power=90, accuracy=100, pp=10, secondary_effect="poison", secondary_effect_chance=30, flavor_text="Unsanitary sludge is hurled at the target, which may poison it."),
    "Poison Jab": Move(name="Poison Jab", type=Type.POISON, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=20, makes_contact=True, secondary_effect="poison", secondary_effect_chance=30, flavor_text="The target is stabbed with a tentacle or arm steeped in poison."),
    "Acid": Move(name="Acid", type=Type.POISON, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=30, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The target is attacked with a spray of harsh acid, which may lower its Sp. Def."),
    "Toxic": Move(name="Toxic", type=Type.POISON, category=MoveCategory.STATUS, power=None, accuracy=90, pp=10, secondary_effect="toxic", secondary_effect_chance=100, flavor_text="A move that leaves the target badly poisoned, worsening every turn."),
    "Poison Fang": Move(name="Poison Fang", type=Type.POISON, category=MoveCategory.PHYSICAL, power=50, accuracy=100, pp=15, makes_contact=True, secondary_effect="toxic", secondary_effect_chance=30, flavor_text="The user bites the target with toxic fangs, which may badly poison it."),
    "Gunk Shot": Move(name="Gunk Shot", type=Type.POISON, category=MoveCategory.PHYSICAL, power=120, accuracy=70, pp=5, secondary_effect="poison", secondary_effect_chance=30, flavor_text="The user shoots filthy garbage at the target, which may poison it."),
    "Smog": Move(name="Smog", type=Type.POISON, category=MoveCategory.PHYSICAL, power=30, accuracy=70, pp=20, secondary_effect="poison", secondary_effect_chance=40, flavor_text="The target is attacked with a discharge of filthy gases, which may poison it."),

    # ------------------------------------------------------------------
    # GROUND
    # ------------------------------------------------------------------
    "Sand Attack": Move(name="Sand Attack", type=Type.GROUND, category=MoveCategory.STATUS, power=None, accuracy=100, pp=15, secondary_effect="stat_change_target", secondary_effect_params={"stat": "accuracy", "stages": -1}, flavor_text="Sand is hurled in the target's face, lowering its accuracy."),
    "Mud Slap": Move(name="Mud Slap", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=20, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "accuracy", "stages": -1}, flavor_text="Mud is hurled in the target's face, lowering its accuracy."),
    "Earthquake": Move(name="Earthquake", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=100, accuracy=100, pp=10, flavor_text="The user sets off an earthquake that strikes those around it."),
    "Dig": Move(name="Dig", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=10, makes_contact=True, flavor_text="The user burrows underground, then attacks on the next turn."),
    "Bulldoze": Move(name="Bulldoze", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=60, accuracy=100, pp=20, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="The user stomps down on the ground, lowering the target's Speed."),
    "Bone Club": Move(name="Bone Club", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=65, accuracy=85, pp=20, secondary_effect="flinch", secondary_effect_chance=10, flavor_text="The user clubs the target with a bone, which may make it flinch."),
    "Mud Bomb": Move(name="Mud Bomb", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=65, accuracy=85, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=30, secondary_effect_params={"stat": "accuracy", "stages": -1}, flavor_text="The user launches a hard-packed mudball, which may lower the target's accuracy."),
    "Fissure": Move(name="Fissure", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=None, accuracy=30, pp=5, secondary_effect="ohko", secondary_effect_chance=100, flavor_text="The user opens a fissure in the ground and drops the target in, knocking it out instantly if it hits."),
    "Earth Power": Move(name="Earth Power", type=Type.GROUND, category=MoveCategory.PHYSICAL, power=90, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The user makes the ground under the target erupt with power."),

    # ------------------------------------------------------------------
    # FLYING
    # ------------------------------------------------------------------
    "Gust": Move(name="Gust", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, flavor_text="A gust of wind is whipped up and launched at the target."),
    "Wing Attack": Move(name="Wing Attack", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=60, accuracy=100, pp=35, makes_contact=True, flavor_text="The target is struck with large, imposing wings spread wide."),
    "Aerial Ace": Move(name="Aerial Ace", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=60, accuracy=None, pp=20, makes_contact=True, flavor_text="The user confounds the target with speed, striking as it dashes in, and it never misses."),
    "Air Slash": Move(name="Air Slash", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=75, accuracy=95, pp=15, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="The user attacks with a blade of air that slices even the sky, which may make the target flinch."),
    "Brave Bird": Move(name="Brave Bird", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=120, accuracy=100, pp=15, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.33}, flavor_text="The user tucks in its wings and charges from a low altitude, also hurting itself."),
    "Drill Peck": Move(name="Drill Peck", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=20, makes_contact=True, flavor_text="A corkscrewing attack with a sharply pointed beak, acting as a drill."),
    "Peck": Move(name="Peck", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=35, accuracy=100, pp=35, makes_contact=True, flavor_text="The target is jabbed with a sharply pointed beak or horn."),
    "Sky Attack": Move(name="Sky Attack", type=Type.FLYING, category=MoveCategory.PHYSICAL, power=140, accuracy=90, pp=5, makes_contact=True, flavor_text="A second-turn attack move that requires a first turn of charging before it strikes."),
    "Roost": Move(name="Roost", type=Type.FLYING, category=MoveCategory.STATUS, power=None, accuracy=None, pp=10, target=Target.USER, secondary_effect="heal_self", secondary_effect_params={"fraction": 0.5}, flavor_text="The user lands and rests its body, restoring its own HP."),

    # ------------------------------------------------------------------
    # PSYCHIC
    # ------------------------------------------------------------------
    "Confusion": Move(name="Confusion", type=Type.PSYCHIC, category=MoveCategory.SPECIAL, power=50, accuracy=100, pp=25, secondary_effect="confuse", secondary_effect_chance=10, flavor_text="The target is hit by a weak telekinetic force, which may also confuse it."),
    "Psybeam": Move(name="Psybeam", type=Type.PSYCHIC, category=MoveCategory.SPECIAL, power=65, accuracy=100, pp=20, secondary_effect="confuse", secondary_effect_chance=10, flavor_text="The target is attacked with a peculiar ray that may cause confusion."),
    "Psychic": Move(name="Psychic", type=Type.PSYCHIC, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The target is hit by a strong telekinetic force, which may also lower its Sp. Def."),
    "Psycho Cut": Move(name="Psycho Cut", type=Type.PSYCHIC, category=MoveCategory.SPECIAL, power=70, accuracy=100, pp=20, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The user slashes with blades of psychic energy, striking a critical hit more often."),
    "Zen Headbutt": Move(name="Zen Headbutt", type=Type.PSYCHIC, category=MoveCategory.SPECIAL, power=80, accuracy=90, pp=15, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=20, flavor_text="The user focuses its willpower to its head and rams the target, which may cause flinching."),
    "Calm Mind": Move(name="Calm Mind", type=Type.PSYCHIC, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "sp_atk", "stages": 1}, flavor_text="The user quietly focuses its mind, raising its Sp. Atk."),
    "Amnesia": Move(name="Amnesia", type=Type.PSYCHIC, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "sp_def", "stages": 2}, flavor_text="The user temporarily empties its mind, sharply raising its Sp. Def."),
    "Hypnosis": Move(name="Hypnosis", type=Type.PSYCHIC, category=MoveCategory.STATUS, power=None, accuracy=60, pp=20, secondary_effect="sleep", secondary_effect_chance=100, flavor_text="The user employs hypnotic suggestion to make the target fall into a deep sleep."),
    "Agility": Move(name="Agility", type=Type.PSYCHIC, category=MoveCategory.STATUS, power=None, accuracy=None, pp=30, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "speed", "stages": 2}, flavor_text="The user relaxes and lightens its body, sharply raising its Speed."),

    # ------------------------------------------------------------------
    # BUG
    # ------------------------------------------------------------------
    "Bug Bite": Move(name="Bug Bite", type=Type.BUG, category=MoveCategory.PHYSICAL, power=60, accuracy=100, pp=20, makes_contact=True, flavor_text="The user bites the target, sinking its mandibles in deep."),
    "X-Scissor": Move(name="X-Scissor", type=Type.BUG, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=15, makes_contact=True, flavor_text="The user slashes at the target by crossing its scythes or claws as if they were a pair of scissors."),
    "Signal Beam": Move(name="Signal Beam", type=Type.BUG, category=MoveCategory.PHYSICAL, power=75, accuracy=100, pp=15, secondary_effect="confuse", secondary_effect_chance=10, flavor_text="The user attacks with a sinister beam of light, which may confuse the target."),
    "Megahorn": Move(name="Megahorn", type=Type.BUG, category=MoveCategory.PHYSICAL, power=120, accuracy=85, pp=10, makes_contact=True, flavor_text="Using its tough and impressive horn, the user rams into the target with no letup."),
    "String Shot": Move(name="String Shot", type=Type.BUG, category=MoveCategory.STATUS, power=None, accuracy=95, pp=40, secondary_effect="stat_change_target", secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="The target is bound with silk shot from the user's mouth, lowering its Speed."),
    "Struggle Bug": Move(name="Struggle Bug", type=Type.BUG, category=MoveCategory.PHYSICAL, power=50, accuracy=100, pp=20, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "sp_atk", "stages": -1}, flavor_text="The user attacks while resisting, which lowers the target's Sp. Atk."),
    "Pin Missile": Move(name="Pin Missile", type=Type.BUG, category=MoveCategory.PHYSICAL, power=14, accuracy=85, pp=20, makes_contact=True, secondary_effect="multi_hit", secondary_effect_params={"min_hits": 2, "max_hits": 5}, flavor_text="Sharp spikes are shot at the target in rapid succession, hitting two to five times."),
    "Leech Life": Move(name="Leech Life", type=Type.BUG, category=MoveCategory.PHYSICAL, power=20, accuracy=100, pp=15, makes_contact=True, secondary_effect="drain", secondary_effect_params={"fraction": 0.5}, flavor_text="The user drains the target's blood, healing itself for half the damage dealt."),

    # ------------------------------------------------------------------
    # ROCK
    # ------------------------------------------------------------------
    "Rock Throw": Move(name="Rock Throw", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=50, accuracy=90, pp=15, flavor_text="The user picks up and throws a small rock at the target."),
    "Rock Slide": Move(name="Rock Slide", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=75, accuracy=90, pp=10, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="Large boulders are hurled at the target, which may make it flinch."),
    "Stone Edge": Move(name="Stone Edge", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=100, accuracy=80, pp=5, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The user stabs the target with sharpened stones, striking a critical hit more often."),
    "Rock Tomb": Move(name="Rock Tomb", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=60, accuracy=95, pp=15, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "speed", "stages": -1}, flavor_text="Boulders are hurled at the target, which lowers the target's Speed."),
    "Ancient Power": Move(name="Ancient Power", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=60, accuracy=100, pp=5, secondary_effect="stat_change_self", secondary_effect_chance=10, secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The user attacks with a prehistoric power, which may raise all its stats."),
    "Rock Blast": Move(name="Rock Blast", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=25, accuracy=90, pp=10, secondary_effect="multi_hit", secondary_effect_params={"min_hits": 2, "max_hits": 5}, flavor_text="The user hurls hard rocks at the target, hitting two to five times."),
    "Rock Polish": Move(name="Rock Polish", type=Type.ROCK, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "speed", "stages": 2}, flavor_text="The user polishes its body to reduce drag, sharply raising its Speed."),
    "Head Smash": Move(name="Head Smash", type=Type.ROCK, category=MoveCategory.PHYSICAL, power=150, accuracy=80, pp=5, makes_contact=True, secondary_effect="recoil", secondary_effect_params={"fraction": 0.5}, flavor_text="The user attacks with a hazardous, full-power headbutt, also damaging itself."),

    # ------------------------------------------------------------------
    # GHOST
    # ------------------------------------------------------------------
    "Lick": Move(name="Lick", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=30, accuracy=100, pp=30, makes_contact=True, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="The target is licked with a long tongue, which may also paralyze it."),
    "Shadow Ball": Move(name="Shadow Ball", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=15, secondary_effect="stat_change_target", secondary_effect_chance=20, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The user hurls a shadowy blob at the target, which may also lower its Sp. Def."),
    "Shadow Punch": Move(name="Shadow Punch", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=60, accuracy=None, pp=20, makes_contact=True, flavor_text="The user throws a punch from the shadows, and it never misses."),
    "Shadow Claw": Move(name="Shadow Claw", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=70, accuracy=100, pp=15, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The user slashes with a sharp claw made from shadows, striking a critical hit more often."),
    "Astonish": Move(name="Astonish", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=30, accuracy=100, pp=15, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="The user attacks the target while shouting in a startling way, which may cause flinching."),
    "Confuse Ray": Move(name="Confuse Ray", type=Type.GHOST, category=MoveCategory.STATUS, power=None, accuracy=100, pp=10, secondary_effect="confuse", secondary_effect_chance=100, flavor_text="The target is exposed to a sinister ray that confuses it."),
    "Hex": Move(name="Hex", type=Type.GHOST, category=MoveCategory.PHYSICAL, power=65, accuracy=100, pp=10, flavor_text="A relentless attack that hits harder if the target has a status condition."),

    # ------------------------------------------------------------------
    # DRAGON
    # ------------------------------------------------------------------
    "Dragon Breath": Move(name="Dragon Breath", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=60, accuracy=100, pp=20, secondary_effect="paralyze", secondary_effect_chance=30, flavor_text="The user exhales a mighty gust that inflicts damage, which may cause paralysis."),
    "Dragon Claw": Move(name="Dragon Claw", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, makes_contact=True, flavor_text="The user slashes the target with huge, sharp claws."),
    "Dragon Pulse": Move(name="Dragon Pulse", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=10, flavor_text="The target is attacked with a shock wave generated by the user's gaping mouth."),
    "Draco Meteor": Move(name="Draco Meteor", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=130, accuracy=90, pp=5, secondary_effect="stat_change_self", secondary_effect_chance=100, secondary_effect_params={"stat": "sp_atk", "stages": -2}, flavor_text="Comets are summoned down from the sky, sharply lowering the user's own Sp. Atk."),
    "Outrage": Move(name="Outrage", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=120, accuracy=100, pp=10, makes_contact=True, flavor_text="The user rampages and attacks for two to three turns, becoming confused afterward."),
    "Dragon Dance": Move(name="Dragon Dance", type=Type.DRAGON, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The user vigorously performs a mystic, powerful dance, raising its Attack."),
    "Twister": Move(name="Twister", type=Type.DRAGON, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=20, secondary_effect="flinch", secondary_effect_chance=20, flavor_text="The user whips up a vicious tornado to tear at the target, which may cause flinching."),

    # ------------------------------------------------------------------
    # DARK
    # ------------------------------------------------------------------
    "Bite": Move(name="Bite", type=Type.DARK, category=MoveCategory.SPECIAL, power=60, accuracy=100, pp=25, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="The target is bitten with sharp fangs, which may make it flinch."),
    "Crunch": Move(name="Crunch", type=Type.DARK, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, makes_contact=True, secondary_effect="stat_change_target", secondary_effect_chance=20, secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The user crunches down hard on the target with sharp fangs, which may lower its Defense."),
    "Dark Pulse": Move(name="Dark Pulse", type=Type.DARK, category=MoveCategory.SPECIAL, power=80, accuracy=100, pp=15, secondary_effect="flinch", secondary_effect_chance=20, flavor_text="The user releases a horrible aura imbued with dark thoughts, which may cause flinching."),
    "Sucker Punch": Move(name="Sucker Punch", type=Type.DARK, category=MoveCategory.SPECIAL, power=70, accuracy=100, pp=5, priority=1, makes_contact=True, flavor_text="This move enables the user to attack first, but it fails if the target is not readying an attack."),
    "Payback": Move(name="Payback", type=Type.DARK, category=MoveCategory.SPECIAL, power=50, accuracy=100, pp=10, makes_contact=True, flavor_text="The user gets revenge for any damage done by the target earlier in the same turn."),
    "Feint Attack": Move(name="Feint Attack", type=Type.DARK, category=MoveCategory.SPECIAL, power=60, accuracy=None, pp=20, makes_contact=True, flavor_text="The user approaches the target disarmingly, then strikes; it never misses."),
    "Nasty Plot": Move(name="Nasty Plot", type=Type.DARK, category=MoveCategory.STATUS, power=None, accuracy=None, pp=20, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "sp_atk", "stages": 2}, flavor_text="The user stimulates its brain by thinking bad thoughts, sharply raising its Sp. Atk."),
    "Snarl": Move(name="Snarl", type=Type.DARK, category=MoveCategory.SPECIAL, power=55, accuracy=95, pp=15, secondary_effect="stat_change_target", secondary_effect_chance=100, secondary_effect_params={"stat": "sp_atk", "stages": -1}, flavor_text="The user yells as if it is ranting about something, lowering the target's Sp. Atk."),
    "Night Slash": Move(name="Night Slash", type=Type.DARK, category=MoveCategory.SPECIAL, power=70, accuracy=100, pp=15, makes_contact=True, secondary_effect="high_crit", secondary_effect_chance=100, flavor_text="The user slashes the target the instant an opportunity arises, striking a critical hit more often."),

    # ------------------------------------------------------------------
    # STEEL
    # ------------------------------------------------------------------
    "Metal Claw": Move(name="Metal Claw", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=50, accuracy=95, pp=35, makes_contact=True, secondary_effect="stat_change_self", secondary_effect_chance=10, secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The target is raked with steel claws, which may raise the user's Attack."),
    "Iron Head": Move(name="Iron Head", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=15, makes_contact=True, secondary_effect="flinch", secondary_effect_chance=30, flavor_text="The user slams the target with its steel-hard head, which may cause flinching."),
    "Iron Tail": Move(name="Iron Tail", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=100, accuracy=75, pp=15, makes_contact=True, secondary_effect="stat_change_target", secondary_effect_chance=30, secondary_effect_params={"stat": "defense", "stages": -1}, flavor_text="The target is slammed with a steel-hard tail, which may lower its Defense."),
    "Flash Cannon": Move(name="Flash Cannon", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=80, accuracy=100, pp=10, secondary_effect="stat_change_target", secondary_effect_chance=10, secondary_effect_params={"stat": "sp_def", "stages": -1}, flavor_text="The user gathers all its light energy and releases it at once."),
    "Steel Wing": Move(name="Steel Wing", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=70, accuracy=90, pp=25, makes_contact=True, secondary_effect="stat_change_self", secondary_effect_chance=10, secondary_effect_params={"stat": "defense", "stages": 1}, flavor_text="The target is hit with wings of steel, which may also raise the user's Defense."),
    "Meteor Mash": Move(name="Meteor Mash", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=90, accuracy=90, pp=10, makes_contact=True, secondary_effect="stat_change_self", secondary_effect_chance=20, secondary_effect_params={"stat": "attack", "stages": 1}, flavor_text="The target is hit with a meteor-like punch, which may also raise the user's Attack."),
    "Bullet Punch": Move(name="Bullet Punch", type=Type.STEEL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=30, priority=1, makes_contact=True, flavor_text="The user strikes the target with tough punches as fast as bullets."),
    "Iron Defense": Move(name="Iron Defense", type=Type.STEEL, category=MoveCategory.STATUS, power=None, accuracy=None, pp=15, target=Target.USER, secondary_effect="stat_change_self", secondary_effect_params={"stat": "defense", "stages": 2}, flavor_text="The user hardens its body's surface like iron, sharply raising its Defense."),
}
