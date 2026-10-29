from __future__ import annotations

import math
from pathlib import Path

import pygame

from data import SPECIES

from settings import (
    ASSET_DIR,
    TILE,
    COLORS,
    TYPE_COLORS,
)


# ============================================================
# FONT PIXEL BITMAP
# ============================================================
#
# Non utilizziamo più Consolas o i font di Windows.
# Ogni lettera viene disegnata direttamente pixel per pixel.
#
# In questo modo:
#
# - niente antialiasing
# - niente caratteri deformati
# - niente font "granati"
# - risultato coerente con la pixel art
#
# ============================================================


GLYPHS = {

    " ": (
        "000",
        "000",
        "000",
        "000",
        "000",
    ),

    "A": (
        "010",
        "101",
        "111",
        "101",
        "101",
    ),

    "B": (
        "110",
        "101",
        "110",
        "101",
        "110",
    ),

    "C": (
        "011",
        "100",
        "100",
        "100",
        "011",
    ),

    "D": (
        "110",
        "101",
        "101",
        "101",
        "110",
    ),

    "E": (
        "111",
        "100",
        "110",
        "100",
        "111",
    ),

    "F": (
        "111",
        "100",
        "110",
        "100",
        "100",
    ),

    "G": (
        "011",
        "100",
        "101",
        "101",
        "011",
    ),

    "H": (
        "101",
        "101",
        "111",
        "101",
        "101",
    ),

    "I": (
        "111",
        "010",
        "010",
        "010",
        "111",
    ),

    "J": (
        "001",
        "001",
        "001",
        "101",
        "010",
    ),

    "K": (
        "101",
        "101",
        "110",
        "101",
        "101",
    ),

    "L": (
        "100",
        "100",
        "100",
        "100",
        "111",
    ),

    "M": (
        "101",
        "111",
        "111",
        "101",
        "101",
    ),

    "N": (
        "101",
        "111",
        "111",
        "111",
        "101",
    ),

    "O": (
        "010",
        "101",
        "101",
        "101",
        "010",
    ),

    "P": (
        "110",
        "101",
        "110",
        "100",
        "100",
    ),

    "Q": (
        "010",
        "101",
        "101",
        "111",
        "011",
    ),

    "R": (
        "110",
        "101",
        "110",
        "101",
        "101",
    ),

    "S": (
        "011",
        "100",
        "010",
        "001",
        "110",
    ),

    "T": (
        "111",
        "010",
        "010",
        "010",
        "010",
    ),

    "U": (
        "101",
        "101",
        "101",
        "101",
        "111",
    ),

    "V": (
        "101",
        "101",
        "101",
        "101",
        "010",
    ),

    "W": (
        "101",
        "101",
        "111",
        "111",
        "101",
    ),

    "X": (
        "101",
        "101",
        "010",
        "101",
        "101",
    ),

    "Y": (
        "101",
        "101",
        "010",
        "010",
        "010",
    ),

    "Z": (
        "111",
        "001",
        "010",
        "100",
        "111",
    ),

    "0": (
        "111",
        "101",
        "101",
        "101",
        "111",
    ),

    "1": (
        "010",
        "110",
        "010",
        "010",
        "111",
    ),

    "2": (
        "110",
        "001",
        "010",
        "100",
        "111",
    ),

    "3": (
        "110",
        "001",
        "010",
        "001",
        "110",
    ),

    "4": (
        "101",
        "101",
        "111",
        "001",
        "001",
    ),

    "5": (
        "111",
        "100",
        "110",
        "001",
        "110",
    ),

    "6": (
        "011",
        "100",
        "111",
        "101",
        "111",
    ),

    "7": (
        "111",
        "001",
        "010",
        "010",
        "010",
    ),

    "8": (
        "111",
        "101",
        "111",
        "101",
        "111",
    ),

    "9": (
        "111",
        "101",
        "111",
        "001",
        "110",
    ),

    ".": (
        "000",
        "000",
        "000",
        "000",
        "010",
    ),

    ",": (
        "000",
        "000",
        "000",
        "010",
        "100",
    ),

    ":": (
        "000",
        "010",
        "000",
        "010",
        "000",
    ),

    ";": (
        "000",
        "010",
        "000",
        "010",
        "100",
    ),

    "!": (
        "010",
        "010",
        "010",
        "000",
        "010",
    ),

    "?": (
        "110",
        "001",
        "010",
        "000",
        "010",
    ),

    "-": (
        "000",
        "000",
        "111",
        "000",
        "000",
    ),

    "+": (
        "000",
        "010",
        "111",
        "010",
        "000",
    ),

    "/": (
        "001",
        "001",
        "010",
        "100",
        "100",
    ),

    "|": (
        "010",
        "010",
        "010",
        "010",
        "010",
    ),

    "'": (
        "010",
        "010",
        "000",
        "000",
        "000",
    ),

    "(": (
        "001",
        "010",
        "010",
        "010",
        "001",
    ),

    ")": (
        "100",
        "010",
        "010",
        "010",
        "100",
    ),

    ">": (
        "100",
        "010",
        "001",
        "010",
        "100",
    ),

    "<": (
        "001",
        "010",
        "100",
        "010",
        "001",
    ),

    "=": (
        "000",
        "111",
        "000",
        "111",
        "000",
    ),

    "_": (
        "000",
        "000",
        "000",
        "000",
        "111",
    ),
}


