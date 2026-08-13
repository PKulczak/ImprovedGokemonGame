"""TRAINERS: dict[str, Trainer] -- every scripted trainer battle in the game.

Keying scheme (short id -> Trainer), so the overworld/scripted-event
workstream can look battles up by a stable string key rather than by index:

  "rival_<starter>_<stage>"   -- Rival Corin always fields whichever starter
        is type-advantaged over the PLAYER's choice. Since this module is
        authored before the player's actual pick is known, one full line is
        authored per possible player starter (the key names the *player's*
        starter, not Corin's -- Corin's own team is the counter-pick):
            rival_chikorita_1/2/3  -- player chose Chikorita  -> Corin uses Torchic line
            rival_torchic_1/2/3    -- player chose Torchic    -> Corin uses Oshawott line
            rival_oshawott_1/2/3   -- player chose Oshawott   -> Corin uses Chikorita line
        `_1`/`_2`/`_3` are escalating story-progress stages (early route,
        mid-game, pre-League).
  "gym_leader_<name>"         -- the 8 Gym Leaders, one each, in plan-doc order.
  "team_eclipse_grunt_<n>"    -- generic Team Eclipse grunts (n = 1..3).
  "team_eclipse_nyx"          -- Team Eclipse leader Nyx's first appearance.
  "team_eclipse_nyx_climax"   -- Nyx's stronger, climactic rematch just before
        the Champion, per the design doc's "climactic battle" beat.
  "elite_four_<name>"         -- the 4 Elite Four members.
  "champion_astra"            -- the Champion.
  "<class>_<name>"            -- ~20 generic route/gym-puzzle trainers with
        small teams for overworld flavor and gym mazes/puzzles, e.g.
        "youngster_dale", "hiker_grant", "dragon_tamer_finn".
"""

from battle.schemas import AITier, Trainer, TrainerPokemonPreset
from data.species import SPECIES


def _p(species_name, level, moves=None, nature=None, ivs=None, held_item=None):
    return TrainerPokemonPreset(
        species=SPECIES[species_name], level=level, moves=moves,
        nature=nature, ivs=ivs, held_item=held_item,
    )


TRAINERS: dict[str, Trainer] = {}


def _add(key, name, trainer_class, team, ai_tier, prize_money, pre=(), win=(), lose=()):
    TRAINERS[key] = Trainer(
        name=name, trainer_class=trainer_class, team=team, ai_tier=ai_tier,
        prize_money=prize_money, pre_battle_text=pre, win_text=win, lose_text=lose,
    )


# ======================================================================
# Rival Corin -- one line per possible player starter, 3 escalating stages
# ======================================================================

# --- player chose Chikorita -> Corin counters with the Torchic line -------
_add("rival_chikorita_1", "Rival Corin", "Rival",
     (_p("Torchic", 7, moves=("Scratch", "Growl", "Ember")),
      _p("Zigzagoon", 6, moves=("Tackle", "Growl"))),
     AITier.EXPERT_TRAINER, 500,
     pre=("Corin: My Torchic's already stronger than your Chikorita, watch!",),
     win=("Corin: Ha! Told you fire beats grass!",),
     lose=("Corin: Wh-what? Fine, next time I won't hold back!",))
_add("rival_chikorita_2", "Rival Corin", "Rival",
     (_p("Combusken", 20, moves=("Flame Wheel", "Rock Smash", "Slash", "Fire Punch")),
      _p("Taillow", 18, moves=("Wing Attack", "Quick Attack")),
      _p("Linoone", 18, moves=("Slash", "Take Down"))),
     AITier.EXPERT_TRAINER, 2000,
     pre=("Corin: You've gotten better, but so have I. Combusken, let's go!",),
     win=("Corin: Still the same old story, huh?",),
     lose=("Corin: Ugh! I'm not losing again at the League, just watch!",))
_add("rival_chikorita_3", "Rival Corin", "Rival",
     (_p("Blaziken", 40, nature="Adamant", moves=("Flare Blitz", "Close Combat", "Swords Dance", "Fire Punch")),
      _p("Swellow", 38, moves=("Brave Bird", "Aerial Ace")),
      _p("Linoone", 38, moves=("Double-Edge", "Slash")),
      _p("Toxicroak", 37, moves=("Poison Jab", "Close Combat"))),
     AITier.EXPERT_TRAINER, 5000,
     pre=("Corin: Victory Road's no place for old rivalries to go soft. Let's finish this!",),
     win=("Corin: Guess I'll be the one challenging the Champion this year.",),
     lose=("Corin: ...Yeah. You've earned this one. Go show them what you've got.",))

