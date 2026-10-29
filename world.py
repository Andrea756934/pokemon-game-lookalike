from __future__ import annotations

import random

import pygame

from models import NPC
from settings import TILE


class World:

    def __init__(
        self,
        seed=72,
    ):

        self.rng = random.Random(
            seed
        )

        # ====================================================
        # DIMENSIONI MONDO
        # ====================================================
        #
        # Vecchia mappa circa:
        # 40 x 28
        #
        # Nuova:
        # 72 x 52
        #
        # ====================================================

        self.w = 72
        self.h = 52

        self.grid = [

            [
                "."
                for _ in range(
                    self.w
                )
            ]

            for _ in range(
                self.h
            )
        ]

        # Spawn nel villaggio sud-ovest

        self.spawn = (
            10.5 * TILE,
            46.5 * TILE,
        )

        # ----------------------------------------------------
        # NPC
        # ----------------------------------------------------

        self.npcs = [

            NPC(
                "clinic",
                14,
                43,
            ),

            NPC(
                "guide",
                18,
                45,
            ),

            # MIRA
            NPC(
                "trainer0",
                22,
                29,
                0,
            ),

            # NERIO
            NPC(
                "trainer1",
                51,
                31,
                1,
            ),

            # ALBA
            NPC(
                "trainer2",
                59,
                8,
                2,
            ),
        ]

        # ----------------------------------------------------
        # BAULI
        # ----------------------------------------------------

        self.chests = {

            "chest0":
                (
                    27,
                    39,
                ),

            "chest1":
                (
                    8,
                    25,
                ),

            "chest2":
                (
                    31,
                    13,
                ),

            "chest3":
                (
                    46,
                    26,
                ),

            "chest4":
                (
                    64,
                    39,
                ),

            "chest5":
                (
                    62,
                    15,
                ),
        }

        # Casa principale

        self.house_rect = (
            5,
            40,
            8,
            5,
        )

        # Santuario di Alba

        self.shrine_rect = (
            55,
            4,
            10,
            7,
        )

        self.build()

    # ========================================================
    # UTILITY
    # ========================================================

    def inside(
        self,
        x,
        y,
    ):

        return (
            0 <= x < self.w
            and
            0 <= y < self.h
        )

    def tile(
        self,
        x,
        y,
    ):

        if not self.inside(
            x,
            y,
        ):

            return "#"

        return self.grid[
            y
        ][
            x
        ]

    def set_tile(
        self,
        x,
        y,
        value,
    ):

        if self.inside(
            x,
            y,
        ):

            self.grid[
                y
            ][
                x
            ] = value

    # ========================================================
    # PATCH
    # ========================================================

    def patch(
        self,
        x1,
        y1,
        x2,
        y2,
        kind,
        chance=1.0,
        only_ground=True,
    ):

        for y in range(
            y1,
            y2 + 1,
        ):

            for x in range(
                x1,
                x2 + 1,
            ):

                if not self.inside(
                    x,
                    y,
                ):

                    continue

                if (
                    only_ground
                    and
                    self.grid[y][x]
                    != "."
                ):

                    continue

                if (
                    self.rng.random()
                    <= chance
                ):

                    self.grid[
                        y
                    ][
                        x
                    ] = kind

    # ========================================================
    # SENTIERI
    # ========================================================

    def path_segment(
        self,
        start,
        end,
        width=1,
    ):

        x, y = start

        end_x, end_y = end

        while True:

            radius = (
                width - 1
            )

            for oy in range(
                -radius,
                radius + 1,
            ):

                for ox in range(
                    -radius,
                    radius + 1,
                ):

                    px = x + ox
                    py = y + oy

                    if not self.inside(
                        px,
                        py,
                    ):

                        continue

                    # Se attraversiamo il fiume
                    # creiamo automaticamente un ponte.

                    if (
                        self.grid[py][px]
                        == "~"
                    ):

                        self.grid[
                            py
                        ][
                            px
                        ] = "="

                    else:

                        self.grid[
                            py
                        ][
                            px
                        ] = ":"

            if (
                x == end_x
                and
                y == end_y
            ):

                break

            if x != end_x:

                x += (
                    1
                    if end_x > x
                    else -1
                )

            elif y != end_y:

                y += (
                    1
                    if end_y > y
                    else -1
                )

    def path(
        self,
        *points,
        width=1,
    ):

        for index in range(
            len(points) - 1
        ):

            self.path_segment(
                points[index],
                points[index + 1],
                width,
            )

    # ========================================================
    # BUILD
    # ========================================================

    def build(self):

        # ====================================================
        # BORDI DEL MONDO
        # ====================================================

        for y in range(
            self.h
        ):

            for x in range(
                self.w
            ):

                if (
                    x < 2
                    or
                    y < 2
                    or
                    x >= self.w - 2
                    or
                    y >= self.h - 2
                ):

                    self.grid[
                        y
                    ][
                        x
                    ] = "#"

        # ====================================================
        # FIUME PRINCIPALE
        # ====================================================

        for y in range(
            2,
            self.h - 2,
        ):

            # Il fiume cambia leggermente
            # posizione lungo il percorso.

            if y < 17:

                river_x = 39

            elif y < 31:

                river_x = 38

            elif y < 42:

                river_x = 39

            else:

                river_x = 40

            for x in range(
                river_x - 1,
                river_x + 2,
            ):

                self.set_tile(
                    x,
                    y,
                    "~",
                )

        # ====================================================
        # FORESTA OCCIDENTALE
        # ====================================================

        self.patch(
            3,
            18,
            10,
            36,
            "#",
            .77,
        )

        self.patch(
            12,
            18,
            17,
            25,
            "#",
            .62,
        )

        self.patch(
            27,
            21,
            34,
            31,
            "#",
            .55,
        )

        self.patch(
            4,
            6,
            12,
            15,
            "#",
            .72,
        )

        self.patch(
            16,
            5,
            22,
            11,
            "#",
            .62,
        )

        # ====================================================
        # FORESTA EST
        # ====================================================

        self.patch(
            43,
            36,
            51,
            48,
            "#",
            .62,
        )

        self.patch(
            60,
            27,
            68,
            35,
            "#",
            .67,
        )

        self.patch(
            43,
            5,
            49,
            14,
            "#",
            .62,
        )

        self.patch(
            65,
            4,
            68,
            17,
            "#",
            .78,
        )

        # ====================================================
        # ROCCE
        # ====================================================

        rock_positions = [

            (
                25,
                10,
            ),

            (
                28,
                11,
            ),

            (
                31,
                9,
            ),

            (
                28,
                15,
            ),

            (
                48,
                18,
            ),

            (
                51,
                17,
            ),

            (
                54,
                20,
            ),

            (
                60,
                21,
            ),

            (
                63,
                22,
            ),

            (
                66,
                20,
            ),

            (
                24,
                33,
            ),

            (
                30,
                34,
            ),

            (
                55,
                39,
            ),

            (
                59,
                42,
            ),

            (
                66,
                44,
            ),
        ]

        for (
            x,
            y,
        ) in rock_positions:

            self.set_tile(
                x,
                y,
                "r",
            )

        # ====================================================
        # RUPE / ZONA ROCCIOSA NORD
        # ====================================================

        for x in range(
            23,
            36,
        ):

            if (
                x
                not in (
                    28,
                    29,
                )
            ):

                self.set_tile(
                    x,
                    5,
                    "c",
                )

        for x in range(
            46,
            55,
        ):

            self.set_tile(
                x,
                12,
                "c",
            )

        # ====================================================
        # ERBA ALTA
        # ====================================================

        # Bosco sud-ovest

        self.patch(
            14,
            33,
            25,
            39,
            ",",
            .78,
        )

        # Bosco Mira

        self.patch(
            17,
            24,
            28,
            32,
            ",",
            .76,
        )

        # Pianura nord-ovest

        self.patch(
            24,
            7,
            35,
            18,
            ",",
            .67,
        )

        # Est centrale

        self.patch(
            43,
            23,
            57,
            33,
            ",",
            .72,
        )

        # Est sud

        self.patch(
            52,
            37,
            67,
            47,
            ",",
            .64,
        )

        # Santuario

        self.patch(
            51,
            12,
            63,
            19,
            ",",
            .55,
        )

        # ====================================================
        # FIORI
        # ====================================================

        for _ in range(
            180
        ):

            x = self.rng.randrange(
                2,
                self.w - 2,
            )

            y = self.rng.randrange(
                2,
                self.h - 2,
            )

            if (
                self.grid[y][x]
                == "."
                and
                self.rng.random()
                < .68
            ):

                self.grid[
                    y
                ][
                    x
                ] = "f"

        # ====================================================
        # CASA / RIFUGIO
        # ====================================================

        hx, hy, hw, hh = (
            self.house_rect
        )

        for y in range(
            hy,
            hy + hh,
        ):

            for x in range(
                hx,
                hx + hw,
            ):

                self.set_tile(
                    x,
                    y,
                    "h",
                )

        # ====================================================
        # SANTUARIO
        # ====================================================

        sx, sy, sw, sh = (
            self.shrine_rect
        )

        for y in range(
            sy,
            sy + sh,
        ):

            for x in range(
                sx,
                sx + sw,
            ):

                self.set_tile(
                    x,
                    y,
                    "a",
                )

        # ====================================================
        # STRADE PRINCIPALI
        # ====================================================

        # Villaggio -> centro

        self.path(

            (
                10,
                46,
            ),

            (
                18,
                46,
            ),

            (
                18,
                37,
            ),

            (
                29,
                37,
            ),

            width=2,
        )

        # Centro -> Mira

        self.path(

            (
                18,
                37,
            ),

            (
                18,
                29,
            ),

            (
                22,
                29,
            ),

            width=1,
        )

        # Mira -> nord ovest

        self.path(

            (
                22,
                29,
            ),

            (
                22,
                19,
            ),

            (
                29,
                19,
            ),

            (
                29,
                11,
            ),

            width=1,
        )

        # Centro -> primo ponte

        self.path(

            (
                29,
                37,
            ),

            (
                34,
                37,
            ),

            (
                34,
                34,
            ),

            (
                45,
                34,
            ),

            (
                51,
                31,
            ),

            width=1,
        )

        # Nerio -> nord-est

        self.path(

            (
                51,
                31,
            ),

            (
                54,
                31,
            ),

            (
                54,
                22,
            ),

            (
                58,
                22,
            ),

            (
                58,
                14,
            ),

            (
                59,
                9,
            ),

            width=1,
        )

        # Strada est verso sud

        self.path(

            (
                51,
                31,
            ),

            (
                58,
                31,
            ),

            (
                58,
                40,
            ),

            (
                65,
                40,
            ),

            width=1,
        )

        # Secondo ponte, più a nord

        self.path(

            (
                29,
                19,
            ),

            (
                33,
                19,
            ),

            (
                44,
                19,
            ),

            (
                48,
                18,
            ),

            width=1,
        )

        # ====================================================
        # PONTI PIÙ LARGHI
        # ====================================================

        # Ponte centrale

        for y in (
            33,
            34,
            35,
        ):

            for x in range(
                37,
                42,
            ):

                if (
                    self.tile(
                        x,
                        y,
                    )
                    in (
                        "~",
                        ":",
                        "=",
                    )
                ):

                    self.set_tile(
                        x,
                        y,
                        "=",
                    )

        # Ponte nord

        for y in (
            18,
            19,
            20,
        ):

            for x in range(
                36,
                41,
            ):

                if (
                    self.tile(
                        x,
                        y,
                    )
                    in (
                        "~",
                        ":",
                        "=",
                    )
                ):

                    self.set_tile(
                        x,
                        y,
                        "=",
                    )

        # ====================================================
        # SPAWN LIBERO
        # ====================================================

        for y in range(
            44,
            49,
        ):

            for x in range(
                8,
                13,
            ):

                if (
                    self.tile(
                        x,
                        y,
                    )
                    not in (
                        "h",
                    )
                ):

                    self.set_tile(
                        x,
                        y,
                        ":",
                    )

        # ====================================================
        # SPAZI NPC
        # ====================================================

        for npc in (
            self.npcs
        ):

            # Il tile sotto all'NPC diventa terreno
            # percorribile/path.

            if (
                self.tile(
                    npc.x,
                    npc.y,
                )
                not in (
                    "a",
                )
            ):

                self.set_tile(
                    npc.x,
                    npc.y,
                    ":",
                )

        # ====================================================
        # SPAZI BAULI
        # ====================================================

        for (
            x,
            y,
        ) in (
            self.chests.values()
        ):

            if (
                self.tile(
                    x,
                    y,
                )
                in (
                    "#",
                    "r",
                    "c",
                    "~",
                )
            ):

                self.set_tile(
                    x,
                    y,
                    ".",
                )

    # ========================================================
    # SOLID
    # ========================================================

    def solid_tile(
        self,
        x,
        y,
    ):

        return (
            self.tile(
                x,
                y,
            )
            in (
                "#",
                "~",
                "r",
                "c",
                "h",
            )
        )

    # ========================================================
    # ENTITY AT
    # ========================================================

    def entity_at(
        self,
        x,
        y,
    ):

        for npc in (
            self.npcs
        ):

            if (
                npc.x == x
                and
                npc.y == y
            ):

                return npc

        for (
            name,
            (
                chest_x,
                chest_y,
            ),
        ) in (
            self.chests.items()
        ):

            if (
                chest_x == x
                and
                chest_y == y
            ):

                return name

        return None

    # ========================================================
    # COLLISION
    # ========================================================

    def collide_rect(
        self,
        rect,
    ):

        left = (
            rect.left
            // TILE
        )

        right = (
            (
                rect.right
                - 1
            )
            // TILE
        )

        top = (
            rect.top
            // TILE
        )

        bottom = (
            (
                rect.bottom
                - 1
            )
            // TILE
        )

        for y in range(
            top,
            bottom + 1,
        ):

            for x in range(
                left,
                right + 1,
            ):

                if (
                    self.solid_tile(
                        x,
                        y,
                    )
                ):

                    return True

                if (
                    self.entity_at(
                        x,
                        y,
                    )
                    is not None
                ):

                    return True

        return False

    # ========================================================
    # DRAW MAPPA
    # ========================================================

    def draw(
        self,
        surface,
        assets,
        camera,
        open_chests,
        t,
    ):

        camera_x = int(
            camera.x
        )

        camera_y = int(
            camera.y
        )

        width = (
            surface.get_width()
        )

        height = (
            surface.get_height()
        )

        start_x = max(
            0,
            camera_x
            // TILE
            - 2,
        )

        end_x = min(

            self.w,

            (
                camera_x
                +
                width
            )
            // TILE
            + 3,
        )

        start_y = max(
            0,
            camera_y
            // TILE
            - 2,
        )

        end_y = min(

            self.h,

            (
                camera_y
                +
                height
            )
            // TILE
            + 3,
        )

        frame = (
            int(
                t * 4
            )
            % 4
        )

        # ----------------------------------------------------
        # TILE
        # ----------------------------------------------------

        for y in range(
            start_y,
            end_y,
        ):

            for x in range(
                start_x,
                end_x,
            ):

                kind = (
                    self.tile(
                        x,
                        y,
                    )
                )

                tile_frame = (

                    frame

                    if
                    kind
                    in (
                        ",",
                        "~",
                    )

                    else

                    0
                )

                image = (
                    assets.tile(

                        kind,

                        tile_frame,

                        (
                            x
                            +
                            y
                        )
                        & 1,
                    )
                )

                surface.blit(
                    image,
                    (
                        x
                        * TILE
                        -
                        camera_x,

                        y
                        * TILE
                        -
                        camera_y,
                    ),
                )

        # ----------------------------------------------------
        # CASA
        # ----------------------------------------------------

        self.draw_house(
            surface,
            camera_x,
            camera_y,
        )

        # ----------------------------------------------------
        # SANTUARIO
        # ----------------------------------------------------

        self.draw_shrine(
            surface,
            camera_x,
            camera_y,
        )

        # ----------------------------------------------------
        # BAULI
        # ----------------------------------------------------

        for (
            name,
            (
                tx,
                ty,
            ),
        ) in (
            self.chests.items()
        ):

            x = (
                tx * TILE
                - camera_x
            )

            y = (
                ty * TILE
                - camera_y
            )

            if (
                x < -TILE
                or
                y < -TILE
                or
                x > width
                or
                y > height
            ):

                continue

            opened = (
                name
                in open_chests
            )

            # Ombra

            pygame.draw.ellipse(
                surface,
                (
                    60,
                    74,
                    55,
                ),
                (
                    x + 2,
                    y + 11,
                    12,
                    4,
                ),
            )

            # Baule

            pygame.draw.rect(
                surface,
                (
                    101,
                    66,
                    39,
                ),
                (
                    x + 2,
                    y + 5,
                    12,
                    8,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    190,
                    135,
                    69,
                ),
                (
                    x + 3,
                    y + 5,
                    10,
                    6,
                ),
            )

            if opened:

                pygame.draw.rect(
                    surface,
                    (
                        87,
                        58,
                        38,
                    ),
                    (
                        x + 3,
                        y + 2,
                        10,
                        4,
                    ),
                )

            else:

                pygame.draw.rect(
                    surface,
                    (
                        243,
                        205,
                        102,
                    ),
                    (
                        x + 7,
                        y + 8,
                        2,
                        3,
                    ),
                )

    # ========================================================
    # CASA
    # ========================================================

    def draw_house(
        self,
        surface,
        camera_x,
        camera_y,
    ):

        hx, hy, hw, hh = (
            self.house_rect
        )

        x = (
            hx * TILE
            - camera_x
        )

        y = (
            hy * TILE
            - camera_y
        )

        width = (
            hw * TILE
        )

        height = (
            hh * TILE
        )

        if (
            x + width < 0
            or
            y + height < 0
            or
            x > surface.get_width()
            or
            y > surface.get_height()
        ):

            return

        # Ombra

        pygame.draw.rect(
            surface,
            (
                80,
                72,
                56,
            ),
            (
                x + 3,
                y + 13,
                width - 2,
                height - 5,
            ),
        )

        # Corpo edificio

        pygame.draw.rect(
            surface,
            (
                232,
                211,
                163,
            ),
            (
                x + 6,
                y + 19,
                width - 12,
                height - 24,
            ),
        )

        # Base

        pygame.draw.rect(
            surface,
            (
                185,
                158,
                111,
            ),
            (
                x + 3,
                y + height - 11,
                width - 6,
                8,
            ),
        )

        # Tetto

        pygame.draw.polygon(
            surface,
            (
                96,
                56,
                43,
            ),
            [

                (
                    x + 2,
                    y + 20,
                ),

                (
                    x + 17,
                    y + 3,
                ),

                (
                    x + width - 18,
                    y + 3,
                ),

                (
                    x + width - 2,
                    y + 20,
                ),
            ],
        )

        pygame.draw.polygon(
            surface,
            (
                181,
                78,
                58,
            ),
            [

                (
                    x + 5,
                    y + 18,
                ),

                (
                    x + 19,
                    y + 5,
                ),

                (
                    x + width - 20,
                    y + 5,
                ),

                (
                    x + width - 5,
                    y + 18,
                ),
            ],
        )

        # Porta

        pygame.draw.rect(
            surface,
            (
                53,
                57,
                53,
            ),
            (
                x
                +
                width // 2
                - 7,

                y + 34,

                14,

                24,
            ),
        )

        # Finestre

        for window_x in (

            x + 17,

            x
            +
            width
            -
            29,

        ):

            pygame.draw.rect(
                surface,
                (
                    60,
                    92,
                    105,
                ),
                (
                    window_x,
                    y + 31,
                    12,
                    10,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    159,
                    205,
                    205,
                ),
                (
                    window_x + 2,
                    y + 33,
                    8,
                    6,
                ),
            )

        # Croce

        pygame.draw.rect(
            surface,
            (
                247,
                239,
                208,
            ),
            (
                x
                +
                width // 2
                - 2,

                y + 7,

                4,

                15,
            ),
        )

        pygame.draw.rect(
            surface,
            (
                247,
                239,
                208,
            ),
            (
                x
                +
                width // 2
                - 7,

                y + 12,

                14,

                4,
            ),
        )

    # ========================================================
    # SANTUARIO
    # ========================================================

    def draw_shrine(
        self,
        surface,
        camera_x,
        camera_y,
    ):

        sx, sy, sw, sh = (
            self.shrine_rect
        )

        x = (
            sx * TILE
            - camera_x
        )

        y = (
            sy * TILE
            - camera_y
        )

        width = (
            sw * TILE
        )

        height = (
            sh * TILE
        )

        if (
            x + width < 0
            or
            y + height < 0
            or
            x > surface.get_width()
            or
            y > surface.get_height()
        ):

            return

        # Gradoni

        pygame.draw.rect(
            surface,
            (
                116,
                124,
                111,
            ),
            (
                x + 13,
                y + 23,
                width - 26,
                height - 28,
            ),
        )

        pygame.draw.rect(
            surface,
            (
                170,
                176,
                155,
            ),
            (
                x + 18,
                y + 18,
                width - 36,
                height - 33,
            ),
        )

        # Colonne

        for column_x in (

            x + 29,

            x
            +
            width
            -
            35,

        ):

            pygame.draw.rect(
                surface,
                (
                    111,
                    119,
                    107,
                ),
                (
                    column_x,
                    y + 10,
                    7,
                    34,
                ),
            )

            pygame.draw.rect(
                surface,
                (
                    193,
                    199,
                    177,
                ),
                (
                    column_x + 1,
                    y + 9,
                    5,
                    31,
                ),
            )

        # Pietra centrale

        pygame.draw.polygon(
            surface,
            (
                85,
                96,
                91,
            ),
            [

                (
                    x
                    +
                    width // 2
                    - 11,

                    y + 37,
                ),

                (
                    x
                    +
                    width // 2,

                    y + 8,
                ),

                (
                    x
                    +
                    width // 2
                    + 11,

                    y + 37,
                ),
            ],
        )

        pygame.draw.polygon(
            surface,
            (
                156,
                173,
                158,
            ),
            [

                (
                    x
                    +
                    width // 2
                    - 7,

                    y + 34,
                ),

                (
                    x
                    +
                    width // 2,

                    y + 13,
                ),

                (
                    x
                    +
                    width // 2
                    + 7,

                    y + 34,
                ),
            ],
        )

    # ========================================================
    # DRAW NPC
    # ========================================================

    def draw_entities(
        self,
        surface,
        assets,
        camera,
        t,
    ):

        camera_x = int(
            camera.x
        )

        camera_y = int(
            camera.y
        )

        frame = (
            int(
                t * 2
            )
            % 2
        )

        for npc in (
            self.npcs
        ):

            x = (
                npc.x * TILE
                - camera_x
            )

            y = (
                npc.y * TILE
                - camera_y
            )

            if (
                x < -24
                or
                y < -32
                or
                x > surface.get_width() + 24
                or
                y > surface.get_height() + 32
            ):

                continue

            sprite = (
                assets.npc(
                    npc.kind,
                    "down",
                    frame,
                )
            )

            surface.blit(
                sprite,
                (
                    x,
                    y - 8,
                ),
            )