class PixelFont:

    def __init__(
        self,
        scale=1,
        spacing=1,
        line_spacing=2,
    ):

        self.scale = scale

        self.spacing = spacing

        self.line_spacing = line_spacing

        self.glyph_width = (
            3 * scale
        )

        self.glyph_height = (
            5 * scale
        )

    # --------------------------------------------------------
    # NORMALIZZAZIONE
    # --------------------------------------------------------

    def _normalize(
        self,
        value,
    ):

        value = str(
            value
        ).upper()

        replacements = {

            "À": "A",
            "Á": "A",
            "Â": "A",
            "Ä": "A",

            "È": "E",
            "É": "E",
            "Ê": "E",
            "Ë": "E",

            "Ì": "I",
            "Í": "I",
            "Î": "I",
            "Ï": "I",

            "Ò": "O",
            "Ó": "O",
            "Ô": "O",
            "Ö": "O",

            "Ù": "U",
            "Ú": "U",
            "Û": "U",
            "Ü": "U",
        }

        for original, replacement in (
            replacements.items()
        ):

            value = value.replace(
                original,
                replacement,
            )

        return value

    # --------------------------------------------------------
    # SIZE
    # --------------------------------------------------------

    def size(
        self,
        value,
    ):

        value = self._normalize(
            value
        )

        if not value:

            return (
                0,
                self.glyph_height,
            )

        width = (
            len(value)
            *
            self.glyph_width
        )

        width += (
            max(
                0,
                len(value) - 1,
            )
            *
            self.spacing
        )

        return (
            width,
            self.glyph_height,
        )

    # --------------------------------------------------------
    # LINE SIZE
    # --------------------------------------------------------

    def get_linesize(self):

        return (
            self.glyph_height
            +
            self.line_spacing
        )

    # --------------------------------------------------------
    # HEIGHT
    # --------------------------------------------------------

    def get_height(self):

        return self.glyph_height

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    def render(
        self,
        value,
        antialias,
        color,
        background=None,
    ):

        value = self._normalize(
            value
        )

        width, height = self.size(
            value
        )

        width = max(
            1,
            width,
        )

        surface = pygame.Surface(
            (
                width,
                height,
            ),
            pygame.SRCALPHA,
        )

        if background is not None:

            surface.fill(
                background
            )

        x_cursor = 0

        for char in value:

            glyph = GLYPHS.get(
                char,
                GLYPHS["?"],
            )

            for row, pattern in enumerate(
                glyph
            ):

                for column, pixel in enumerate(
                    pattern
                ):

                    if pixel != "1":
                        continue

                    pygame.draw.rect(
                        surface,
                        color,
                        (
                            x_cursor
                            +
                            column
                            *
                            self.scale,

                            row
                            *
                            self.scale,

                            self.scale,

                            self.scale,
                        ),
                    )

            x_cursor += (
                self.glyph_width
                +
                self.spacing
            )

        return surface


# ============================================================
# ASSETS
# ============================================================