# --- player chose Torchic -> Corin counters with the Oshawott line --------
_add("rival_torchic_1", "Rival Corin", "Rival",
     (_p("Oshawott", 7, moves=("Tackle", "Tail Whip", "Water Gun")),
      _p("Zigzagoon", 6, moves=("Tackle", "Growl"))),
     AITier.EXPERT_TRAINER, 500,
     pre=("Corin: Water beats fire, everyone knows that! Oshawott, go!",),
     win=("Corin: Easy! Better luck next time.",),
     lose=("Corin: No way! I'll train harder before we meet again!",))
_add("rival_torchic_2", "Rival Corin", "Rival",
     (_p("Dewott", 20, moves=("Aqua Jet", "Slash", "Ice Punch", "Withdraw")),
      _p("Taillow", 18, moves=("Wing Attack", "Quick Attack")),
      _p("Linoone", 18, moves=("Slash", "Take Down"))),
     AITier.EXPERT_TRAINER, 2000,
     pre=("Corin: Dewott's learned some new tricks. Ready or not!",),
     win=("Corin: Ha, still can't put out my fire, huh? Wait, wrong element.",),
     lose=("Corin: Argh! Fine, I see you're serious about this.",))
_add("rival_torchic_3", "Rival Corin", "Rival",
     (_p("Samurott", 40, nature="Modest", moves=("Hydro Pump", "Aqua Tail", "Slash", "Ice Punch")),
      _p("Swellow", 38, moves=("Brave Bird", "Aerial Ace")),
      _p("Linoone", 38, moves=("Double-Edge", "Slash")),
      _p("Weavile", 37, moves=("Ice Punch", "Night Slash"))),
     AITier.EXPERT_TRAINER, 5000,
     pre=("Corin: This is it. Samurott and I have trained for this moment!",),
     win=("Corin: The Champion's throne is mine to challenge now!",),
     lose=("Corin: ...You really are something else. Go get 'em, Champion-to-be.",))

# --- player chose Oshawott -> Corin counters with the Chikorita line ------
_add("rival_oshawott_1", "Rival Corin", "Rival",
     (_p("Chikorita", 7, moves=("Tackle", "Growl", "Vine Whip")),
      _p("Zigzagoon", 6, moves=("Tackle", "Growl"))),
     AITier.EXPERT_TRAINER, 500,
     pre=("Corin: Grass beats water, so this should be simple. Chikorita, go!",),
     win=("Corin: Told you so!",),
     lose=("Corin: What?! Okay, no more Mr. Nice Rival.",))
_add("rival_oshawott_2", "Rival Corin", "Rival",
     (_p("Bayleef", 20, moves=("Body Slam", "Razor Leaf", "Synthesis")),
      _p("Taillow", 18, moves=("Wing Attack", "Quick Attack")),
      _p("Linoone", 18, moves=("Slash", "Take Down"))),
     AITier.EXPERT_TRAINER, 2000,
     pre=("Corin: Bayleef's grown up nice and strong. Let's see how you match up!",),
     win=("Corin: Yep, still got it.",),
     lose=("Corin: No fair! ...Okay, it's fair. You're just better right now.",))
_add("rival_oshawott_3", "Rival Corin", "Rival",
     (_p("Meganium", 40, nature="Bold", moves=("Solar Beam", "Body Slam", "Growth", "Razor Leaf")),
      _p("Swellow", 38, moves=("Brave Bird", "Aerial Ace")),
      _p("Linoone", 38, moves=("Double-Edge", "Slash")),
      _p("Luxray", 37, moves=("Thunderbolt", "Crunch"))),
     AITier.EXPERT_TRAINER, 5000,
     pre=("Corin: One last battle before the League. Meganium and I won't hold anything back!",),
     win=("Corin: I'll be waiting for you at the top!",),
     lose=("Corin: ...Go on. Show the Elite Four what I already know about you.",))

