from __future__ import annotations

import json
import math
import random

import pygame

from settings import (
    TITLE,
    BASE_W,
    BASE_H,
    WINDOW_W,
    WINDOW_H,
    FPS,
    TILE,
    SAVE_FILE,
    SAVE_DIR,
    COLORS,
)

from assets import Assets
from data import STARTERS, TRAINERS
from models import Creature, Particle, NPC
from world import World
from battle import BattleController

from ui import (
    panel,
    text,
    hp_bar,
    button,
    dialogue,
    type_badge,
)


# ============================================================
# CONFIG
# ============================================================

MAX_TEAM_SIZE = 6


class Game:

    def __init__(self):

        pygame.init()

        pygame.display.set_caption(
            TITLE
        )

        self.window = pygame.display.set_mode(
            (
                WINDOW_W,
                WINDOW_H,
            ),
            pygame.RESIZABLE,
        )

        self.canvas = pygame.Surface(
            (
                BASE_W,
                BASE_H,
            )
        )

        self.clock = pygame.time.Clock()

        self.assets = Assets()

        self.rng = random.Random()

        self.world = World(
            72
        )

        self.running = True

        self.fullscreen = False

        self.state = "title"

        self.return_state = "world"

        # ====================================================
        # SQUADRA
        # ====================================================

        self.team = []

        self.active = 0

        self.team_select = 0

        # ====================================================
        # INVENTARIO
        # ====================================================

        self.balls = 8

        self.potions = 5

        self.coins = 60

        # ====================================================
        # PROGRESSO
        # ====================================================

        self.defeated = set()

        self.open_chests = set()

        self.completed = False

        # ====================================================
        # PLAYER
        # ====================================================

        self.player_pos = pygame.Vector2(
            *self.world.spawn
        )

        self.camera = pygame.Vector2()

        self.facing = "up"

        self.walk_frame = 0

        self.walk_timer = 0

        self.steps_since_encounter = 12

        self.last_tile = (
            self.player_tile()
        )

        self.world_particles = []

        # ====================================================
        # UI
        # ====================================================

        self.notice = (
            "Scegli il tuo primo compagno."
        )

        self.notice_timer = 0

        self.battle: BattleController | None = None

        self.transition = 0.0

        self.transition_dir = 0

        self.transition_target = None

        self.title_select = (
            0
            if SAVE_FILE.exists()
            else 1
        )

        self.starter_select = 0

    # ========================================================
    # HERO
    # ========================================================

    @property
    def hero(self):

        return self.team[
            self.active
        ]

    # ========================================================
    # NUOVA PARTITA
    # ========================================================

    def new_game(
        self,
        species,
    ):

        self.team = [
            Creature(
                species,
                5,
            )
        ]

        self.active = 0

        self.team_select = 0

        self.balls = 8

        self.potions = 5

        self.coins = 60

        self.defeated.clear()

        self.open_chests.clear()

        self.completed = False

        self.reset_to_spawn()

        self.notice = (
            "Esplora Selvaluce. "
            "Mira ti aspetta nel bosco."
        )

        self.notice_timer = 5

        self.state = "world"

        self.save()

    # ========================================================
    # SALVATAGGIO
    # ========================================================

    def save(
        self,
        force=False,
    ):

        if (
            not self.team
            or
            (
                self.state == "battle"
                and
                not force
            )
        ):

            return False

        data = {

            "version":
                3,

            "team":
                [
                    creature.serialize()
                    for creature
                    in self.team
                ],

            "active":
                self.active,

            "pos":
                [
                    self.player_pos.x,
                    self.player_pos.y,
                ],

            "facing":
                self.facing,

            "balls":
                self.balls,

            "potions":
                self.potions,

            "coins":
                self.coins,

            "defeated":
                sorted(
                    self.defeated
                ),

            "chests":
                sorted(
                    self.open_chests
                ),

            "completed":
                self.completed,
        }

        try:

            SAVE_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary = (
                SAVE_FILE.with_suffix(
                    ".tmp"
                )
            )

            temporary.write_text(
                json.dumps(
                    data,
                    indent=2,
                ),
                encoding="utf-8",
            )

            temporary.replace(
                SAVE_FILE
            )

            return True

        except OSError:

            return False

    # ========================================================
    # LOAD
    # ========================================================

    def load(self):

        try:

            data = json.loads(
                SAVE_FILE.read_text(
                    encoding="utf-8"
                )
            )

            if (
                data.get(
                    "version"
                )
                != 3
            ):

                return False

            self.team = [

                Creature.deserialize(
                    creature
                )

                for creature
                in data["team"]
            ]

            # Protezione:
            # massimo 6 creature.

            self.team = self.team[
                :MAX_TEAM_SIZE
            ]

            self.active = max(

                0,

                min(
                    len(
                        self.team
                    ) - 1,

                    int(
                        data.get(
                            "active",
                            0,
                        )
                    ),
                ),
            )

            self.team_select = (
                self.active
            )

            self.player_pos.update(

                float(
                    data["pos"][0]
                ),

                float(
                    data["pos"][1]
                ),
            )

            self.facing = (
                data.get(
                    "facing",
                    "up",
                )
            )

            self.balls = int(
                data.get(
                    "balls",
                    8,
                )
            )

            self.potions = int(
                data.get(
                    "potions",
                    5,
                )
            )

            self.coins = int(
                data.get(
                    "coins",
                    60,
                )
            )

            self.defeated = set(
                map(
                    int,
                    data.get(
                        "defeated",
                        [],
                    ),
                )
            )

            self.open_chests = set(
                data.get(
                    "chests",
                    [],
                )
            )

            self.completed = bool(
                data.get(
                    "completed",
                    False,
                )
            )

            self.state = "world"

            self.notice = (
                "Bentornato a Selvaluce."
            )

            self.notice_timer = 3

            return True

        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ):

            return False

    # ========================================================
    # TRANSIZIONE
    # ========================================================

    def begin_transition(
        self,
        target,
    ):

        self.transition = .001

        self.transition_dir = 1

        self.transition_target = (
            target
        )

    def update_transition(
        self,
        dt,
    ):

        if not self.transition:

            return

        self.transition += (
            dt
            * 3.0
            * self.transition_dir
        )

        if (
            self.transition_dir > 0
            and
            self.transition >= 1
        ):

            self.transition = 1

            if (
                self.transition_target
            ):

                old_state = (
                    self.state
                )

                self.state = (
                    self.transition_target
                )

                self.transition_target = None

                if (
                    old_state == "battle"
                    and
                    self.state
                    in (
                        "world",
                        "ending",
                    )
                ):

                    self.battle = None

            self.transition_dir = -1

        elif (
            self.transition_dir < 0
            and
            self.transition <= 0
        ):

            self.transition = 0

            self.transition_dir = 0

    # ========================================================
    # PLAYER
    # ========================================================

    def reset_to_spawn(self):

        self.player_pos.update(
            *self.world.spawn
        )

        self.camera.update(
            0,
            0,
        )

        self.last_tile = (
            self.player_tile()
        )

    def player_tile(self):

        return (

            int(
                self.player_pos.x
                // TILE
            ),

            int(
                self.player_pos.y
                // TILE
            ),
        )

    def player_rect(
        self,
        pos=None,
    ):

        position = (
            pos
            or
            self.player_pos
        )

        return pygame.Rect(

            int(
                position.x - 5
            ),

            int(
                position.y - 4
            ),

            10,

            9,
        )

    def facing_tile(self):

        x, y = (
            self.player_tile()
        )

        dx, dy = {

            "up":
                (
                    0,
                    -1,
                ),

            "down":
                (
                    0,
                    1,
                ),

            "left":
                (
                    -1,
                    0,
                ),

            "right":
                (
                    1,
                    0,
                ),

        }[
            self.facing
        ]

        return (
            x + dx,
            y + dy,
        )

    def collide(
        self,
        pos,
    ):

        return self.world.collide_rect(
            self.player_rect(
                pos
            )
        )

    # ========================================================
    # PARTICELLE
    # ========================================================

    def spawn_grass_particles(
        self,
        tile,
    ):

        tx, ty = (
            tile
        )

        for _ in range(
            4
        ):

            self.world_particles.append(

                Particle(

                    tx * TILE
                    +
                    self.rng.uniform(
                        3,
                        13,
                    ),

                    ty * TILE
                    +
                    self.rng.uniform(
                        8,
                        15,
                    ),

                    self.rng.uniform(
                        -8,
                        8,
                    ),

                    self.rng.uniform(
                        -24,
                        -11,
                    ),

                    .45,

                    (
                        69,
                        128,
                        70,
                    ),

                    1,

                    45,
                )
            )

    # ========================================================
    # UPDATE WORLD
    # ========================================================

    def update_world(
        self,
        dt,
    ):

        keys = (
            pygame.key.get_pressed()
        )

        move = pygame.Vector2(

            int(
                keys[
                    pygame.K_d
                ]
                or
                keys[
                    pygame.K_RIGHT
                ]
            )
            -
            int(
                keys[
                    pygame.K_a
                ]
                or
                keys[
                    pygame.K_LEFT
                ]
            ),

            int(
                keys[
                    pygame.K_s
                ]
                or
                keys[
                    pygame.K_DOWN
                ]
            )
            -
            int(
                keys[
                    pygame.K_w
                ]
                or
                keys[
                    pygame.K_UP
                ]
            ),
        )

        if (
            move.length_squared()
        ):

            move = (
                move.normalize()
            )

            self.walk_timer += (
                dt
            )

            if (
                abs(
                    move.x
                )
                >
                abs(
                    move.y
                )
            ):

                self.facing = (
                    "right"
                    if
                    move.x > 0
                    else
                    "left"
                )

            else:

                self.facing = (
                    "down"
                    if
                    move.y > 0
                    else
                    "up"
                )

            if (
                self.walk_timer
                >= .11
            ):

                self.walk_timer = 0

                self.walk_frame = (
                    self.walk_frame
                    + 1
                ) % 4

        else:

            self.walk_frame = 0

            self.walk_timer = 0

        delta = (
            move
            * 72
            * dt
        )

        trial = (
            self.player_pos.copy()
        )

        trial.x += (
            delta.x
        )

        if not self.collide(
            trial
        ):

            self.player_pos.x = (
                trial.x
            )

        trial = (
            self.player_pos.copy()
        )

        trial.y += (
            delta.y
        )

        if not self.collide(
            trial
        ):

            self.player_pos.y = (
                trial.y
            )

        tile = (
            self.player_tile()
        )

        if (
            tile
            != self.last_tile
        ):

            self.steps_since_encounter += 1

            self.last_tile = (
                tile
            )

            if (
                self.world.tile(
                    *tile
                )
                == ","
            ):

                self.spawn_grass_particles(
                    tile
                )

                if (
                    self.steps_since_encounter
                    >= 5
                    and
                    self.rng.random()
                    < .105
                ):

                    self.steps_since_encounter = 0

                    self.trigger_wild()

        target = pygame.Vector2(

            self.player_pos.x
            - BASE_W / 2,

            self.player_pos.y
            - BASE_H / 2,
        )

        target.x = max(

            0,

            min(
                self.world.w
                * TILE
                - BASE_W,

                target.x,
            ),
        )

        target.y = max(

            0,

            min(
                self.world.h
                * TILE
                - BASE_H,

                target.y,
            ),
        )

        self.camera += (

            target
            - self.camera

        ) * min(
            1,
            dt * 7.5,
        )

        for particle in (
            self.world_particles
        ):

            particle.update(
                dt
            )

        self.world_particles[:] = [

            particle

            for particle
            in self.world_particles

            if particle.life > 0
        ]

        if (
            self.notice_timer
            > 0
        ):

            self.notice_timer = max(
                0,
                self.notice_timer
                - dt,
            )

    # ========================================================
    # INTERAZIONE
    # ========================================================

    def interact(self):

        tx, ty = (
            self.facing_tile()
        )

        entity = (
            self.world.entity_at(
                tx,
                ty,
            )
        )

        if isinstance(
            entity,
            NPC,
        ):

            if (
                entity.kind
                == "clinic"
            ):

                for creature in (
                    self.team
                ):

                    creature.heal_full()

                self.balls = max(
                    5,
                    self.balls,
                )

                self.potions = max(
                    3,
                    self.potions,
                )

                self.notice = (
                    "Squadra curata."
                )

                self.notice_timer = 3

                self.save()

            elif (
                entity.kind
                == "guide"
            ):

                self.notice = (
                    "Guida: Mira, Nerio e poi Alba."
                )

                self.notice_timer = 4

            elif (
                entity.trainer_index
                is not None
            ):

                self.challenge(
                    entity.trainer_index
                )

            return

        if (
            isinstance(
                entity,
                str,
            )
            and
            entity.startswith(
                "chest"
            )
        ):

            if (
                entity
                in self.open_chests
            ):

                self.notice = (
                    "Il baule e' vuoto."
                )

                self.notice_timer = 2

            else:

                self.open_chests.add(
                    entity
                )

                self.balls += 3

                self.potions += 2

                self.coins += 20

                self.notice = (
                    "+3 Sfere | +2 Cure | +20 monete"
                )

                self.notice_timer = 4

                self.save()

            return

        self.notice = (
            "Non c'e' nulla qui."
        )

        self.notice_timer = 2

    # ========================================================
    # TRAINER
    # ========================================================

    def challenge(
        self,
        index,
    ):

        if (
            index
            in self.defeated
        ):

            self.notice = (
                f"{TRAINERS[index]['name']}: "
                "bella sfida!"
            )

            self.notice_timer = 3

            return

        if (
            index == 1
            and
            0 not in self.defeated
        ):

            self.notice = (
                "Nerio: prima affronta Mira."
            )

            self.notice_timer = 3

            return

        if (
            index == 2
            and
            not {
                0,
                1,
            }
            <= self.defeated
        ):

            self.notice = (
                "Alba: torna con le due medaglie."
            )

            self.notice_timer = 3

            return

        enemies = [

            Creature(
                species,
                level,
            )

            for (
                species,
                level,
            )
            in
            TRAINERS[index][
                "team"
            ]
        ]

        self.start_battle(

            enemies,

            index,

            (
                f"{TRAINERS[index]['name']}: "
                f"{TRAINERS[index]['line']}"
            ),
        )

    # ========================================================
    # WILD
    # ========================================================

    def trigger_wild(self):

        tx, _ = (
            self.player_tile()
        )

        if (
            tx < 39
        ):

            pool = (

                "germillo",

                "alafoglia",

                "nimbat",

                "braciotto",
            )

            low = 3

            high = 6

        else:

            pool = (

                "ondino",

                "ciottolo",

                "nimbat",

                "germillo",
            )

            low = 5

            high = 8

        level = min(

            12,

            self.rng.randint(
                low,
                high,
            )
            +
            min(
                3,
                len(
                    self.defeated
                ),
            ),
        )

        enemy = Creature(

            self.rng.choice(
                pool
            ),

            level,
        )

        self.start_battle(

            [
                enemy
            ],

            None,

            (
                f"Un {enemy.name} selvatico appare!"
            ),
        )

    # ========================================================
    # BATTLE
    # ========================================================

    def start_battle(
        self,
        enemies,
        trainer_index,
        intro,
    ):

        if not any(

            creature.hp > 0

            for creature
            in self.team
        ):

            return

        if (
            self.hero.hp
            <= 0
        ):

            self.active = next(

                index

                for (
                    index,
                    creature,
                )
                in enumerate(
                    self.team
                )

                if creature.hp > 0
            )

        self.battle = BattleController(

            self,

            enemies,

            trainer_index,

            intro,
        )

        self.begin_transition(
            "battle"
        )

    def finish_battle(
        self,
        message,
        ending=False,
    ):

        self.notice = (
            message
        )

        self.notice_timer = 5

        self.save(
            force=True
        )

        self.begin_transition(

            "ending"
            if ending
            else
            "world"
        )

    # ========================================================
    # CAMBIO CREATURE
    # ========================================================

    def choose_team_member(
        self,
        index,
    ):

        if not (
            0
            <= index
            <
            len(
                self.team
            )
        ):

            return False

        creature = (
            self.team[
                index
            ]
        )

        if (
            creature.hp
            <= 0
        ):

            return False

        if (
            self.return_state
            == "battle"
            and
            self.battle
        ):

            if (
                self.battle.switch(
                    index
                )
            ):

                self.state = (
                    "battle"
                )

                return True

            return False

        self.active = (
            index
        )

        self.state = (
            self.return_state
        )

        return True

    # ========================================================
    # DRAW WORLD
    # ========================================================

    def draw_world(self):

        t = (
            pygame.time.get_ticks()
            / 1000
        )

        self.world.draw(

            self.canvas,

            self.assets,

            self.camera,

            self.open_chests,

            t,
        )

        camera_x = int(
            self.camera.x
        )

        camera_y = int(
            self.camera.y
        )

        for particle in (
            self.world_particles
        ):

            pygame.draw.rect(
                self.canvas,
                particle.color,
                (
                    int(
                        particle.x
                        -
                        camera_x
                    ),

                    int(
                        particle.y
                        -
                        camera_y
                    ),

                    particle.size,

                    particle.size,
                ),
            )

        self.world.draw_entities(

            self.canvas,

            self.assets,

            self.camera,

            t,
        )

        player_x = int(

            self.player_pos.x
            -
            camera_x
            -
            8
        )

        player_y = int(

            self.player_pos.y
            -
            camera_y
            -
            16
        )

        self.canvas.blit(

            self.assets.player(
                self.facing,
                self.walk_frame,
            ),

            (
                player_x,
                player_y,
            ),
        )

        self.draw_world_hud()

        if (
            self.notice_timer
            > 0
        ):

            dialogue(

                self.canvas,

                self.assets,

                self.notice,

                "E INTERAGISCI",
            )

    # ========================================================
    # HUD
    # ========================================================

    def draw_world_hud(self):

        # ====================================================
        # INVENTARIO
        # ====================================================

        badges = len(

            self.defeated

            &
            {
                0,
                1,
            }
        )

        panel(

            self.canvas,

            (
                5,
                5,
                65,
                22,
            ),

            (
                235,
                233,
                210,
            ),
        )

        text(

            self.canvas,

            self.assets.font_small,

            (
                f"SFERE {self.balls} "
                f"| CURE {self.potions}"
            ),

            (
                9,
                9,
            ),

            COLORS[
                "ink"
            ],

            shadow=False,
        )

        text(

            self.canvas,

            self.assets.font_small,

            (
                f"MEDAGLIE {badges}/2"
            ),

            (
                9,
                17,
            ),

            COLORS[
                "ink"
            ],

            shadow=False,
        )

        # ====================================================
        # CREATURE ATTIVA
        # ====================================================

        if not self.team:

            return

        creature = (
            self.hero
        )

        x = (
            BASE_W - 70
        )

        panel(

            self.canvas,

            (
                x,
                5,
                65,
                22,
            ),

            (
                235,
                233,
                210,
            ),
        )

        icon = (
            pygame.transform.scale(

                self.assets.creature(
                    creature.species,
                    "front",
                    0,
                    1,
                ),

                (
                    18,
                    18,
                ),
            )
        )

        self.canvas.blit(
            icon,
            (
                x + 2,
                7,
            ),
        )

        text(

            self.canvas,

            self.assets.font_small,

            creature.name,

            (
                x + 22,
                9,
            ),

            COLORS[
                "ink"
            ],

            shadow=False,
        )

        hp_bar(

            self.canvas,

            (
                x + 22,
                17,
                37,
                4,
            ),

            creature.hp
            /
            creature.max_hp,
        )

        # Indicatore numero squadra

        text(

            self.canvas,

            self.assets.font_tiny,

            (
                f"{len(self.team)}/"
                f"{MAX_TEAM_SIZE}"
            ),

            (
                x + 59,
                24,
            ),

            COLORS[
                "white"
            ],

            "bottomright",

            False,
        )

    # ========================================================
    # TITLE
    # ========================================================

    def draw_title(self):

        t = (
            pygame.time.get_ticks()
            / 1000
        )

        self.canvas.fill(
            (
                29,
                54,
                56,
            )
        )

        for y in range(
            0,
            BASE_H,
            16,
        ):

            for x in range(
                0,
                BASE_W,
                16,
            ):

                kind = (

                    "#"

                    if (
                        y < 64
                        and
                        (
                            x // 16
                            +
                            y // 16
                        )
                        % 3
                    )

                    else
                    "."
                )

                self.canvas.blit(

                    self.assets.tile(

                        kind,

                        int(
                            t * 3
                        )
                        % 4,

                        (
                            x + y
                        )
                        & 1,
                    ),

                    (
                        x,
                        y,
                    ),
                )

        shade = pygame.Surface(
            (
                BASE_W,
                BASE_H,
            ),
            pygame.SRCALPHA,
        )

        shade.fill(
            (
                18,
                35,
                40,
                130,
            )
        )

        self.canvas.blit(
            shade,
            (
                0,
                0,
            ),
        )

        panel(

            self.canvas,

            (
                20,
                19,
                280,
                61,
            ),

            (
                29,
                59,
                61,
            ),
        )

        text(

            self.canvas,

            self.assets.font_title,

            "SELVALUCE DX",

            (
                160,
                34,
            ),

            (
                245,
                234,
                197,
            ),

            "center",

            False,
        )

        text(

            self.canvas,

            self.assets.font,

            "ESPLORA. CATTURA. CRESCI INSIEME.",

            (
                160,
                59,
            ),

            (
                194,
                222,
                178,
            ),

            "center",

            False,
        )

        for (
            index,
            species,
        ) in enumerate(
            STARTERS
        ):

            image = (
                self.assets.creature(

                    species,

                    "front",

                    int(
                        t * 3
                        +
                        index
                    )
                    % 2,

                    2,
                )
            )

            self.canvas.blit(

                image,

                (
                    47
                    +
                    index
                    * 90,

                    73
                    +
                    int(
                        math.sin(
                            t * 2
                            +
                            index
                        )
                        * 2
                    ),
                ),
            )

        options = [

            (
                "CONTINUA",
                SAVE_FILE.exists(),
            ),

            (
                "NUOVA PARTITA",
                True,
            ),
        ]

        for (
            index,
            (
                label,
                enabled,
            ),
        ) in enumerate(
            options
        ):

            button(

                self.canvas,

                self.assets.font,

                (
                    72
                    +
                    index
                    * 92,

                    149,

                    84,

                    22,
                ),

                label,

                index
                ==
                self.title_select,

                enabled,

                index
                ==
                self.title_select,
            )

    # ========================================================
    # STARTER
    # ========================================================

    def draw_starter(self):

        self.canvas.fill(
            (
                34,
                53,
                56,
            )
        )

        text(

            self.canvas,

            self.assets.font_big,

            "SCEGLI IL TUO COMPAGNO",

            (
                160,
                18,
            ),

            COLORS[
                "accent2"
            ],

            "center",

            False,
        )

        for (
            index,
            species,
        ) in enumerate(
            STARTERS
        ):

            x = (
                8
                +
                index
                * 104
            )

            selected = (
                index
                ==
                self.starter_select
            )

            rect = panel(

                self.canvas,

                (
                    x,
                    38,
                    96,
                    126,
                ),

                (
                    224,
                    239,
                    198,
                )
                if selected
                else
                (
                    239,
                    233,
                    207,
                ),
            )

            image = (
                self.assets.creature(

                    species,

                    "front",

                    int(
                        pygame.time.get_ticks()
                        / 300
                    )
                    % 2,

                    2,
                )
            )

            self.canvas.blit(
                image,
                (
                    x,
                    47,
                ),
            )

            creature = (
                Creature(
                    species,
                    5,
                )
            )

            text(

                self.canvas,

                self.assets.font,

                creature.name,

                (
                    x + 48,
                    118,
                ),

                COLORS[
                    "ink"
                ],

                "center",

                False,
            )

            type_badge(

                self.canvas,

                self.assets.font_tiny,

                creature.element,

                (
                    x + 31,
                    130,
                    34,
                    10,
                ),
            )

            if selected:

                pygame.draw.rect(

                    self.canvas,

                    COLORS[
                        "accent2"
                    ],

                    rect,

                    2,

                    border_radius=3,
                )

    # ========================================================
    # TEAM - 6 CREATURE
    # ========================================================

    def draw_team(self):

        if (
            self.return_state
            == "battle"
            and
            self.battle
        ):

            self.battle.draw(

                self.canvas,

                self.assets,

                pygame.time.get_ticks()
                / 1000,
            )

        else:

            self.draw_world()

        overlay = pygame.Surface(
            (
                BASE_W,
                BASE_H,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                10,
                20,
                25,
                185,
            )
        )

        self.canvas.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        panel(

            self.canvas,

            (
                8,
                8,
                304,
                164,
            ),

            (
                239,
                233,
                209,
            ),
        )

        text(

            self.canvas,

            self.assets.font_big,

            "SQUADRA",

            (
                160,
                20,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

        # ====================================================
        # 6 SLOT:
        #
        # 1  4
        # 2  5
        # 3  6
        #
        # ====================================================

        for index in range(
            MAX_TEAM_SIZE
        ):

            column = (
                index // 3
            )

            row = (
                index % 3
            )

            x = (
                17
                +
                column
                * 145
            )

            y = (
                37
                +
                row
                * 38
            )

            rect = pygame.Rect(
                x,
                y,
                140,
                34,
            )

            selected = (
                index
                ==
                self.team_select
            )

            pygame.draw.rect(

                self.canvas,

                (
                    216,
                    232,
                    194,
                )
                if selected
                else
                (
                    231,
                    229,
                    211,
                ),

                rect,

                border_radius=3,
            )

            pygame.draw.rect(

                self.canvas,

                COLORS[
                    "accent"
                ]
                if selected
                else
                (
                    110,
                    122,
                    112,
                ),

                rect,

                2
                if selected
                else
                1,

                border_radius=3,
            )

            # ================================================
            # CREATURE PRESENTE
            # ================================================

            if (
                index
                <
                len(
                    self.team
                )
            ):

                creature = (
                    self.team[
                        index
                    ]
                )

                image = (
                    pygame.transform.scale(

                        self.assets.creature(
                            creature.species,
                            "front",
                            0,
                            1,
                        ),

                        (
                            28,
                            28,
                        ),
                    )
                )

                self.canvas.blit(
                    image,
                    (
                        x + 3,
                        y + 3,
                    ),
                )

                text(

                    self.canvas,

                    self.assets.font,

                    (
                        f"{index + 1} "
                        f"{creature.name}"
                    ),

                    (
                        x + 34,
                        y + 5,
                    ),

                    COLORS[
                        "ink"
                    ],

                    shadow=False,
                )

                text(

                    self.canvas,

                    self.assets.font_tiny,

                    (
                        f"LV {creature.level}"
                    ),

                    (
                        x + 34,
                        y + 14,
                    ),

                    COLORS[
                        "ink"
                    ],

                    shadow=False,
                )

                hp_bar(

                    self.canvas,

                    (
                        x + 34,
                        y + 23,
                        59,
                        4,
                    ),

                    creature.hp
                    /
                    creature.max_hp,
                )

                text(

                    self.canvas,

                    self.assets.font_tiny,

                    (
                        f"{creature.hp}/"
                        f"{creature.max_hp}"
                    ),

                    (
                        x + 97,
                        y + 22,
                    ),

                    COLORS[
                        "ink"
                    ],

                    shadow=False,
                )

                if (
                    index
                    ==
                    self.active
                ):

                    text(

                        self.canvas,

                        self.assets.font_tiny,

                        "ATTIVO",

                        (
                            rect.right - 4,
                            rect.top + 4,
                        ),

                        COLORS[
                            "accent"
                        ],

                        "topright",

                        False,
                    )

            # ================================================
            # SLOT VUOTO
            # ================================================

            else:

                text(

                    self.canvas,

                    self.assets.font,

                    (
                        f"{index + 1} VUOTO"
                    ),

                    rect.center,

                    (
                        113,
                        116,
                        108,
                    ),

                    "center",

                    False,
                )

        text(

            self.canvas,

            self.assets.font_tiny,

            (
                "1-6 SELEZIONA | "
                "FRECCE MUOVI | "
                "INVIO CONFERMA"
            ),

            (
                160,
                160,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

    # ========================================================
    # HELP
    # ========================================================

    def draw_help(self):

        self.draw_world()

        overlay = pygame.Surface(
            (
                BASE_W,
                BASE_H,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                10,
                20,
                25,
                180,
            )
        )

        self.canvas.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        panel(

            self.canvas,

            (
                24,
                14,
                272,
                151,
            ),

            (
                241,
                235,
                211,
            ),
        )

        text(

            self.canvas,

            self.assets.font_big,

            "TACCUINO",

            (
                160,
                26,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

        lines = [

            "WASD / FRECCE = MUOVI",

            "E / INVIO = INTERAGISCI",

            "Q = SQUADRA",

            "P = POZIONE",

            "1-4 = MOSSE",

            "C = LANCIA SFERA",

            "B = ZAINO",

            "F = FUGA",

            "SQUADRA MASSIMA = 6",

            "F5 = SALVA",
        ]

        for (
            index,
            line,
        ) in enumerate(
            lines
        ):

            text(

                self.canvas,

                self.assets.font_small,

                line,

                (
                    42,
                    47
                    +
                    index
                    * 10,
                ),

                COLORS[
                    "ink"
                ],

                shadow=False,
            )

    # ========================================================
    # PAUSE
    # ========================================================

    def draw_pause(self):

        self.draw_world()

        overlay = pygame.Surface(
            (
                BASE_W,
                BASE_H,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                10,
                20,
                25,
                180,
            )
        )

        self.canvas.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        panel(

            self.canvas,

            (
                93,
                57,
                134,
                62,
            ),

            (
                239,
                233,
                209,
            ),
        )

        text(

            self.canvas,

            self.assets.font_big,

            "PAUSA",

            (
                160,
                74,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

    # ========================================================
    # ENDING
    # ========================================================

    def draw_ending(self):

        self.canvas.fill(
            (
                26,
                48,
                51,
            )
        )

        panel(

            self.canvas,

            (
                28,
                19,
                264,
                143,
            ),

            (
                240,
                233,
                209,
            ),
        )

        text(

            self.canvas,

            self.assets.font_big,

            "NUOVO CUSTODE",

            (
                160,
                35,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

        text(

            self.canvas,

            self.assets.font,

            "HAI COMPLETATO SELVALUCE!",

            (
                160,
                55,
            ),

            COLORS[
                "ink"
            ],

            "center",

            False,
        )

    # ========================================================
    # TRANSITION DRAW
    # ========================================================

    def draw_transition(self):

        if not self.transition:

            return

        t = (
            1
            -
            (
                1
                -
                max(
                    0,
                    min(
                        1,
                        self.transition,
                    ),
                )
            )
            ** 3
        )

        stripe_height = (
            BASE_H / 8
        )

        for index in range(
            8
        ):

            delay = (
                index
                * .05
            )

            local = max(

                0,

                min(

                    1,

                    (
                        t
                        -
                        delay
                    )
                    /
                    (
                        1
                        -
                        7
                        *
                        .05
                    ),
                ),
            )

            width = int(
                BASE_W
                *
                local
            )

            rect = pygame.Rect(

                0
                if
                index % 2 == 0
                else
                BASE_W - width,

                int(
                    index
                    *
                    stripe_height
                ),

                width,

                math.ceil(
                    stripe_height
                )
                +
                1,
            )

            pygame.draw.rect(

                self.canvas,

                (
                    26,
                    42,
                    49,
                ),

                rect,
            )

    # ========================================================
    # KEYBOARD
    # ========================================================

    def handle_keydown(
        self,
        key,
    ):

        if (
            key
            ==
            pygame.K_F11
        ):

            self.toggle_fullscreen()

            return

        if self.transition:

            return

        # ====================================================
        # TITLE
        # ====================================================

        if (
            self.state
            ==
            "title"
        ):

            if key in (

                pygame.K_LEFT,
                pygame.K_a,
                pygame.K_RIGHT,
                pygame.K_d,

            ):

                self.title_select = (
                    1
                    -
                    self.title_select
                )

            elif key in (

                pygame.K_RETURN,
                pygame.K_SPACE,

            ):

                if (
                    self.title_select
                    ==
                    0
                    and
                    SAVE_FILE.exists()
                ):

                    if (
                        self.load()
                    ):

                        return

                self.state = (
                    "starter"
                )

        # ====================================================
        # STARTER
        # ====================================================

        elif (
            self.state
            ==
            "starter"
        ):

            if key in (

                pygame.K_LEFT,
                pygame.K_a,

            ):

                self.starter_select = (

                    self.starter_select
                    -
                    1

                ) % 3

            elif key in (

                pygame.K_RIGHT,
                pygame.K_d,

            ):

                self.starter_select = (

                    self.starter_select
                    +
                    1

                ) % 3

            elif key in (

                pygame.K_RETURN,
                pygame.K_SPACE,

            ):

                self.new_game(

                    STARTERS[
                        self.starter_select
                    ]
                )

            elif (
                key
                ==
                pygame.K_ESCAPE
            ):

                self.state = (
                    "title"
                )

        # ====================================================
        # WORLD
        # ====================================================

        elif (
            self.state
            ==
            "world"
        ):

            if key in (

                pygame.K_e,
                pygame.K_RETURN,
                pygame.K_SPACE,

            ):

                self.interact()

            elif (
                key
                ==
                pygame.K_q
            ):

                self.return_state = (
                    "world"
                )

                self.team_select = (
                    self.active
                )

                self.state = (
                    "team"
                )

            elif (
                key
                ==
                pygame.K_h
            ):

                self.return_state = (
                    "world"
                )

                self.state = (
                    "help"
                )

            elif (
                key
                ==
                pygame.K_p
            ):

                if (
                    self.potions
                    >
                    0
                    and
                    self.hero.hp
                    >
                    0
                    and
                    self.hero.hp
                    <
                    self.hero.max_hp
                ):

                    self.potions -= 1

                    amount = min(

                        35,

                        self.hero.max_hp
                        -
                        self.hero.hp,
                    )

                    self.hero.hp += (
                        amount
                    )

                    self.notice = (
                        f"{self.hero.name} +{amount} PS"
                    )

                    self.notice_timer = 3

                    self.save()

            elif (
                key
                ==
                pygame.K_F5
            ):

                self.save()

                self.notice = (
                    "PARTITA SALVATA"
                )

                self.notice_timer = 2

            elif (
                key
                ==
                pygame.K_ESCAPE
            ):

                self.state = (
                    "pause"
                )

        # ====================================================
        # BATTLE
        # ====================================================

        elif (
            self.state
            ==
            "battle"
            and
            self.battle
        ):

            battle = (
                self.battle
            )

            if (
                key
                in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                )
                and
                battle.phase
                ==
                "input"
                and
                not
                battle.must_switch
            ):

                index = (
                    key
                    -
                    pygame.K_1
                )

                if (
                    battle.menu
                    ==
                    "moves"
                ):

                    battle.choose_move(
                        index
                    )

                else:

                    if (
                        index
                        ==
                        0
                    ):

                        battle.capture()

                    elif (
                        index
                        ==
                        1
                    ):

                        battle.use_potion()

            elif (
                key
                ==
                pygame.K_c
            ):

                battle.capture()

            elif (
                key
                ==
                pygame.K_b
                and
                battle.phase
                ==
                "input"
            ):

                battle.menu = (

                    "bag"

                    if
                    battle.menu
                    ==
                    "moves"

                    else

                    "moves"
                )

            elif (
                key
                ==
                pygame.K_q
            ):

                self.return_state = (
                    "battle"
                )

                self.team_select = (
                    self.active
                )

                self.state = (
                    "team"
                )

            elif (
                key
                ==
                pygame.K_f
            ):

                battle.run()

        # ====================================================
        # TEAM
        # ====================================================

        elif (
            self.state
            ==
            "team"
        ):

            # ------------------------------------------------
            # 1-6 = selezione diretta
            # ------------------------------------------------

            if key in (

                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
                pygame.K_4,
                pygame.K_5,
                pygame.K_6,

            ):

                index = (
                    key
                    -
                    pygame.K_1
                )

                self.team_select = (
                    index
                )

                self.choose_team_member(
                    index
                )

            # ------------------------------------------------
            # SU
            # ------------------------------------------------

            elif key in (

                pygame.K_UP,
                pygame.K_w,

            ):

                column = (
                    self.team_select
                    //
                    3
                )

                row = (
                    self.team_select
                    %
                    3
                )

                row = (
                    row - 1
                ) % 3

                self.team_select = (
                    column
                    *
                    3
                    +
                    row
                )

            # ------------------------------------------------
            # GIU
            # ------------------------------------------------

            elif key in (

                pygame.K_DOWN,
                pygame.K_s,

            ):

                column = (
                    self.team_select
                    //
                    3
                )

                row = (
                    self.team_select
                    %
                    3
                )

                row = (
                    row + 1
                ) % 3

                self.team_select = (
                    column
                    *
                    3
                    +
                    row
                )

            # ------------------------------------------------
            # SINISTRA / DESTRA
            # ------------------------------------------------

            elif key in (

                pygame.K_LEFT,
                pygame.K_a,
                pygame.K_RIGHT,
                pygame.K_d,

            ):

                if (
                    self.team_select
                    <
                    3
                ):

                    self.team_select += 3

                else:

                    self.team_select -= 3

            # ------------------------------------------------
            # CONFERMA
            # ------------------------------------------------

            elif key in (

                pygame.K_RETURN,
                pygame.K_SPACE,

            ):

                self.choose_team_member(
                    self.team_select
                )

            # ------------------------------------------------
            # ESC
            # ------------------------------------------------

            elif key in (

                pygame.K_ESCAPE,
                pygame.K_q,

            ):

                self.state = (
                    self.return_state
                )

        # ====================================================
        # HELP
        # ====================================================

        elif (
            self.state
            ==
            "help"
        ):

            if key in (

                pygame.K_ESCAPE,
                pygame.K_h,
                pygame.K_RETURN,

            ):

                self.state = (
                    self.return_state
                )

        # ====================================================
        # PAUSE
        # ====================================================

        elif (
            self.state
            ==
            "pause"
        ):

            if (
                key
                ==
                pygame.K_ESCAPE
            ):

                self.state = (
                    "world"
                )

        # ====================================================
        # ENDING
        # ====================================================

        elif (
            self.state
            ==
            "ending"
        ):

            if key in (

                pygame.K_RETURN,
                pygame.K_SPACE,
                pygame.K_ESCAPE,

            ):

                self.state = (
                    "world"
                )

    # ========================================================
    # FULLSCREEN
    # ========================================================

    def toggle_fullscreen(self):

        self.fullscreen = (
            not
            self.fullscreen
        )

        if (
            self.fullscreen
        ):

            self.window = (
                pygame.display.set_mode(

                    (
                        0,
                        0,
                    ),

                    pygame.FULLSCREEN,
                )
            )

        else:

            self.window = (
                pygame.display.set_mode(

                    (
                        WINDOW_W,
                        WINDOW_H,
                    ),

                    pygame.RESIZABLE,
                )
            )

    # ========================================================
    # WINDOW -> LOGICAL
    # ========================================================

    def window_to_logical(
        self,
        pos,
    ):

        window_width, window_height = (
            self.window.get_size()
        )

        scale = max(

            1,

            int(

                min(

                    window_width
                    /
                    BASE_W,

                    window_height
                    /
                    BASE_H,
                )
            ),
        )

        scaled_width = (
            BASE_W
            *
            scale
        )

        scaled_height = (
            BASE_H
            *
            scale
        )

        offset_x = (

            window_width
            -
            scaled_width

        ) / 2

        offset_y = (

            window_height
            -
            scaled_height

        ) / 2

        x = (

            pos[0]
            -
            offset_x

        ) / scale

        y = (

            pos[1]
            -
            offset_y

        ) / scale

        if not (
            0
            <=
            x
            <
            BASE_W
            and
            0
            <=
            y
            <
            BASE_H
        ):

            return None

        return (
            x,
            y,
        )

    # ========================================================
    # MOUSE MOTION
    # ========================================================

    def handle_mouse_motion(
        self,
        pos,
    ):

        if self.transition:

            return

        logical = (
            self.window_to_logical(
                pos
            )
        )

        if (
            logical
            is None
        ):

            return

        x, y = (
            logical
        )

        # TITLE

        if (
            self.state
            ==
            "title"
        ):

            for index in range(
                2
            ):

                rect = pygame.Rect(

                    72
                    +
                    index
                    *
                    92,

                    149,

                    84,

                    22,
                )

                if (
                    rect.collidepoint(
                        x,
                        y,
                    )
                ):

                    if (
                        index
                        ==
                        1
                        or
                        SAVE_FILE.exists()
                    ):

                        self.title_select = (
                            index
                        )

                    return

        # STARTER

        elif (
            self.state
            ==
            "starter"
        ):

            for index in range(
                3
            ):

                rect = pygame.Rect(

                    8
                    +
                    index
                    *
                    104,

                    38,

                    96,

                    126,
                )

                if (
                    rect.collidepoint(
                        x,
                        y,
                    )
                ):

                    self.starter_select = (
                        index
                    )

                    return

        # TEAM 6

        elif (
            self.state
            ==
            "team"
        ):

            for index in range(
                MAX_TEAM_SIZE
            ):

                column = (
                    index // 3
                )

                row = (
                    index % 3
                )

                rect = pygame.Rect(

                    17
                    +
                    column
                    *
                    145,

                    37
                    +
                    row
                    *
                    38,

                    140,

                    34,
                )

                if (
                    rect.collidepoint(
                        x,
                        y,
                    )
                ):

                    self.team_select = (
                        index
                    )

                    return

    # ========================================================
    # MOUSE DOWN
    # ========================================================

    def handle_mouse_down(
        self,
        pos,
        button_id,
    ):

        if (
            button_id
            !=
            1
            or
            self.transition
        ):

            return

        logical = (
            self.window_to_logical(
                pos
            )
        )

        if (
            logical
            is None
        ):

            return

        x, y = (
            logical
        )

        # ====================================================
        # TITLE
        # ====================================================

        if (
            self.state
            ==
            "title"
        ):

            continue_rect = pygame.Rect(
                72,
                149,
                84,
                22,
            )

            new_rect = pygame.Rect(
                164,
                149,
                84,
                22,
            )

            if (
                continue_rect.collidepoint(
                    x,
                    y,
                )
            ):

                self.title_select = 0

                if (
                    SAVE_FILE.exists()
                ):

                    if not self.load():

                        self.state = (
                            "starter"
                        )

                else:

                    self.state = (
                        "starter"
                    )

                return

            if (
                new_rect.collidepoint(
                    x,
                    y,
                )
            ):

                self.title_select = 1

                self.state = (
                    "starter"
                )

                return

        # ====================================================
        # STARTER
        # ====================================================

        elif (
            self.state
            ==
            "starter"
        ):

            for index in range(
                3
            ):

                rect = pygame.Rect(

                    8
                    +
                    index
                    *
                    104,

                    38,

                    96,

                    126,
                )

                if (
                    rect.collidepoint(
                        x,
                        y,
                    )
                ):

                    self.starter_select = (
                        index
                    )

                    self.new_game(
                        STARTERS[
                            index
                        ]
                    )

                    return

        # ====================================================
        # TEAM
        # ====================================================

        elif (
            self.state
            ==
            "team"
        ):

            for index in range(
                MAX_TEAM_SIZE
            ):

                column = (
                    index // 3
                )

                row = (
                    index % 3
                )

                rect = pygame.Rect(

                    17
                    +
                    column
                    *
                    145,

                    37
                    +
                    row
                    *
                    38,

                    140,

                    34,
                )

                if not (
                    rect.collidepoint(
                        x,
                        y,
                    )
                ):

                    continue

                self.team_select = (
                    index
                )

                self.choose_team_member(
                    index
                )

                return

        # ====================================================
        # BATTLE
        # ====================================================

        elif (
            self.state
            ==
            "battle"
            and
            self.battle
        ):

            battle = (
                self.battle
            )

            if (
                battle.phase
                !=
                "input"
            ):

                return

            # Cambio obbligatorio

            if (
                battle.must_switch
            ):

                if pygame.Rect(
                    150,
                    139,
                    155,
                    27,
                ).collidepoint(
                    x,
                    y,
                ):

                    self.return_state = (
                        "battle"
                    )

                    self.team_select = (
                        self.active
                    )

                    self.state = (
                        "team"
                    )

                return

            # C SFERA

            if pygame.Rect(
                142,
                123,
                41,
                14,
            ).collidepoint(
                x,
                y,
            ):

                battle.capture()

                return

            # B ZAINO

            if pygame.Rect(
                185,
                123,
                41,
                14,
            ).collidepoint(
                x,
                y,
            ):

                battle.menu = (

                    "bag"

                    if
                    battle.menu
                    ==
                    "moves"

                    else

                    "moves"
                )

                return

            # Q TEAM

            if pygame.Rect(
                228,
                123,
                41,
                14,
            ).collidepoint(
                x,
                y,
            ):

                self.return_state = (
                    "battle"
                )

                self.team_select = (
                    self.active
                )

                self.state = (
                    "team"
                )

                return

            # F FUGA

            if pygame.Rect(
                271,
                123,
                41,
                14,
            ).collidepoint(
                x,
                y,
            ):

                battle.run()

                return

            # MOSSE

            if (
                battle.menu
                ==
                "moves"
            ):

                for index in range(
                    4
                ):

                    rect_x = (

                        142

                        +
                        (
                            index
                            %
                            2
                        )
                        *
                        85
                    )

                    rect_y = (

                        141

                        +
                        (
                            index
                            //
                            2
                        )
                        *
                        17
                    )

                    rect = pygame.Rect(

                        rect_x,

                        rect_y,

                        82,

                        16,
                    )

                    if (
                        rect.collidepoint(
                            x,
                            y,
                        )
                    ):

                        battle.choose_move(
                            index
                        )

                        return

            # ZAINO

            else:

                if pygame.Rect(
                    142,
                    144,
                    82,
                    27,
                ).collidepoint(
                    x,
                    y,
                ):

                    battle.capture()

                    return

                if pygame.Rect(
                    227,
                    144,
                    85,
                    27,
                ).collidepoint(
                    x,
                    y,
                ):

                    battle.use_potion()

                    return

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        self.update_transition(
            dt
        )

        if (
            self.transition
            and
            self.transition_dir
            >
            0
        ):

            return

        if (
            self.state
            ==
            "world"
        ):

            self.update_world(
                dt
            )

        elif (
            self.state
            ==
            "battle"
            and
            self.battle
        ):

            self.battle.update(
                dt
            )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        if (
            self.state
            ==
            "title"
        ):

            self.draw_title()

        elif (
            self.state
            ==
            "starter"
        ):

            self.draw_starter()

        elif (
            self.state
            ==
            "world"
        ):

            self.draw_world()

        elif (
            self.state
            ==
            "battle"
            and
            self.battle
        ):

            self.battle.draw(

                self.canvas,

                self.assets,

                pygame.time.get_ticks()
                /
                1000,
            )

        elif (
            self.state
            ==
            "team"
        ):

            self.draw_team()

        elif (
            self.state
            ==
            "help"
        ):

            self.draw_help()

        elif (
            self.state
            ==
            "pause"
        ):

            self.draw_pause()

        elif (
            self.state
            ==
            "ending"
        ):

            self.draw_ending()

        self.draw_transition()

        self.present()

    # ========================================================
    # PRESENT
    # ========================================================

    def present(self):

        window_width, window_height = (
            self.window.get_size()
        )

        scale = max(

            1,

            int(

                min(

                    window_width
                    /
                    BASE_W,

                    window_height
                    /
                    BASE_H,
                )
            ),
        )

        scaled_width = (
            BASE_W
            *
            scale
        )

        scaled_height = (
            BASE_H
            *
            scale
        )

        scaled = pygame.transform.scale(

            self.canvas,

            (
                scaled_width,
                scaled_height,
            ),
        )

        self.window.fill(
            (
                8,
                16,
                21,
            )
        )

        self.window.blit(

            scaled,

            (
                (
                    window_width
                    -
                    scaled_width
                )
                //
                2,

                (
                    window_height
                    -
                    scaled_height
                )
                //
                2,
            ),
        )

        pygame.display.flip()

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        while (
            self.running
        ):

            dt = min(

                .05,

                self.clock.tick(
                    FPS
                )
                /
                1000,
            )

            for event in (
                pygame.event.get()
            ):

                if (
                    event.type
                    ==
                    pygame.QUIT
                ):

                    self.running = False

                elif (
                    event.type
                    ==
                    pygame.KEYDOWN
                ):

                    self.handle_keydown(
                        event.key
                    )

                elif (
                    event.type
                    ==
                    pygame.MOUSEMOTION
                ):

                    self.handle_mouse_motion(
                        event.pos
                    )

                elif (
                    event.type
                    ==
                    pygame.MOUSEBUTTONDOWN
                ):

                    self.handle_mouse_down(
                        event.pos,
                        event.button,
                    )

                elif (
                    event.type
                    ==
                    pygame.VIDEORESIZE
                    and
                    not
                    self.fullscreen
                ):

                    self.window = (
                        pygame.display.set_mode(

                            (
                                max(
                                    640,
                                    event.w,
                                ),

                                max(
                                    360,
                                    event.h,
                                ),
                            ),

                            pygame.RESIZABLE,
                        )
                    )

            self.update(
                dt
            )

            self.draw()

        if (
            self.state
            not in (
                "battle",
                "title",
                "starter",
            )
        ):

            self.save()

        pygame.quit()