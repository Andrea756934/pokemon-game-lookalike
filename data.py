SPECIES = {
    "germillo": {
        "name": "Germillo", "type": "Erba", "hp": 28, "atk": 12, "def": 12, "spd": 12,
        "palette": ((65, 119, 65), (102, 174, 86), (155, 208, 105), (226, 232, 177)),
    },
    "braciotto": {
        "name": "Braciotto", "type": "Fuoco", "hp": 25, "atk": 15, "def": 10, "spd": 15,
        "palette": ((124, 58, 47), (220, 91, 58), (244, 146, 74), (253, 211, 132)),
    },
    "ondino": {
        "name": "Ondino", "type": "Acqua", "hp": 31, "atk": 11, "def": 14, "spd": 10,
        "palette": ((48, 89, 127), (73, 151, 196), (122, 196, 221), (217, 240, 237)),
    },
    "ciottolo": {
        "name": "Ciottolo", "type": "Roccia", "hp": 34, "atk": 14, "def": 18, "spd": 7,
        "palette": ((80, 73, 68), (133, 121, 106), (184, 169, 143), (229, 219, 190)),
    },
    "alafoglia": {
        "name": "Alafoglia", "type": "Erba", "hp": 24, "atk": 13, "def": 10, "spd": 18,
        "palette": ((42, 96, 61), (77, 157, 76), (133, 199, 96), (213, 235, 169)),
    },
    "nimbat": {
        "name": "Nimbat", "type": "Normale", "hp": 27, "atk": 12, "def": 11, "spd": 17,
        "palette": ((61, 55, 77), (114, 101, 145), (173, 158, 194), (232, 221, 236)),
    },
}

STARTERS = ("germillo", "braciotto", "ondino")

MOVESETS = {
    "Erba": [
        {"name": "Balzo", "type": "Normale", "power": 11, "pp": 20},
        {"name": "Foglia Lama", "type": "Erba", "power": 17, "pp": 15},
        {"name": "Scatto", "type": "Normale", "power": 9, "pp": 10},
        {"name": "Ristoro", "type": "Erba", "power": 0, "pp": 5, "heal": 0.38},
    ],
    "Fuoco": [
        {"name": "Balzo", "type": "Normale", "power": 11, "pp": 20},
        {"name": "Fiammella", "type": "Fuoco", "power": 17, "pp": 15},
        {"name": "Scatto", "type": "Normale", "power": 9, "pp": 10},
        {"name": "Ristoro", "type": "Fuoco", "power": 0, "pp": 5, "heal": 0.38},
    ],
    "Acqua": [
        {"name": "Balzo", "type": "Normale", "power": 11, "pp": 20},
        {"name": "Ondina", "type": "Acqua", "power": 17, "pp": 15},
        {"name": "Scatto", "type": "Normale", "power": 9, "pp": 10},
        {"name": "Ristoro", "type": "Acqua", "power": 0, "pp": 5, "heal": 0.38},
    ],
    "Roccia": [
        {"name": "Balzo", "type": "Normale", "power": 11, "pp": 20},
        {"name": "Sassata", "type": "Roccia", "power": 18, "pp": 15},
        {"name": "Scatto", "type": "Normale", "power": 9, "pp": 10},
        {"name": "Ristoro", "type": "Roccia", "power": 0, "pp": 5, "heal": 0.35},
    ],
    "Normale": [
        {"name": "Balzo", "type": "Normale", "power": 12, "pp": 20},
        {"name": "Eco", "type": "Normale", "power": 16, "pp": 15},
        {"name": "Scatto", "type": "Normale", "power": 10, "pp": 10},
        {"name": "Ristoro", "type": "Normale", "power": 0, "pp": 5, "heal": 0.35},
    ],
}

TRAINERS = [
    {
        "name": "Mira", "pos": (11, 11), "facing": "down", "sprite": "trainer0",
        "team": [("nimbat", 5)], "reward": 65,
        "line": "Vediamo se sai scegliere il momento giusto!",
    },
    {
        "name": "Nerio", "pos": (27, 16), "facing": "left", "sprite": "trainer1",
        "team": [("ondino", 7), ("alafoglia", 7)], "reward": 95,
        "line": "Una squadra varia vale piu' della forza bruta.",
    },
    {
        "name": "Alba", "pos": (30, 5), "facing": "down", "sprite": "trainer2",
        "team": [("braciotto", 9), ("ciottolo", 9), ("germillo", 10)], "reward": 160,
        "line": "Ultima prova. Fammi vedere quanto siete cresciuti!",
    },
]

TYPE_CHART = {
    ("Fuoco", "Erba"): 1.6,
    ("Acqua", "Fuoco"): 1.6,
    ("Acqua", "Roccia"): 1.6,
    ("Erba", "Acqua"): 1.6,
    ("Erba", "Roccia"): 1.6,
    ("Roccia", "Fuoco"): 1.6,
    ("Fuoco", "Acqua"): 0.65,
    ("Fuoco", "Roccia"): 0.65,
    ("Acqua", "Erba"): 0.65,
    ("Erba", "Fuoco"): 0.65,
    ("Normale", "Roccia"): 0.65,
}

def effectiveness(attacking, defending):
    if attacking == defending and attacking != "Normale":
        return 0.75
    return TYPE_CHART.get((attacking, defending), 1.0)