# ======================================================================
# Gym Leaders (plan-doc order, escalating levels ~14 -> ~45)
# ======================================================================
_add("gym_leader_wren", "Wren", "Gym Leader",
     (_p("Beautifly", 13, moves=("Gust", "Absorb", "Stun Spore", "Signal Beam")),
      _p("Ledian", 14, nature="Timid", ivs="perfect", moves=("Bug Bite", "Agility", "Signal Beam", "Megahorn"))),
     AITier.EXPERT_TRAINER, 1400,
     pre=("Wren: Welcome to Bramblegate! My Bug types have the whole hedge maze mapped out in their heads.",),
     win=("Wren: The maze always favors the home team!",),
     lose=("Wren: Well fought! Here, take the Bramble Badge -- you've earned it.",))
_add("gym_leader_bartle", "Bartle", "Gym Leader",
     (_p("Bibarel", 16, moves=("Water Gun", "Slam", "Take Down")),
      _p("Herdier", 17, moves=("Crunch", "Take Down", "Body Slam")),
      _p("Girafarig", 18, nature="Modest", ivs="perfect", moves=("Psybeam", "Psychic", "Confusion", "Astonish"))),
     AITier.EXPERT_TRAINER, 1800,
     pre=("Bartle: Out of the spotlight, in you go! Let's see if you can even find my Pokemon.",),
     win=("Bartle: Normal types are never as simple as they look, huh?",),
     lose=("Bartle: Ha! You found the spotlight trick. Take the Hollow Badge, well earned.",))
_add("gym_leader_talia", "Talia", "Gym Leader",
     (_p("Electrode", 21, moves=("Discharge", "Thunderbolt", "Charge Beam")),
      _p("Luxio", 22, moves=("Spark", "Thunder Fang", "Leer")),
      _p("Galvantula", 23, nature="Timid", ivs="perfect", held_item="Magnet", moves=("Discharge", "X-Scissor", "Signal Beam", "Thunderbolt"))),
     AITier.EXPERT_TRAINER, 2300,
     pre=("Talia: Mind your step on the harbor tiles -- some of them bite back.",),
     win=("Talia: Currents favor the prepared!",),
     lose=("Talia: Shocking! Take the Circuit Badge -- you've more than earned it.",))
_add("gym_leader_orin", "Orin", "Gym Leader",
     (_p("Ariados", 25, moves=("Poison Jab", "Leech Life", "X-Scissor")),
      _p("Weezing", 26, moves=("Sludge Bomb", "Smog", "Acid")),
      _p("Toxicroak", 27, nature="Adamant", ivs="perfect", moves=("Poison Jab", "Close Combat", "Sludge Bomb", "Brick Break"))),
     AITier.EXPERT_TRAINER, 2700,
     pre=("Orin: Can't see much through this swamp gas, can you? My Pokemon don't mind one bit.",),
     win=("Orin: The gas always thickens right when you need to see clearly!",),
     lose=("Orin: *cough* Well fought. Take the Mire Badge before this gas gets to me.",))
_add("gym_leader_priscilla", "Priscilla", "Gym Leader",
     (_p("Mismagius", 29, moves=("Shadow Ball", "Confuse Ray", "Dark Pulse")),
      _p("Froslass", 30, moves=("Ice Beam", "Shadow Ball", "Confuse Ray")),
      _p("Dusknoir", 32, nature="Careful", ivs="perfect", held_item="Leftovers", moves=("Shadow Ball", "Ice Punch", "Hex", "Confuse Ray"))),
     AITier.EXPERT_TRAINER, 3200,
     pre=("Priscilla: The lanterns only show you so much of my manor. The rest stays in shadow.",),
     win=("Priscilla: The dark plays favorites here.",),
     lose=("Priscilla: How lovely -- a challenger who isn't afraid of the dark. Take the Duskmere Badge.",))
_add("gym_leader_kade", "Kade", "Gym Leader",
     (_p("Weavile", 33, moves=("Ice Punch", "Night Slash", "Dark Pulse")),
      _p("Vanilluxe", 34, moves=("Blizzard", "Ice Beam", "Icy Wind")),
      _p("Abomasnow", 35, nature="Modest", ivs="perfect", moves=("Blizzard", "Ice Punch", "Energy Ball", "Icy Wind"))),
     AITier.EXPERT_TRAINER, 3500,
     pre=("Kade: Careful footing on the ice -- one wrong slide and you're right back where you started.",),
     win=("Kade: Cold, calculated, and undefeated.",),
     lose=("Kade: You kept your footing better than most. Take the Frostholm Badge.",))