class Assets:

    def __init__(self):

        self.cache: dict[
            tuple,
            pygame.Surface,
        ] = {}

        # ====================================================
        # FONT PIXEL
        # ====================================================
        #
        # Questi NON sono font Windows.
        #
        # Vengono renderizzati direttamente pixel per pixel.
        # ====================================================

        self.font_tiny = PixelFont(
            scale=1,
            spacing=0,
        )

        self.font_small = PixelFont(
            scale=1,
            spacing=1,
        )

        self.font = PixelFont(
            scale=1,
            spacing=1,
        )

        self.font_big = PixelFont(
            scale=2,
            spacing=1,
        )

        self.font_title = PixelFont(
            scale=2,
            spacing=2,
        )

    # ========================================================
    # LOAD
    # ========================================================

    def _load(
        self,
        path: Path,
        size=None,
    ):

        key = (
            "file",
            str(path),
            size,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        if not path.exists():

            return None

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            if (
                size
                and
                image.get_size()
                != size
            ):

                image = (
                    pygame.transform.scale(
                        image,
                        size,
                    )
                )

            self.cache[
                key
            ] = image

            return image

        except pygame.error:

            return None

    # ========================================================
    # SURFACE
    # ========================================================

    @staticmethod
    def surf(
        size,
    ):

        return pygame.Surface(
            size,
            pygame.SRCALPHA,
        )

    # ========================================================
    # TILE
    # ========================================================

    def tile(
        self,
        kind: str,
        frame=0,
        variant=0,
    ):

        names = {

            ".":
                f"grass_{variant % 2}.png",

            ",":
                f"tall_grass_{frame % 4}.png",

            ":":
                "path.png",

            "~":
                f"water_{frame % 4}.png",

            "=":
                "bridge.png",

            "#":
                f"tree_{variant % 2}.png",

            "r":
                f"rock_{variant % 2}.png",

            "f":
                f"flowers_{variant % 2}.png",

            "a":
                "altar_floor.png",

            "h":
                "house_floor.png",

            "c":
                "cliff.png",
        }

        path = (
            ASSET_DIR
            /
            "tiles"
            /
            names.get(
                kind,
                "grass_0.png",
            )
        )

        loaded = self._load(
            path,
            (
                TILE,
                TILE,
            ),
        )

        if loaded:

            return loaded

        key = (
            "tile",
            kind,
            frame % 4,
            variant % 2,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        surface = self._draw_tile(
            kind,
            frame,
            variant,
        )

        self.cache[
            key
        ] = surface

        return surface

    # ========================================================
    # GRASS
    # ========================================================

    def _base_grass(
        self,
        variant=0,
    ):

        surface = self.surf(
            (
                TILE,
                TILE,
            )
        )

        base = (

            COLORS[
                "grass"
            ]

            if
            variant % 2 == 0

            else

            (
                134,
                184,
                101,
            )
        )

        surface.fill(
            base
        )

        light = COLORS[
            "grass_light"
        ]

        dark = COLORS[
            "grass_dark"
        ]

        pattern = [

            (
                2,
                3,
            ),

            (
                11,
                2,
            ),

            (
                6,
                9,
            ),

            (
                14,
                13,
            ),

            (
                3,
                14,
            ),

            (
                9,
                6,
            ),
        ]

        for (
            index,
            (
                x,
                y,
            ),
        ) in enumerate(
            pattern
        ):

            surface.set_at(
                (
                    x,
                    y,
                ),
                (
                    light

                    if
                    (
                        index
                        +
                        variant
                    )
                    % 2

                    else

                    dark
                ),
            )

        return surface

    # ========================================================
    # DRAW TILE
    # ========================================================

    def _draw_tile(
        self,
        kind,
        frame,
        variant,
    ):

        surface = (
            self._base_grass(
                variant
            )
        )

        # ----------------------------------------------------
        # ERBA
        # ----------------------------------------------------

        if kind == ".":

            return surface

        # ----------------------------------------------------
        # SENTIERO
        # ----------------------------------------------------

        if kind == ":":

            surface.fill(
                COLORS[
                    "path"
                ]
            )

            pygame.draw.line(
                surface,
                COLORS[
                    "path_dark"
                ],
                (
                    0,
                    15,
                ),
                (
                    15,
                    15,
                ),
            )

            for (
                x,
                y,
            ) in (

                (
                    3,
                    4,
                ),

                (
                    12,
                    7,
                ),

                (
                    7,
                    12,
                ),

            ):

                surface.set_at(
                    (
                        x,
                        y,
                    ),
                    (
                        225,
                        205,
                        160,
                    ),
                )

            return surface

        # ----------------------------------------------------
        # ACQUA
        # ----------------------------------------------------

        if kind == "~":

            surface.fill(
                COLORS[
                    "water"
                ]
            )

            shift = (
                frame % 4
            )

            for y in (
                3,
                9,
                14,
            ):

                pygame.draw.line(
                    surface,
                    COLORS[
                        "water_light"
                    ],
                    (
                        (
                            y
                            +
                            shift
                        )
                        % 6,
                        y,
                    ),
                    (
                        11
                        +
                        shift,
                        y,
                    ),
                )

            pygame.draw.line(
                surface,
                (
                    47,
                    113,
                    163,
                ),
                (
                    0,
                    6,
                ),
                (
                    15,
                    6,
                ),
            )

            return surface

        # ----------------------------------------------------
        # PONTE
        # ----------------------------------------------------

        if kind == "=":

            surface.fill(
                (
                    103,
                    72,
                    48,
                )
            )

            for y in range(
                0,
                16,
                4,
            ):

                pygame.draw.rect(
                    surface,
                    (
                        177,
                        130,
                        76,
                    ),
                    (
                        0,
                        y,
                        16,
                        3,
                    ),
                )

                pygame.draw.line(
                    surface,
                    (
                        213,
                        170,
                        103,
                    ),
                    (
                        0,
                        y,
                    ),
                    (
                        15,
                        y,
                    ),
                )

            pygame.draw.line(
                surface,
                (
                    73,
                    55,
                    42,
                ),
                (
                    2,
                    0,
                ),
                (
                    2,
                    15,
                ),
            )

            pygame.draw.line(
                surface,
                (
                    73,
                    55,
                    42,
                ),
                (
                    13,
                    0,
                ),
                (
                    13,
                    15,
                ),
            )

            return surface

        # ----------------------------------------------------
        # ERBA ALTA
        # ----------------------------------------------------

        if kind == ",":

            sway = (

                (
                    -1,
                    0,
                    1,
                    0,
                )[
                    frame % 4
                ]
            )

            for (
                x,
                y,
            ) in (

                (
                    1,
                    5,
                ),

                (
                    5,
                    2,
                ),

                (
                    9,
                    6,
                ),

                (
                    13,
                    3,
                ),

                (
                    3,
                    11,
                ),

                (
                    11,
                    11,
                ),

            ):

                pygame.draw.line(
                    surface,
                    (
                        45,
                        105,
                        64,
                    ),
                    (
                        x,
                        y + 5,
                    ),
                    (
                        x + sway,
                        y,
                    ),
                    1,
                )

                pygame.draw.line(
                    surface,
                    (
                        72,
                        140,
                        70,
                    ),
                    (
                        x + 2,
                        y + 5,
                    ),
                    (
                        x + 2 - sway,
                        y + 1,
                    ),
                    1,
                )

            return surface

        # ----------------------------------------------------
        # ALBERO
        # ----------------------------------------------------

        if kind == "#":

            pygame.draw.rect(
                surface,
                (
                    91,
                    68,
                    44,
                ),
                (
                    7,
                    10,
                    3,
                    6,
                ),
            )

            pygame.draw.ellipse(
                surface,
                (
                    33,
                    76,
                    55,
                ),
                (
                    0,
                    2,
                    16,
                    13,
                ),
            )

            pygame.draw.ellipse(
                surface,
                COLORS[
                    "tree"
                ],
                (
                    1,
                    0,
                    14,
                    12,
                ),
            )

            pygame.draw.ellipse(
                surface,
                COLORS[
                    "tree_light"
                ],
                (
                    3,
                    1,
                    8,
                    6,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    113,
                    161,
                    92,
                ),
                (
                    5,
                    2,
                    3,
                    2,
                ),
            )

            return surface

        # ----------------------------------------------------
        # ROCCIA
        # ----------------------------------------------------

        if kind == "r":

            pygame.draw.polygon(
                surface,
                (
                    86,
                    81,
                    77,
                ),
                [

                    (
                        2,
                        13,
                    ),

                    (
                        4,
                        5,
                    ),

                    (
                        8,
                        2,
                    ),

                    (
                        13,
                        5,
                    ),

                    (
                        15,
                        13,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                COLORS[
                    "rock"
                ],
                [

                    (
                        3,
                        12,
                    ),

                    (
                        5,
                        5,
                    ),

                    (
                        8,
                        3,
                    ),

                    (
                        12,
                        6,
                    ),

                    (
                        14,
                        12,
                    ),
                ],
            )

            pygame.draw.line(
                surface,
                COLORS[
                    "rock_light"
                ],
                (
                    6,
                    5,
                ),
                (
                    10,
                    5,
                ),
            )

            return surface

        # ----------------------------------------------------
        # FIORI
        # ----------------------------------------------------

        if kind == "f":

            for (
                x,
                y,
                color,
            ) in (

                (
                    4,
                    5,
                    (
                        250,
                        241,
                        188,
                    ),
                ),

                (
                    11,
                    11,
                    (
                        238,
                        155,
                        145,
                    ),
                ),

            ):

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        x - 1,
                        y,
                        3,
                        1,
                    ),
                )

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        x,
                        y - 1,
                        1,
                        3,
                    ),
                )

                surface.set_at(
                    (
                        x,
                        y,
                    ),
                    (
                        245,
                        197,
                        77,
                    ),
                )

            return surface

        # ----------------------------------------------------
        # ALTARE
        # ----------------------------------------------------

        if kind == "a":

            surface.fill(
                (
                    173,
                    178,
                    151,
                )
            )

            pygame.draw.line(
                surface,
                (
                    195,
                    199,
                    172,
                ),
                (
                    0,
                    3,
                ),
                (
                    15,
                    3,
                ),
            )

            pygame.draw.line(
                surface,
                (
                    136,
                    142,
                    125,
                ),
                (
                    0,
                    14,
                ),
                (
                    15,
                    14,
                ),
            )

            return surface

        # ----------------------------------------------------
        # CASA
        # ----------------------------------------------------

        if kind == "h":

            surface.fill(
                (
                    218,
                    196,
                    151,
                )
            )

            pygame.draw.line(
                surface,
                (
                    190,
                    166,
                    122,
                ),
                (
                    0,
                    15,
                ),
                (
                    15,
                    15,
                ),
            )

            return surface

        # ----------------------------------------------------
        # RUPE
        # ----------------------------------------------------

        if kind == "c":

            surface.fill(
                COLORS[
                    "grass"
                ]
            )

            pygame.draw.rect(
                surface,
                (
                    120,
                    87,
                    62,
                ),
                (
                    0,
                    8,
                    16,
                    8,
                ),
            )

            pygame.draw.line(
                surface,
                (
                    161,
                    117,
                    77,
                ),
                (
                    0,
                    8,
                ),
                (
                    15,
                    8,
                ),
            )

            for x in (
                2,
                8,
                13,
            ):

                pygame.draw.line(
                    surface,
                    (
                        87,
                        68,
                        57,
                    ),
                    (
                        x,
                        10,
                    ),
                    (
                        x - 2,
                        15,
                    ),
                )

            return surface

        return surface

    # ========================================================
    # PLAYER
    # ========================================================

    def player(
        self,
        facing="down",
        frame=0,
    ):

        path = (
            ASSET_DIR
            /
            "player"
            /
            f"{facing}_{frame % 4}.png"
        )

        loaded = self._load(
            path,
            (
                16,
                24,
            ),
        )

        if loaded:

            return loaded

        key = (
            "player",
            facing,
            frame % 4,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        surface = (
            self._draw_person(
                (
                    200,
                    76,
                    60,
                ),
                facing,
                frame,
                hero=True,
            )
        )

        self.cache[
            key
        ] = surface

        return surface

    # ========================================================
    # NPC
    # ========================================================

    def npc(
        self,
        kind,
        facing="down",
        frame=0,
    ):

        path = (
            ASSET_DIR
            /
            "npcs"
            /
            f"{kind}_{facing}_{frame % 2}.png"
        )

        loaded = self._load(
            path,
            (
                16,
                24,
            ),
        )

        if loaded:

            return loaded

        palettes = {

            "clinic":
                (
                    234,
                    225,
                    203,
                ),

            "guide":
                (
                    82,
                    137,
                    91,
                ),

            "trainer0":
                (
                    82,
                    153,
                    119,
                ),

            "trainer1":
                (
                    80,
                    130,
                    185,
                ),

            "trainer2":
                (
                    155,
                    109,
                    171,
                ),
        }

        key = (
            "npc",
            kind,
            facing,
            frame % 2,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        surface = self._draw_person(
            palettes.get(
                kind,
                (
                    140,
                    120,
                    100,
                ),
            ),
            facing,
            frame,
            hero=False,
        )

        self.cache[
            key
        ] = surface

        return surface

    # ========================================================
    # PERSON
    # ========================================================

    def _draw_person(
        self,
        shirt,
        facing,
        frame,
        hero=False,
    ):

        surface = self.surf(
            (
                16,
                24,
            )
        )

        ink = COLORS[
            "ink"
        ]

        skin = (
            236,
            195,
            147,
        )

        hair = (
            75,
            52,
            43,
        )

        step = (
            0,
            1,
            0,
            -1,
        )[
            frame % 4
        ]

        pygame.draw.ellipse(
            surface,
            (
                0,
                0,
                0,
                70,
            ),
            (
                3,
                20,
                10,
                3,
            ),
        )

        pygame.draw.rect(
            surface,
            ink,
            (
                4
                +
                max(
                    step,
                    0,
                ),
                18,
                3,
                4,
            ),
        )

        pygame.draw.rect(
            surface,
            ink,
            (
                9
                +
                min(
                    step,
                    0,
                ),
                18,
                3,
                4,
            ),
        )

        pygame.draw.rect(
            surface,
            ink,
            (
                3,
                9,
                10,
                10,
            ),
        )

        pygame.draw.rect(
            surface,
            shirt,
            (
                4,
                10,
                8,
                8,
            ),
        )

        pygame.draw.rect(
            surface,
            skin,
            (
                4,
                3,
                8,
                7,
            ),
        )

        pygame.draw.rect(
            surface,
            hair,
            (
                3,
                2,
                10,
                4,
            ),
        )

        if hero:

            pygame.draw.rect(
                surface,
                (
                    204,
                    77,
                    60,
                ),
                (
                    3,
                    1,
                    10,
                    3,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    246,
                    222,
                    175,
                ),
                (
                    9,
                    2,
                    4,
                    1,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    48,
                    77,
                    105,
                ),
                (
                    3,
                    12,
                    2,
                    6,
                ),
            )

        if facing == "up":

            pygame.draw.rect(
                surface,
                hair,
                (
                    5,
                    5,
                    6,
                    5,
                ),
            )

        elif facing == "left":

            surface.set_at(
                (
                    5,
                    6,
                ),
                ink,
            )

        elif facing == "right":

            surface.set_at(
                (
                    10,
                    6,
                ),
                ink,
            )

        else:

            surface.set_at(
                (
                    6,
                    6,
                ),
                ink,
            )

            surface.set_at(
                (
                    10,
                    6,
                ),
                ink,
            )

        return surface

    # ========================================================
    # CREATURE
    # ========================================================

    def creature(
        self,
        species: str,
        side="front",
        frame=0,
        scale=1,
    ):

        path = (
            ASSET_DIR
            /
            "creatures"
            /
            f"{species}_{side}_{frame % 2}.png"
        )

        loaded = self._load(
            path
        )

        if loaded:

            if scale != 1:

                loaded = (
                    pygame.transform.scale(
                        loaded,
                        (
                            loaded.get_width()
                            *
                            scale,

                            loaded.get_height()
                            *
                            scale,
                        ),
                    )
                )

            return loaded

        key = (
            "creature",
            species,
            side,
            frame % 2,
            scale,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        base = (
            self._draw_creature(
                species,
                side,
                frame,
            )
        )

        if scale != 1:

            base = pygame.transform.scale(
                base,
                (
                    base.get_width()
                    *
                    scale,

                    base.get_height()
                    *
                    scale,
                ),
            )

        self.cache[
            key
        ] = base

        return base

    # ========================================================
    # DRAW CREATURE
    # ========================================================

    def _draw_creature(
        self,
        species,
        side,
        frame,
    ):

        surface = self.surf(
            (
                48,
                48,
            )
        )

        palette = SPECIES[
            species
        ][
            "palette"
        ]

        (
            dark,
            base,
            light,
            pale,
        ) = palette

        bob = (
            frame % 2
        )

        pygame.draw.ellipse(
            surface,
            (
                0,
                0,
                0,
                55,
            ),
            (
                9,
                39,
                30,
                5,
            ),
        )

        # ----------------------------------------------------
        # GERMILLO
        # ----------------------------------------------------

        if species == "germillo":

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    10,
                    14 + bob,
                    29,
                    27,
                ),
            )

            pygame.draw.ellipse(
                surface,
                base,
                (
                    12,
                    13 + bob,
                    25,
                    26,
                ),
            )

            pygame.draw.ellipse(
                surface,
                light,
                (
                    16,
                    25 + bob,
                    16,
                    12,
                ),
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        18,
                        17 + bob,
                    ),

                    (
                        9,
                        4 + bob,
                    ),

                    (
                        22,
                        10 + bob,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        19,
                        15 + bob,
                    ),

                    (
                        12,
                        6 + bob,
                    ),

                    (
                        22,
                        11 + bob,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        28,
                        14 + bob,
                    ),

                    (
                        36,
                        2 + bob,
                    ),

                    (
                        34,
                        18 + bob,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        29,
                        14 + bob,
                    ),

                    (
                        35,
                        5 + bob,
                    ),

                    (
                        33,
                        18 + bob,
                    ),
                ],
            )

        # ----------------------------------------------------
        # BRACIOTTO
        # ----------------------------------------------------

        elif species == "braciotto":

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    9,
                    13 + bob,
                    29,
                    28,
                ),
            )

            pygame.draw.ellipse(
                surface,
                base,
                (
                    11,
                    12 + bob,
                    25,
                    27,
                ),
            )

            pygame.draw.ellipse(
                surface,
                pale,
                (
                    17,
                    27 + bob,
                    13,
                    10,
                ),
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        35,
                        32,
                    ),

                    (
                        44,
                        19,
                    ),

                    (
                        42,
                        37,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                (
                    237,
                    79,
                    48,
                ),
                [

                    (
                        38,
                        32,
                    ),

                    (
                        44,
                        22,
                    ),

                    (
                        43,
                        37,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        40,
                        31,
                    ),

                    (
                        44,
                        26,
                    ),

                    (
                        43,
                        35,
                    ),
                ],
            )

        # ----------------------------------------------------
        # ONDINO
        # ----------------------------------------------------

        elif species == "ondino":

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    8,
                    12 + bob,
                    30,
                    29,
                ),
            )

            pygame.draw.ellipse(
                surface,
                base,
                (
                    10,
                    11 + bob,
                    26,
                    28,
                ),
            )

            pygame.draw.ellipse(
                surface,
                pale,
                (
                    15,
                    26 + bob,
                    17,
                    11,
                ),
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        22,
                        12 + bob,
                    ),

                    (
                        24,
                        1 + bob,
                    ),

                    (
                        28,
                        13 + bob,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        23,
                        11 + bob,
                    ),

                    (
                        25,
                        4 + bob,
                    ),

                    (
                        27,
                        12 + bob,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                base,
                [

                    (
                        9,
                        23,
                    ),

                    (
                        2,
                        19,
                    ),

                    (
                        5,
                        29,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                base,
                [

                    (
                        36,
                        23,
                    ),

                    (
                        44,
                        18,
                    ),

                    (
                        41,
                        30,
                    ),
                ],
            )

        # ----------------------------------------------------
        # CIOTTOLO
        # ----------------------------------------------------

        elif species == "ciottolo":

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        10,
                        38,
                    ),

                    (
                        12,
                        14,
                    ),

                    (
                        23,
                        6,
                    ),

                    (
                        37,
                        15,
                    ),

                    (
                        39,
                        39,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                base,
                [

                    (
                        12,
                        37,
                    ),

                    (
                        14,
                        15,
                    ),

                    (
                        23,
                        9,
                    ),

                    (
                        35,
                        17,
                    ),

                    (
                        37,
                        37,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        16,
                        16,
                    ),

                    (
                        23,
                        11,
                    ),

                    (
                        29,
                        17,
                    ),

                    (
                        20,
                        18,
                    ),
                ],
            )

        # ----------------------------------------------------
        # ALAFOGLIA
        # ----------------------------------------------------

        elif species == "alafoglia":

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    15,
                    12 + bob,
                    20,
                    29,
                ),
            )

            pygame.draw.ellipse(
                surface,
                base,
                (
                    17,
                    12 + bob,
                    16,
                    27,
                ),
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        17,
                        23,
                    ),

                    (
                        3,
                        11,
                    ),

                    (
                        12,
                        29,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        17,
                        22,
                    ),

                    (
                        5,
                        13,
                    ),

                    (
                        13,
                        27,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        32,
                        23,
                    ),

                    (
                        45,
                        10,
                    ),

                    (
                        37,
                        29,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        31,
                        22,
                    ),

                    (
                        42,
                        13,
                    ),

                    (
                        36,
                        27,
                    ),
                ],
            )

        # ----------------------------------------------------
        # NIMBAT
        # ----------------------------------------------------

        else:

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    15,
                    13 + bob,
                    19,
                    28,
                ),
            )

            pygame.draw.ellipse(
                surface,
                base,
                (
                    17,
                    13 + bob,
                    15,
                    26,
                ),
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        16,
                        22,
                    ),

                    (
                        1,
                        12,
                    ),

                    (
                        9,
                        30,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        16,
                        21,
                    ),

                    (
                        4,
                        14,
                    ),

                    (
                        10,
                        27,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                dark,
                [

                    (
                        32,
                        22,
                    ),

                    (
                        46,
                        11,
                    ),

                    (
                        39,
                        30,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                light,
                [

                    (
                        32,
                        21,
                    ),

                    (
                        43,
                        14,
                    ),

                    (
                        38,
                        27,
                    ),
                ],
            )

        # ----------------------------------------------------
        # FRONT / BACK
        # ----------------------------------------------------

        if side == "front":

            pygame.draw.rect(
                surface,
                pale,
                (
                    18,
                    20 + bob,
                    4,
                    5,
                ),
            )

            pygame.draw.rect(
                surface,
                pale,
                (
                    28,
                    20 + bob,
                    4,
                    5,
                ),
            )

            pygame.draw.rect(
                surface,
                dark,
                (
                    20,
                    21 + bob,
                    2,
                    4,
                ),
            )

            pygame.draw.rect(
                surface,
                dark,
                (
                    28,
                    21 + bob,
                    2,
                    4,
                ),
            )

            pygame.draw.rect(
                surface,
                dark,
                (
                    23,
                    28 + bob,
                    5,
                    2,
                ),
            )

        else:

            pygame.draw.ellipse(
                surface,
                dark,
                (
                    17,
                    19 + bob,
                    15,
                    9,
                ),
                1,
            )

        return surface

    # ========================================================
    # BALL
    # ========================================================

    def ball(
        self,
        frame=0,
    ):

        path = (
            ASSET_DIR
            /
            "effects"
            /
            f"capture_ball_{frame % 2}.png"
        )

        loaded = self._load(
            path,
            (
                12,
                12,
            ),
        )

        if loaded:

            return loaded

        key = (
            "ball",
            frame % 2,
        )

        if key in self.cache:

            return self.cache[
                key
            ]

        surface = self.surf(
            (
                12,
                12,
            )
        )

        pygame.draw.circle(
            surface,
            COLORS[
                "ink"
            ],
            (
                6,
                6,
            ),
            5,
        )

        pygame.draw.arc(
            surface,
            (
                223,
                83,
                75,
            ),
            (
                2,
                2,
                8,
                8,
            ),
            math.pi,
            math.tau,
            4,
        )

        pygame.draw.arc(
            surface,
            (
                239,
                238,
                217,
            ),
            (
                2,
                2,
                8,
                8,
            ),
            0,
            math.pi,
            4,
        )

        pygame.draw.line(
            surface,
            COLORS[
                "ink"
            ],
            (
                1,
                6,
            ),
            (
                11,
                6,
            ),
            2,
        )

        pygame.draw.circle(
            surface,
            COLORS[
                "panel"
            ],
            (
                6,
                6,
            ),
            2,
        )

        self.cache[
            key
        ] = surface

        return surface