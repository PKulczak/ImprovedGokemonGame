"""Canonical name -> National Dex number map for every species used in this game.

This is the single source of truth both `data/species.py` and the one-off
`tools/prepare_pokemon_sprites.py` asset-prep script key off of, so a
species' fetched sprite folder name always matches its data entry.
"""

ROSTER = {
    # Starters
    "Chikorita": 152, "Bayleef": 153, "Meganium": 154,
    "Torchic": 255, "Combusken": 256, "Blaziken": 257,
    "Oshawott": 501, "Dewott": 502, "Samurott": 503,
    # Gym 1 Bug - Wren
    "Ledyba": 165, "Ledian": 166,
    "Wurmple": 265, "Silcoon": 266, "Beautifly": 267, "Cascoon": 268, "Dustox": 269,
    # Gym 2 Normal - Bartle
    "Bidoof": 399, "Bibarel": 400,
    "Lillipup": 506, "Herdier": 507, "Stoutland": 508,
    "Girafarig": 203,
    # Gym 3 Electric - Talia
    "Voltorb": 100, "Electrode": 101,
    "Shinx": 403, "Luxio": 404, "Luxray": 405,
    "Joltik": 595, "Galvantula": 596,
    # Gym 4 Poison - Orin
    "Spinarak": 167, "Ariados": 168,
    "Koffing": 109, "Weezing": 110,
    "Croagunk": 453, "Toxicroak": 454,
    # Gym 5 Ghost - Priscilla
    "Misdreavus": 200, "Mismagius": 429,
    "Duskull": 355, "Dusclops": 356, "Dusknoir": 477,
    "Snorunt": 361, "Froslass": 478,
    # Gym 6 Ice - Kade
    "Sneasel": 215, "Weavile": 461,
    "Vanillite": 582, "Vanillish": 583, "Vanilluxe": 584,
    "Snover": 459, "Abomasnow": 460,
    # Gym 7 Ground/Rock - Garrick
    "Geodude": 74, "Graveler": 75, "Golem": 76,
    "Drilbur": 529, "Excadrill": 530,
    "Rhyhorn": 111, "Rhydon": 112, "Rhyperior": 464,
    # Gym 8 Dragon - Serath
    "Druddigon": 621,
    "Trapinch": 328, "Vibrava": 329, "Flygon": 330,
    "Gible": 443, "Gabite": 444, "Garchomp": 445,
    # Elite Four #1 Fire - Ivor
    "Vulpix": 37, "Ninetales": 38,
    "Cyndaquil": 155, "Quilava": 156, "Typhlosion": 157,
    "Chimchar": 390, "Monferno": 391, "Infernape": 392,
    "Litwick": 607, "Lampent": 608, "Chandelure": 609,
    # Elite Four #2 Water - Maren
    "Totodile": 158, "Croconaw": 159, "Feraligatr": 160,
    "Mudkip": 258, "Marshtomp": 259, "Swampert": 260,
    "Piplup": 393, "Prinplup": 394, "Empoleon": 395,
    "Horsea": 116, "Seadra": 117, "Kingdra": 230,
    # Elite Four #3 Flying/Psychic - Zephyra
    "Hoothoot": 163, "Noctowl": 164,
    "Swablu": 333, "Altaria": 334,
    "Ralts": 280, "Kirlia": 281, "Gardevoir": 282,
    "Togepi": 175, "Togetic": 176, "Togekiss": 468,
    # Elite Four #4 Dark/Dragon - Draven
    "Absol": 359,
    "Houndour": 228, "Houndoom": 229,
    "Deino": 633, "Zweilous": 634, "Hydreigon": 635,
    "Larvitar": 246, "Pupitar": 247, "Tyranitar": 248,
    # Champion - Astra
    "Budew": 406, "Roselia": 315, "Roserade": 407,
    "Feebas": 349, "Milotic": 350,
    "Gastly": 92, "Haunter": 93, "Gengar": 94,
    "Pawniard": 624, "Bisharp": 625,
    "Dratini": 147, "Dragonair": 148, "Dragonite": 149,
    # Team Eclipse
    "Zubat": 41, "Golbat": 42,
    "Poochyena": 261, "Mightyena": 262,
    "Murkrow": 198, "Honchkrow": 430, "Sableye": 302,
    # Wild route filler
    "Rattata": 19, "Raticate": 20,
    "Zigzagoon": 263, "Linoone": 264,
    "Hoppip": 187, "Skiploom": 188, "Jumpluff": 189,
    "Taillow": 276, "Swellow": 277,
    "Whismur": 293, "Loudred": 294, "Exploud": 295,
    "Woobat": 527, "Swoobat": 528,
    "Magikarp": 129, "Gyarados": 130,
    "Wingull": 278, "Pelipper": 279,
    "Buizel": 418, "Floatzel": 419,
    "Skarmory": 227,
    "Roggenrola": 524, "Boldore": 525, "Gigalith": 526,
    "Yanma": 193, "Yanmega": 469,
    "Shroomish": 285, "Breloom": 286,
    "Zangoose": 335, "Seviper": 336,
    "Numel": 322, "Camerupt": 323,
    "Spoink": 325, "Grumpig": 326,
    "Barboach": 339, "Whiscash": 340,
    # Postgame / Victory Road rare
    "Bagon": 371, "Shelgon": 372, "Salamence": 373,
    "Beldum": 374, "Metang": 375, "Metagross": 376,
    "Riolu": 447, "Lucario": 448,
    # Legendaries (postgame, one per "spot")
    "Articuno": 144, "Zapdos": 145, "Moltres": 146,
    "Mew": 151,
    "Lugia": 249, "Ho-Oh": 250,
    "Suicune": 245,
    "Groudon": 383, "Rayquaza": 384,
    "Dialga": 483, "Palkia": 484, "Giratina": 487, "Regigigas": 486,
    "Reshiram": 643, "Zekrom": 644,
    "Jirachi": 385,
}