_add("gym_leader_garrick", "Garrick", "Gym Leader",
     (_p("Graveler", 37, moves=("Rock Slide", "Earthquake", "Rock Tomb")),
      _p("Excadrill", 38, moves=("Earthquake", "Iron Head", "Metal Claw", "Rock Slide")),
      _p("Rhyperior", 40, nature="Adamant", ivs="perfect", held_item="Choice Band", moves=("Earthquake", "Megahorn", "Rock Slide", "Stone Edge"))),
     AITier.EXPERT_TRAINER, 4000,
     pre=("Garrick: The ground itself is my gym gimmick -- hope you've got your balance.",),
     win=("Garrick: Solid as bedrock!",),
     lose=("Garrick: HA! Now THAT'S a battle. Take the Quake Badge -- you've earned every bit of it.",))
_add("gym_leader_serath", "Serath", "Gym Leader",
     (_p("Druddigon", 42, moves=("Dragon Claw", "Crunch", "Superpower")),
      _p("Flygon", 43, moves=("Dragon Claw", "Earthquake", "Dragon Dance")),
      _p("Garchomp", 45, nature="Jolly", ivs="perfect", held_item="Scope Lens", moves=("Dragon Claw", "Earthquake", "Dragon Dance", "Stone Edge"))),
     AITier.EXPERT_TRAINER, 4500,
     pre=("Serath: Skyreach Summit doesn't forgive weak wings or weak resolve. Show me yours.",),
     win=("Serath: The wind favors those who respect it.",),
     lose=("Serath: Magnificent. Take the Summit Badge -- you've earned the sky itself.",))

# ======================================================================
# Team Eclipse
# ======================================================================
_add("team_eclipse_grunt_1", "Team Eclipse Grunt", "Team Eclipse Grunt",
     (_p("Zubat", 10, moves=("Leer", "Bite")),
      _p("Poochyena", 10, moves=("Tackle", "Bite"))),
     AITier.BASIC_TRAINER, 400,
     pre=("Grunt: Eclipse business isn't your concern, kid. Get lost!",),
     win=("Grunt: Ha! Stick to catching Rattata.",),
     lose=("Grunt: Tch. Boss isn't gonna like this.",))
_add("team_eclipse_grunt_2", "Team Eclipse Grunt", "Team Eclipse Grunt",
     (_p("Golbat", 16, moves=("Bite", "Air Slash", "Poison Fang")),
      _p("Mightyena", 16, moves=("Crunch", "Take Down"))),
     AITier.BASIC_TRAINER, 900,
     pre=("Grunt: You again? We've almost got what we need from Absol's trail.",),
     win=("Grunt: Heh, Eclipse always finds a way.",),
     lose=("Grunt: H-how are you still following us?!",))
_add("team_eclipse_grunt_3", "Team Eclipse Grunt", "Team Eclipse Grunt",
     (_p("Zubat", 18, moves=("Air Slash", "Bite")),
      _p("Poochyena", 18, moves=("Take Down", "Bite")),
      _p("Golbat", 19, moves=("Poison Fang", "Air Slash", "Bite"))),
     AITier.BASIC_TRAINER, 1200,
     pre=("Grunt: The eclipse is coming, and Skyreach Summit will be ours to command!",),
     win=("Grunt: Nyx will be pleased with this.",),
     lose=("Grunt: Impossible! Nyx needs to hear about this personally...",))
_add("team_eclipse_nyx", "Nyx", "Team Eclipse Leader",
     (_p("Murkrow", 29, moves=("Astonish", "Night Slash", "Feint Attack")),
      _p("Sableye", 30, moves=("Night Slash", "Shadow Ball", "Payback")),
      _p("Honchkrow", 31, nature="Adamant", ivs="perfect", moves=("Dark Pulse", "Sucker Punch", "Night Slash", "Air Slash"))),
     AITier.EXPERT_TRAINER, 3100,
     pre=("Nyx: Absol's disaster sense is the key to everything we're planning. Step aside.",),
     win=("Nyx: Team Eclipse always gets what it came for.",),
     lose=("Nyx: ...Impressive. But this is only a taste of what's coming.",))
_add("team_eclipse_nyx_climax", "Nyx", "Team Eclipse Leader",
     (_p("Murkrow", 47, moves=("Dark Pulse", "Night Slash", "Feint Attack")),
      _p("Sableye", 48, moves=("Shadow Ball", "Night Slash", "Payback", "Confuse Ray")),
      _p("Honchkrow", 50, nature="Adamant", ivs="perfect", held_item="Scope Lens", moves=("Dark Pulse", "Sucker Punch", "Night Slash", "Air Slash"))),
     AITier.EXPERT_TRAINER, 6000,
     pre=("Nyx: The eclipse begins at Skyreach Summit. Rayquaza WILL answer our call -- you won't stop this!",),
     win=("Nyx: The sky itself bends to Eclipse now!",),
     lose=("Nyx: No... the eclipse fades. Rayquaza slips away, and so does everything we worked for.",))

