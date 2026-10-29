from __future__ import annotations

import math

import pygame

from models import Particle
from data import effectiveness, TRAINERS
from settings import COLORS, TYPE_COLORS

from ui import (
    panel,
    text,
    hp_bar,
    button,
    type_badge,
    dialogue,
)


# ============================================================
# CONFIG
# ============================================================

MAX_TEAM_SIZE = 6


class BattleController:

    def __init__(
        self,
        game,
        enemies,
        trainer_index=None,
        intro="",
    ):

        self.game = game

        self.enemies = enemies

        self.index = 0

        self.trainer_index = (
            trainer_index
        )

        self.rng = (
            game.rng
        )

        self.message = (

            intro

            or

            (
                f"Un {self.enemy.name} "
                "selvatico appare!"
            )
        )

        self.phase = "input"

        self.menu = "moves"

        self.anim = None

        self.delay = 0

        self.pending_enemy = False

        self.must_switch = False

        self.run_attempts = 0

        self.enemy_heals = 0

        self.display_enemy_hp = float(
            self.enemy.hp
        )

        self.display_hero_hp = float(
            game.hero.hp
        )

        self.particles = []

        self.flash = 0

        self.shake = 0

        self.capture_anim = None

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def enemy(self):

        return self.enemies[
            self.index
        ]

    @property
    def wild(self):

        return (
            self.trainer_index
            is None
        )

    # ========================================================
    # PARTICLES
    # ========================================================

    def spawn_particles(
        self,
        x,
        y,
        color,
        count=14,
        speed=65,
    ):

        for _ in range(
            count
        ):

            angle = (
                self.rng.random()
                *
                math.tau
            )

            particle_speed = (
                self.rng.uniform(
                    speed * .35,
                    speed,
                )
            )

            self.particles.append(

                Particle(

                    x,

                    y,

                    math.cos(
                        angle
                    )
                    *
                    particle_speed,

                    math.sin(
                        angle
                    )
                    *
                    particle_speed,

                    self.rng.uniform(
                        .25,
                        .55,
                    ),

                    color,

                    self.rng.choice(
                        (
                            1,
                            1,
                            2,
                        )
                    ),

                    42,
                )
            )

    # ========================================================
    # MOVE
    # ========================================================

    def choose_move(
        self,
        index,
    ):

        if (
            self.phase
            !=
            "input"
            or
            self.must_switch
            or
            not
            0
            <=
            index
            <
            4
        ):

            return

        move = (
            self.game.hero.moves[
                index
            ]
        )

        if (
            self.game.hero.pp[
                index
            ]
            <=
            0
        ):

            self.message = (
                "NESSUN PP"
            )

            return

        if (
            move.get(
                "heal"
            )
            and
            self.game.hero.hp
            >=
            self.game.hero.max_hp
        ):

            self.message = (
                "PS GIA' AL MASSIMO"
            )

            return

        self._start_move(
            True,
            index,
        )

    # ========================================================
    # ENEMY AI
    # ========================================================

    def _enemy_choice(self):

        enemy = (
            self.enemy
        )

        if (
            enemy.hp
            <
            enemy.max_hp
            *
            .3
            and
            enemy.pp[3]
            >
            0
            and
            self.enemy_heals
            <
            1
        ):

            self.enemy_heals += 1

            return 3

        options = [

            index

            for (
                index,
                move,
            )
            in enumerate(
                enemy.moves[
                    :3
                ]
            )

            if
            enemy.pp[
                index
            ]
            >
            0
        ]

        if not options:

            return 0

        def score(
            index,
        ):

            move = (
                enemy.moves[
                    index
                ]
            )

            return (

                move[
                    "power"
                ]

                *

                effectiveness(

                    move[
                        "type"
                    ],

                    self.game.hero.element,
                )

                +

                self.rng.random()
                *
                4
            )

        return max(
            options,
            key=score,
        )

    # ========================================================
    # START MOVE
    # ========================================================

    def _start_move(
        self,
        hero_turn,
        index,
    ):

        actor = (

            self.game.hero

            if
            hero_turn

            else

            self.enemy
        )

        if (
            actor.pp[
                index
            ]
            <=
            0
        ):

            index = 0

        actor.pp[
            index
        ] -= 1

        move = (
            actor.moves[
                index
            ]
        )

        self.phase = (
            "anim"
        )

        self.anim = {

            "hero":
                hero_turn,

            "move":
                index,

            "t":
                0.0,

            "duration":
                (
                    .62

                    if
                    not
                    move.get(
                        "heal"
                    )

                    else

                    .55
                ),

            "impact":
                .27,

            "applied":
                False,
        }

        self.message = (
            f"{actor.name} USA "
            f"{move['name']}"
        )

    # ========================================================
    # APPLY MOVE
    # ========================================================

    def _apply_move(
        self,
        hero_turn,
        index,
    ):

        actor = (

            self.game.hero

            if
            hero_turn

            else

            self.enemy
        )

        target = (

            self.enemy

            if
            hero_turn

            else

            self.game.hero
        )

        move = (
            actor.moves[
                index
            ]
        )

        # ====================================================
        # HEAL
        # ====================================================

        if (
            move.get(
                "heal"
            )
        ):

            amount = min(

                actor.max_hp
                -
                actor.hp,

                max(

                    1,

                    int(

                        actor.max_hp

                        *

                        move[
                            "heal"
                        ]
                    ),
                ),
            )

            actor.hp += (
                amount
            )

            self.message = (
                f"{actor.name} +{amount} PS"
            )

            self.spawn_particles(

                90
                if hero_turn
                else
                244,

                105
                if hero_turn
                else
                63,

                (
                    126,
                    213,
                    135,
                ),

                18,

                45,
            )

            return

        # ====================================================
        # DAMAGE
        # ====================================================

        multiplier = (
            effectiveness(

                move[
                    "type"
                ],

                target.element,
            )
        )

        stab = (

            1.2

            if
            move[
                "type"
            ]
            ==
            actor.element

            else

            1.0
        )

        critical = (
            self.rng.random()
            <
            .065
        )

        raw_damage = (

            (
                move[
                    "power"
                ]

                +
                actor.level
                *
                .9
            )

            *

            actor.attack

            /

            max(
                1,
                target.defense,
            )

            *

            .40
        )

        damage = max(

            1,

            int(

                raw_damage

                *

                multiplier

                *

                stab

                *

                self.rng.uniform(
                    .92,
                    1.06,
                )

                *

                (
                    1.4
                    if critical
                    else
                    1
                )
            ),
        )

        target.hp = max(

            0,

            target.hp
            -
            damage,
        )

        suffix = ""

        if (
            multiplier
            >
            1
        ):

            suffix = (
                " SUPER!"
            )

        elif (
            multiplier
            <
            1
        ):

            suffix = (
                " DEBOLE"
            )

        if (
            critical
        ):

            suffix += (
                " CRITICO!"
            )

        self.message = (
            f"{target.name} -{damage} PS"
            f"{suffix}"
        )

        position = (

            (
                239,
                66,
            )

            if
            hero_turn

            else

            (
                78,
                111,
            )
        )

        self.spawn_particles(

            *position,

            TYPE_COLORS.get(

                move[
                    "type"
                ],

                COLORS[
                    "white"
                ],
            ),

            18,

            80,
        )

        self.flash = .12

        self.shake = .16

    # ========================================================
    # POTION
    # ========================================================

    def use_potion(self):

        if (
            self.phase
            !=
            "input"
            or
            self.must_switch
        ):

            return

        if (
            self.game.potions
            <=
            0
        ):

            self.message = (
                "NESSUNA POZIONE"
            )

            return

        hero = (
            self.game.hero
        )

        if (
            hero.hp
            <=
            0
            or
            hero.hp
            >=
            hero.max_hp
        ):

            self.message = (
                "NON PUOI USARLA"
            )

            return

        self.game.potions -= 1

        amount = min(

            35,

            hero.max_hp
            -
            hero.hp,
        )

        hero.hp += (
            amount
        )

        self.message = (
            f"{hero.name} +{amount} PS"
        )

        self.phase = (
            "delay"
        )

        self.delay = .35

        self.pending_enemy = True

    # ========================================================
    # CAPTURE
    # ========================================================

    def capture(self):

        if (
            self.phase
            !=
            "input"
            or
            self.must_switch
        ):

            return

        if (
            not
            self.wild
        ):

            self.message = (
                "NON PUOI CATTURARLO"
            )

            return

        # ====================================================
        # MASSIMO 6
        # ====================================================

        if (
            len(
                self.game.team
            )
            >=
            MAX_TEAM_SIZE
        ):

            self.message = (
                "SQUADRA PIENA 6/6"
            )

            return

        if (
            self.game.balls
            <=
            0
        ):

            self.message = (
                "NESSUNA SFERA"
            )

            return

        self.game.balls -= 1

        chance = min(

            .94,

            .24

            +

            (
                1

                -

                self.enemy.hp

                /

                self.enemy.max_hp
            )

            *

            .70,
        )

        success = (
            self.rng.random()
            <
            chance
        )

        self.phase = (
            "capture"
        )

        self.capture_anim = {

            "t":
                0.0,

            "success":
                success,

            "shakes":
                0,
        }

        self.message = (
            "LANCIO SFERA!"
        )

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        if (
            self.phase
            !=
            "input"
            or
            self.must_switch
        ):

            return

        if (
            not
            self.wild
        ):

            self.message = (
                "NON PUOI FUGGIRE"
            )

            return

        self.run_attempts += 1

        chance = min(

            1,

            .65

            +

            .18

            *

            (
                self.run_attempts
                -
                1
            ),
        )

        if (
            self.rng.random()
            <
            chance
        ):

            self.game.finish_battle(
                "FUGA RIUSCITA"
            )

        else:

            self.message = (
                "FUGA FALLITA"
            )

            self.phase = (
                "delay"
            )

            self.delay = .3

            self.pending_enemy = True

    # ========================================================
    # SWITCH
    # ========================================================

    def switch(
        self,
        index,
    ):

        if not (
            0
            <=
            index
            <
            len(
                self.game.team
            )
        ):

            return False

        if (
            index
            ==
            self.game.active
        ):

            return False

        if (
            self.game.team[
                index
            ].hp
            <=
            0
        ):

            return False

        forced = (
            self.must_switch
        )

        self.game.active = (
            index
        )

        self.must_switch = False

        self.display_hero_hp = float(
            self.game.hero.hp
        )

        self.message = (
            f"VAI {self.game.hero.name}!"
        )

        if (
            forced
        ):

            self.phase = (
                "input"
            )

        else:

            self.phase = (
                "delay"
            )

            self.delay = .3

            self.pending_enemy = True

        return True

    # ========================================================
    # KO
    # ========================================================

    def _resolve_ko(self):

        # ====================================================
        # ENEMY KO
        # ====================================================

        if (
            self.enemy.hp
            <=
            0
        ):

            defeated = (
                self.enemy
            )

            reward = (
                14
                +
                defeated.level
                *
                5
            )

            # Esperienza a tutta la squadra viva

            for (
                index,
                creature,
            ) in enumerate(
                self.game.team
            ):

                if (
                    creature.hp
                    >
                    0
                ):

                    creature.gain_xp(

                        reward

                        if
                        index
                        ==
                        self.game.active

                        else

                        max(
                            1,
                            reward // 2,
                        )
                    )

            self.game.coins += (
                8
                +
                defeated.level
            )

            # Altro Pokémon dell'allenatore

            if (
                self.index
                +
                1
                <
                len(
                    self.enemies
                )
            ):

                self.index += 1

                self.enemy_heals = 0

                self.display_enemy_hp = float(
                    self.enemy.hp
                )

                self.message = (
                    f"ENTRA {self.enemy.name}"
                )

                self.phase = (
                    "delay"
                )

                self.delay = .7

                self.pending_enemy = False

                return True

            trainer = (
                self.trainer_index
            )

            # Trainer

            if (
                trainer
                is not None
            ):

                self.game.defeated.add(
                    trainer
                )

                self.game.coins += (
                    TRAINERS[
                        trainer
                    ][
                        "reward"
                    ]
                )

                self.game.potions += 2

                self.game.balls += 2

                if (
                    trainer
                    ==
                    2
                ):

                    self.game.completed = True

                    self.game.finish_battle(
                        "HAI BATTUTO ALBA!",
                        ending=True,
                    )

                    return True

                self.game.finish_battle(
                    "MEDAGLIA OTTENUTA!"
                )

                return True

            # Wild

            self.game.finish_battle(
                "VITTORIA!"
            )

            return True

        # ====================================================
        # HERO KO
        # ====================================================

        if (
            self.game.hero.hp
            <=
            0
        ):

            living = [

                index

                for (
                    index,
                    creature,
                )
                in enumerate(
                    self.game.team
                )

                if
                creature.hp
                >
                0
            ]

            if (
                living
            ):

                self.must_switch = True

                self.phase = (
                    "input"
                )

                self.message = (
                    "KO! SCEGLI UN ALTRO"
                )

            else:

                for creature in (
                    self.game.team
                ):

                    creature.heal_full()

                self.game.active = 0

                self.game.coins = max(

                    0,

                    self.game.coins
                    -
                    20,
                )

                self.game.reset_to_spawn()

                self.game.finish_battle(
                    "SQUADRA KO"
                )

            return True

        return False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        for particle in (
            self.particles
        ):

            particle.update(
                dt
            )

        self.particles[:] = [

            particle

            for particle
            in self.particles

            if particle.life > 0
        ]

        self.flash = max(
            0,
            self.flash - dt,
        )

        self.shake = max(
            0,
            self.shake - dt,
        )

        self.display_enemy_hp += (

            self.enemy.hp

            -

            self.display_enemy_hp

        ) * min(
            1,
            dt * 10,
        )

        self.display_hero_hp += (

            self.game.hero.hp

            -

            self.display_hero_hp

        ) * min(
            1,
            dt * 10,
        )

        # ====================================================
        # CAPTURE
        # ====================================================

        if (
            self.phase
            ==
            "capture"
        ):

            animation = (
                self.capture_anim
            )

            animation[
                "t"
            ] += dt

            if (
                animation[
                    "t"
                ]
                >=
                1.75
            ):

                if (
                    animation[
                        "success"
                    ]
                ):

                    caught = (
                        self.enemy
                    )

                    # Ulteriore sicurezza

                    if (
                        len(
                            self.game.team
                        )
                        <
                        MAX_TEAM_SIZE
                    ):

                        self.game.team.append(
                            caught
                        )

                        self.game.finish_battle(
                            f"{caught.name} CATTURATO!"
                        )

                    else:

                        self.phase = (
                            "input"
                        )

                        self.message = (
                            "SQUADRA PIENA 6/6"
                        )

                else:

                    self.message = (
                        "SI E' LIBERATO!"
                    )

                    self.phase = (
                        "delay"
                    )

                    self.delay = .35

                    self.pending_enemy = True

            return

        # ====================================================
        # ATTACK ANIMATION
        # ====================================================

        if (
            self.phase
            ==
            "anim"
        ):

            animation = (
                self.anim
            )

            animation[
                "t"
            ] += dt

            if (
                not
                animation[
                    "applied"
                ]
                and
                animation[
                    "t"
                ]
                >=
                animation[
                    "impact"
                ]
            ):

                animation[
                    "applied"
                ] = True

                self._apply_move(

                    animation[
                        "hero"
                    ],

                    animation[
                        "move"
                    ],
                )

            if (
                animation[
                    "t"
                ]
                >=
                animation[
                    "duration"
                ]
            ):

                hero_turn = (
                    animation[
                        "hero"
                    ]
                )

                self.anim = None

                if (
                    self._resolve_ko()
                ):

                    return

                if (
                    hero_turn
                ):

                    self.phase = (
                        "delay"
                    )

                    self.delay = .35

                    self.pending_enemy = True

                else:

                    self.phase = (
                        "input"
                    )

        # ====================================================
        # DELAY
        # ====================================================

        elif (
            self.phase
            ==
            "delay"
        ):

            self.delay -= (
                dt
            )

            if (
                self.delay
                <=
                0
            ):

                if (
                    self.pending_enemy
                ):

                    self.pending_enemy = False

                    self._start_move(

                        False,

                        self._enemy_choice(),
                    )

                else:

                    self.phase = (
                        "input"
                    )

    # ========================================================
    # STATUS
    # ========================================================

    def _status(
        self,
        surface,
        assets,
        creature,
        rect,
        hp_value,
    ):

        rect = panel(

            surface,

            rect,

            (
                242,
                238,
                216,
            ),
        )

        text(

            surface,

            assets.font,

            creature.name,

            (
                rect.x + 7,
                rect.y + 6,
            ),

            COLORS[
                "ink"
            ],

            shadow=False,
        )

        text(

            surface,

            assets.font_tiny,

            f"LV {creature.level}",

            (
                rect.right - 6,
                rect.y + 7,
            ),

            COLORS[
                "ink"
            ],

            "topright",

            False,
        )

        type_badge(

            surface,

            assets.font_tiny,

            creature.element,

            (
                rect.x + 7,
                rect.y + 19,
                33,
                9,
            ),
        )

        hp_bar(

            surface,

            (
                rect.x + 44,
                rect.y + 20,
                rect.width - 52,
                6,
            ),

            hp_value
            /
            creature.max_hp,
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface,
        assets,
        t,
    ):

        # ====================================================
        # BACKGROUND
        # ====================================================

        surface.fill(
            (
                128,
                177,
                120,
            )
        )

        pygame.draw.rect(
            surface,
            (
                83,
                132,
                91,
            ),
            (
                0,
                0,
                320,
                67,
            ),
        )

        # Foresta

        for x in range(
            0,
            320,
            20,
        ):

            pygame.draw.circle(
                surface,
                (
                    39,
                    86,
                    62,
                ),
                (
                    x + 8,
                    30
                    +
                    (
                        x % 3
                    )
                    *
                    3,
                ),
                24,
            )

            pygame.draw.circle(
                surface,
                (
                    68,
                    126,
                    71,
                ),
                (
                    x + 11,
                    22
                    +
                    (
                        x % 2
                    )
                    *
                    4,
                ),
                18,
            )

        # Acqua

        pygame.draw.rect(
            surface,
            COLORS[
                "water"
            ],
            (
                0,
                48,
                320,
                48,
            ),
        )

        for y in (
            55,
            67,
            83,
        ):

            offset = (
                int(
                    t * 24
                    +
                    y
                )
                %
                20
            )

            for x in range(
                -20,
                340,
                40,
            ):

                pygame.draw.line(
                    surface,
                    COLORS[
                        "water_light"
                    ],
                    (
                        x
                        +
                        offset,
                        y,
                    ),
                    (
                        x
                        +
                        offset
                        +
                        16,
                        y,
                    ),
                )

        # Piattaforme

        pygame.draw.ellipse(
            surface,
            (
                94,
                139,
                77,
            ),
            (
                174,
                67,
                119,
                27,
            ),
        )

        pygame.draw.ellipse(
            surface,
            (
                196,
                170,
                112,
            ),
            (
                185,
                70,
                96,
                19,
            ),
        )

        pygame.draw.ellipse(
            surface,
            (
                88,
                134,
                74,
            ),
            (
                13,
                91,
                145,
                30,
            ),
        )

        pygame.draw.ellipse(
            surface,
            (
                202,
                176,
                119,
            ),
            (
                27,
                95,
                114,
                21,
            ),
        )

        # ====================================================
        # MOVIMENTO SPRITE
        # ====================================================

        hero_offset = (
            pygame.Vector2()
        )

        enemy_offset = (
            pygame.Vector2()
        )

        if (
            self.anim
        ):

            animation = (
                self.anim
            )

            pulse = math.sin(

                min(
                    1,
                    animation[
                        "t"
                    ]
                    /
                    animation[
                        "duration"
                    ],
                )

                *

                math.pi
            )

            offset = pygame.Vector2(
                25 * pulse,
                -4 * pulse,
            )

            if (
                animation[
                    "hero"
                ]
            ):

                hero_offset += (
                    offset
                )

            else:

                enemy_offset -= (
                    offset
                )

        shake = (
            pygame.Vector2()
        )

        if (
            self.shake
            >
            0
        ):

            shake.update(

                self.rng.randint(
                    -2,
                    2,
                ),

                self.rng.randint(
                    -1,
                    1,
                ),
            )

        # ====================================================
        # SPRITE
        # ====================================================

        enemy_sprite = (
            assets.creature(

                self.enemy.species,

                "front",

                int(
                    t * 3
                )
                % 2,

                2,
            )
        )

        hero_sprite = (
            assets.creature(

                self.game.hero.species,

                "back",

                int(
                    t * 3
                )
                % 2,

                2,
            )
        )

        surface.blit(
            enemy_sprite,
            (
                199
                +
                int(
                    enemy_offset.x
                    +
                    shake.x
                ),

                25
                +
                int(
                    enemy_offset.y
                    +
                    shake.y
                ),
            ),
        )

        surface.blit(
            hero_sprite,
            (
                36
                +
                int(
                    hero_offset.x
                    +
                    shake.x
                ),

                56
                +
                int(
                    hero_offset.y
                    +
                    shake.y
                ),
            ),
        )

        # ====================================================
        # CAPTURE BALL
        # ====================================================

        if (
            self.phase
            ==
            "capture"
            and
            self.capture_anim
        ):

            capture_t = (
                self.capture_anim[
                    "t"
                ]
            )

            if (
                capture_t
                <
                .58
            ):

                progress = min(
                    1,
                    capture_t / .58,
                )

                x = (
                    72
                    +
                    (
                        225 - 72
                    )
                    *
                    progress
                )

                y = (
                    88
                    +
                    (
                        56 - 88
                    )
                    *
                    progress
                    -
                    40
                    *
                    math.sin(
                        math.pi
                        *
                        progress
                    )
                )

            else:

                elapsed = (
                    capture_t
                    -
                    .58
                )

                x = (
                    225
                    +
                    math.sin(
                        elapsed
                        *
                        18
                    )
                    *
                    3
                )

                y = 60

            surface.blit(

                assets.ball(
                    int(
                        t * 6
                    )
                    % 2
                ),

                (
                    int(
                        x
                    ),

                    int(
                        y
                    ),
                ),
            )

        # ====================================================
        # HUD STATUS
        # ====================================================

        self._status(

            surface,

            assets,

            self.enemy,

            (
                6,
                5,
                139,
                35,
            ),

            self.display_enemy_hp,
        )

        self._status(

            surface,

            assets,

            self.game.hero,

            (
                175,
                79,
                139,
                35,
            ),

            self.display_hero_hp,
        )

        # ====================================================
        # PARTICLES
        # ====================================================

        for particle in (
            self.particles
        ):

            pygame.draw.circle(

                surface,

                particle.color,

                (
                    int(
                        particle.x
                    ),

                    int(
                        particle.y
                    ),
                ),

                particle.size,
            )

        # ====================================================
        # LOWER UI
        # ====================================================

        pygame.draw.rect(
            surface,
            (
                24,
                37,
                45,
            ),
            (
                0,
                116,
                320,
                64,
            ),
        )

        dialogue(

            surface,

            assets,

            self.message,

            "1-4 MOSSE",

            rect=(
                4,
                120,
                132,
                56,
            ),
        )

        panel(

            surface,

            (
                139,
                120,
                177,
                56,
            ),

            (
                226,
                231,
                207,
            ),
        )

        # ====================================================
        # INPUT
        # ====================================================

        if (
            self.phase
            ==
            "input"
            and
            not
            self.must_switch
        ):

            bag_label = (

                "B MOSSE"

                if
                self.menu
                ==
                "bag"

                else

                "B ZAINO"
            )

            actions = [

                (
                    (
                        142,
                        123,
                        41,
                        14,
                    ),

                    "C SFERA",

                    (
                        self.wild

                        and
                        self.game.balls
                        >
                        0

                        and
                        len(
                            self.game.team
                        )
                        <
                        MAX_TEAM_SIZE
                    ),
                ),

                (
                    (
                        185,
                        123,
                        41,
                        14,
                    ),

                    bag_label,

                    True,
                ),

                (
                    (
                        228,
                        123,
                        41,
                        14,
                    ),

                    "Q TEAM",

                    len(
                        self.game.team
                    )
                    >
                    1,
                ),

                (
                    (
                        271,
                        123,
                        41,
                        14,
                    ),

                    "F FUGA",

                    self.wild,
                ),
            ]

            for (
                rect,
                label,
                enabled,
            ) in actions:

                button(

                    surface,

                    assets.font_tiny,

                    rect,

                    label,

                    False,

                    enabled,

                    label.startswith(
                        "C "
                    ),
                )

            # ================================================
            # MOVES
            # ================================================

            if (
                self.menu
                ==
                "moves"
            ):

                for (
                    index,
                    move,
                ) in enumerate(
                    self.game.hero.moves
                ):

                    x = (
                        142
                        +
                        (
                            index % 2
                        )
                        *
                        85
                    )

                    y = (
                        141
                        +
                        (
                            index // 2
                        )
                        *
                        17
                    )

                    name = (
                        move[
                            "name"
                        ]
                    )

                    if (
                        len(
                            name
                        )
                        >
                        10
                    ):

                        name = (
                            name[
                                :9
                            ]
                            +
                            "."
                        )

                    button(

                        surface,

                        assets.font_tiny,

                        (
                            x,
                            y,
                            82,
                            16,
                        ),

                        (
                            f"{index + 1} "
                            f"{name}"
                        ),

                        False,

                        self.game.hero.pp[
                            index
                        ]
                        >
                        0,

                        index
                        ==
                        1,
                    )

            # ================================================
            # BAG
            # ================================================

            else:

                button(

                    surface,

                    assets.font_small,

                    (
                        142,
                        144,
                        82,
                        27,
                    ),

                    (
                        f"1 SFERA X"
                        f"{self.game.balls}"
                    ),

                    False,

                    (
                        self.wild

                        and
                        self.game.balls
                        >
                        0

                        and
                        len(
                            self.game.team
                        )
                        <
                        MAX_TEAM_SIZE
                    ),

                    True,
                )

                button(

                    surface,

                    assets.font_small,

                    (
                        227,
                        144,
                        85,
                        27,
                    ),

                    (
                        f"2 CURA X"
                        f"{self.game.potions}"
                    ),

                    False,

                    self.game.potions
                    >
                    0,

                    False,
                )

        # ====================================================
        # MUST SWITCH
        # ====================================================

        elif (
            self.must_switch
        ):

            button(

                surface,

                assets.font_small,

                (
                    150,
                    139,
                    155,
                    27,
                ),

                "Q SCEGLI COMPAGNO",

                True,

                True,

                True,
            )

        else:

            text(

                surface,

                assets.font_small,

                "ATTENDI...",

                (
                    227,
                    150,
                ),

                COLORS[
                    "ink"
                ],

                "center",

                False,
            )

        # ====================================================
        # FLASH
        # ====================================================

        if (
            self.flash
            >
            0
        ):

            overlay = pygame.Surface(
                (
                    320,
                    180,
                ),
                pygame.SRCALPHA,
            )

            overlay.fill(
                (
                    255,
                    247,
                    223,
                    int(

                        120

                        *

                        self.flash

                        /

                        .12
                    ),
                )
            )

            surface.blit(
                overlay,
                (
                    0,
                    0,
                ),
            )