# ======================================================================
# Elite Four
# ======================================================================
_add("elite_four_ivor", "Ivor", "Elite Four",
     (_p("Ninetales", 48, nature="Timid", moves=("Fire Blast", "Flamethrower", "Extreme Speed", "Will-O-Wisp")),
      _p("Typhlosion", 49, nature="Modest", moves=("Flamethrower", "Fire Punch", "Quick Attack")),
      _p("Infernape", 49, nature="Jolly", moves=("Close Combat", "Flamethrower", "Fire Punch", "Mach Punch")),
      _p("Chandelure", 50, nature="Modest", ivs="perfect", held_item="Charcoal", moves=("Fire Blast", "Shadow Ball", "Flamethrower", "Will-O-Wisp"))),
     AITier.EXPERT_TRAINER, 9800,
     pre=("Ivor: Fire cleanses as much as it destroys. Let's see which you bring out in me.",),
     win=("Ivor: The Elite Four's flame burns eternal.",),
     lose=("Ivor: A blaze truly worthy of the name. Onward -- Maren awaits.",))
_add("elite_four_maren", "Maren", "Elite Four",
     (_p("Feraligatr", 49, nature="Adamant", moves=("Hydro Pump", "Ice Punch", "Aqua Tail")),
      _p("Swampert", 49, nature="Adamant", moves=("Earthquake", "Hydro Pump", "Brine")),
      _p("Empoleon", 50, nature="Modest", moves=("Hydro Pump", "Flash Cannon", "Aqua Jet")),
      _p("Kingdra", 51, nature="Modest", ivs="perfect", held_item="Mystic Water", moves=("Hydro Pump", "Dragon Pulse", "Ice Beam", "Brine"))),
     AITier.EXPERT_TRAINER, 10100,
     pre=("Maren: The tide waits for no one. Let's see if you can keep your footing.",),
     win=("Maren: Every current eventually returns to the sea.",),
     lose=("Maren: You swim against the tide better than most. Zephyra's up next.",))
_add("elite_four_zephyra", "Zephyra", "Elite Four",
     (_p("Noctowl", 50, nature="Calm", moves=("Air Slash", "Psychic", "Hypnosis")),
      _p("Altaria", 50, nature="Bold", moves=("Dragon Pulse", "Aerial Ace", "Dragon Dance")),
      _p("Gardevoir", 51, nature="Modest", moves=("Psychic", "Shadow Ball", "Calm Mind", "Confusion")),
      _p("Togekiss", 52, nature="Modest", ivs="perfect", held_item="Leftovers", moves=("Air Slash", "Extreme Speed", "Ancient Power", "Psychic"))),
     AITier.EXPERT_TRAINER, 10400,
     pre=("Zephyra: The mind and the sky share the same secret: neither can truly be grounded.",),
     win=("Zephyra: Grace favors the prepared spirit.",),
     lose=("Zephyra: You soar higher than I expected. Draven is waiting, and he shows no mercy.",))
_add("elite_four_draven", "Draven", "Elite Four",
     (_p("Houndoom", 51, nature="Modest", moves=("Fire Blast", "Crunch", "Dark Pulse")),
      _p("Hydreigon", 51, nature="Modest", moves=("Dark Pulse", "Draco Meteor", "Crunch")),
      _p("Absol", 52, nature="Jolly", moves=("Night Slash", "Swords Dance", "Superpower", "Bite")),
      _p("Tyranitar", 53, nature="Adamant", ivs="perfect", held_item="Focus Sash", moves=("Stone Edge", "Crunch", "Earthquake", "Superpower"))),
     AITier.EXPERT_TRAINER, 10600,
     pre=("Draven: Darkness doesn't fight fair, and neither do I. Last chance to turn back.",),
     win=("Draven: In the end, the shadows always win.",),
     lose=("Draven: ...Heh. Go on. Astra's been waiting a long time for someone like you.",))

# ======================================================================
# Champion Astra
# ======================================================================
_add("champion_astra", "Astra", "Champion",
     (_p("Gengar", 52, nature="Timid", moves=("Shadow Ball", "Dark Pulse", "Sludge Bomb", "Confuse Ray")),
      _p("Noctowl", 52, nature="Calm", moves=("Air Slash", "Psychic", "Hypnosis")),
      _p("Milotic", 53, nature="Modest", moves=("Hydro Pump", "Ice Beam", "Aqua Tail", "Withdraw")),
      _p("Roserade", 53, nature="Modest", moves=("Sludge Bomb", "Giga Drain", "Energy Ball", "Sleep Powder")),
      _p("Bisharp", 54, nature="Adamant", moves=("Iron Head", "Night Slash", "Swords Dance", "Crunch")),
      _p("Dragonite", 56, nature="Adamant", ivs="perfect", held_item="Leftovers", moves=("Dragon Claw", "Hyper Beam", "Extreme Speed", "Dragon Dance"))),
     AITier.EXPERT_TRAINER, 25000,
     pre=("Astra: Every generation, every region has its champions. Show me which one you'll be.",),
     win=("Astra: The title stays with me -- for now. Train harder and come back.",),
     lose=("Astra: ...It's done. Virelia has a new Champion. Wear the title well.",))

# ======================================================================
# Generic route / gym-puzzle trainers (~20, flavor + obstacle battles)
# ======================================================================
_add("youngster_dale", "Youngster", "Youngster",
     (_p("Rattata", 5),), AITier.BASIC_TRAINER, 120,
     pre=("Dale: Hey! Bet my Rattata's faster than anything you've got!",),
     win=("Dale: Speed wins again!",), lose=("Dale: Aw, beaten already?",))
_add("lass_mira", "Lass", "Lass",
     (_p("Zigzagoon", 6),), AITier.BASIC_TRAINER, 150,
     pre=("Mira: My Zigzagoon may zigzag, but it always gets there in the end!",),
     win=("Mira: Told you it'd get there first!",), lose=("Mira: Oh well, off we zigzag.",))
_add("bug_catcher_theo", "Bug Catcher", "Bug Catcher",
     (_p("Wurmple", 6), _p("Ledyba", 7)), AITier.BASIC_TRAINER, 180,
     pre=("Theo: Wanna see my bug collection battle? Bramblegate's finest!",),
     win=("Theo: Bugs rule this hedge maze!",), lose=("Theo: Aw man, back to the maze I guess.",))
_add("youngster_cole", "Youngster", "Youngster",
     (_p("Rattata", 9), _p("Taillow", 9)), AITier.BASIC_TRAINER, 220,
     pre=("Cole: Two Pokemon, double the trouble!",),
     win=("Cole: Two's better than one!",), lose=("Cole: Guess two wasn't enough...",))
_add("lass_priya", "Lass", "Lass",
     (_p("Hoppip", 11), _p("Zigzagoon", 11)), AITier.BASIC_TRAINER, 260,
     pre=("Priya: My Hoppip just floats along, but don't underestimate it!",),
     win=("Priya: Floated right to victory!",), lose=("Priya: Down it goes... literally.",))
_add("hiker_grant", "Hiker", "Hiker",
     (_p("Geodude", 14), _p("Roggenrola", 14)), AITier.BASIC_TRAINER, 320,
     pre=("Grant: These mountain paths build strong Pokemon, and strong legs!",),
     win=("Grant: Solid as the rock we stand on!",), lose=("Grant: Hah, you've got some grit, kid.",))
_add("fisherman_dell", "Fisherman", "Fisherman",
     (_p("Magikarp", 13), _p("Barboach", 13)), AITier.BASIC_TRAINER, 300,
     pre=("Dell: Caught these two myself! Let's see what they can do.",),
     win=("Dell: The big one always gets away, except in battle!",), lose=("Dell: Reel it back in, I guess.",))
_add("battle_girl_sana", "Battle Girl", "Battle Girl",
     (_p("Croagunk", 16),), AITier.BASIC_TRAINER, 380,
     pre=("Sana: Fighting spirit is all you need. Let's go!",),
     win=("Sana: Spirit wins battles!",), lose=("Sana: Guess my spirit needs more training.",))
_add("school_kid_milo", "School Kid", "School Kid",
     (_p("Voltorb", 15), _p("Shinx", 15)), AITier.BASIC_TRAINER, 360,
     pre=("Milo: I studied type match-ups all week for this!",),
     win=("Milo: Just like the textbook said!",), lose=("Milo: Guess the textbook missed a chapter.",))
_add("picnicker_wendy", "Picnicker", "Picnicker",
     (_p("Skiploom", 12), _p("Spoink", 12)), AITier.BASIC_TRAINER, 280,
     pre=("Wendy: Care to join my picnic? After this battle, of course!",),
     win=("Wendy: Tea and victory, my favorite combo!",), lose=("Wendy: Oh dear, the sandwiches will have to wait.",))
_add("camper_rowan", "Camper", "Camper",
     (_p("Zigzagoon", 18), _p("Linoone", 18), _p("Taillow", 18)), AITier.BASIC_TRAINER, 440,
     pre=("Rowan: Set up camp, packed three Pokemon. Let's get a battle going!",),
     win=("Rowan: Nothing like a good battle by the campfire!",), lose=("Rowan: Well, back to setting up camp.",))
_add("falconer_reed", "Falconer", "Falconer",
     (_p("Wingull", 20), _p("Swellow", 20)), AITier.BASIC_TRAINER, 480,
     pre=("Reed: My birds have the whole sky memorized. Let's soar!",),
     win=("Reed: Nothing outflies my flock!",), lose=("Reed: Grounded again, huh.",))
_add("swimmer_kai", "Swimmer", "Swimmer",
     (_p("Buizel", 22), _p("Wingull", 22)), AITier.BASIC_TRAINER, 520,
     pre=("Kai: Race you -- Pokemon battle style!",),
     win=("Kai: Smooth sailing to victory!",), lose=("Kai: Guess I'll paddle back to shore.",))
_add("ruin_maniac_otto", "Ruin Maniac", "Ruin Maniac",
     (_p("Roggenrola", 24), _p("Boldore", 24)), AITier.BASIC_TRAINER, 560,
     pre=("Otto: These Terracalda ruins hide more than old rocks -- strong Pokemon too!",),
     win=("Otto: Ancient power never gets old!",), lose=("Otto: Guess these ruins have secrets left to give up.",))
_add("beauty_coral", "Beauty", "Beauty",
     (_p("Woobat", 26), _p("Swoobat", 26)), AITier.BASIC_TRAINER, 600,
     pre=("Coral: My Pokemon are as lovely as they are strong. Watch closely!",),
     win=("Coral: Beauty and strength, all in one!",), lose=("Coral: Oh! Well, I never lose my composure.",))
_add("black_belt_igor", "Black Belt", "Black Belt",
     (_p("Toxicroak", 28), _p("Zangoose", 28)), AITier.BASIC_TRAINER, 660,
     pre=("Igor: Fists and fangs! Let's see whose training runs deeper.",),
     win=("Igor: Discipline always prevails!",), lose=("Igor: Hmph. Worthy opponent.",))
_add("psychic_wanda", "Psychic", "Psychic",
     (_p("Spoink", 30), _p("Grumpig", 30), _p("Woobat", 30)), AITier.BASIC_TRAINER, 720,
     pre=("Wanda: I foresaw this battle... mostly. Let's find out how it ends.",),
     win=("Wanda: Just as I foresaw!",), lose=("Wanda: Hm, didn't see that coming at all.",))
_add("veteran_holt", "Veteran", "Veteran",
     (_p("Whiscash", 35), _p("Camerupt", 35), _p("Seviper", 35)), AITier.BASIC_TRAINER, 900,
     pre=("Holt: Decades of battling, and I still love a good challenge. Show me yours!",),
     win=("Holt: Experience wins out, every time.",), lose=("Holt: Ha! Reminds me of my glory days. Well fought.",))
_add("ace_trainer_mika", "Ace Trainer", "Ace Trainer",
     (_p("Zangoose", 38), _p("Linoone", 38), _p("Swellow", 38)), AITier.BASIC_TRAINER, 1000,
     pre=("Mika: I train Pokemon for a living -- literally. Bring your best!",),
     win=("Mika: Just another day at the office.",), lose=("Mika: Impressive! You might just have what it takes for the League.",))
_add("dragon_tamer_finn", "Dragon Tamer", "Dragon Tamer",
     (_p("Vibrava", 40), _p("Gabite", 40)), AITier.BASIC_TRAINER, 1100,
     pre=("Finn: Skyreach Summit's winds don't scare my dragons one bit. Ready?",),
     win=("Finn: Dragons don't back down from anyone!",), lose=("Finn: Whoa! Guess my dragons met their match.",))
