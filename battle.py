from __future__ import annotations

import math
import random

import pygame

from models import Creature, Particle
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


class BattleController:

    def __init__(
        self,
        game,
        enemies,
        trainer_index=None,
        intro="",
    ):

        self.game=game

        self.enemies=enemies

        self.index=0

        self.trainer_index=trainer_index

        self.rng=game.rng

        self.message=(
            intro
            or
            f"Un {self.enemy.name} selvatico appare!"
        )

        self.phase="input"

        self.menu="moves"

        self.anim=None

        self.delay=0

        self.pending_enemy=False

        self.must_switch=False

        self.run_attempts=0

        self.enemy_heals=0

        self.display_enemy_hp=float(
            self.enemy.hp
        )

        self.display_hero_hp=float(
            game.hero.hp
        )

        self.particles=[]

        self.flash=0

        self.shake=0

        self.capture_anim=None

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
    # PARTICELLE
    # ========================================================

    def spawn_particles(
        self,
        x,
        y,
        color,
        count=14,
        speed=65,
    ):

        for _ in range(count):

            a=self.rng.random()*math.tau

            sp=self.rng.uniform(
                speed*.35,
                speed,
            )

            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(a)*sp,
                    math.sin(a)*sp,
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
    # MOSSE
    # ========================================================

    def choose_move(self, idx):

        if (
            self.phase!="input"
            or
            self.must_switch
            or
            not 0<=idx<4
        ):
            return

        move=self.game.hero.moves[
            idx
        ]

        if self.game.hero.pp[idx]<=0:
            self.message=(
                "Quella mossa non ha piu' PP."
            )
            return

        if (
            move.get("heal")
            and
            self.game.hero.hp
            >=
            self.game.hero.max_hp
        ):
            self.message=(
                "I PS sono gia' al massimo."
            )
            return

        self._start_move(
            True,
            idx,
        )

    def _enemy_choice(self):

        e=self.enemy

        if (
            e.hp<e.max_hp*.3
            and
            e.pp[3]>0
            and
            self.enemy_heals<1
        ):

            self.enemy_heals+=1

            return 3

        options=[
            i
            for i,m in enumerate(
                e.moves[:3]
            )
            if e.pp[i]>0
        ]

        if not options:
            return 0

        def score(i):

            m=e.moves[i]

            return (
                m["power"]
                *
                effectiveness(
                    m["type"],
                    self.game.hero.element,
                )
                +
                self.rng.random()*4
            )

        return max(
            options,
            key=score,
        )

    def _start_move(
        self,
        hero_turn,
        idx,
    ):

        actor=(
            self.game.hero
            if hero_turn
            else self.enemy
        )

        if actor.pp[idx]<=0:
            idx=0

        actor.pp[idx]-=1

        move=actor.moves[idx]

        self.phase="anim"

        self.anim={
            "hero":hero_turn,
            "move":idx,
            "t":0.0,
            "duration":(
                .62
                if not move.get("heal")
                else .55
            ),
            "impact":.27,
            "applied":False,
        }

        self.message=(
            f"{actor.name} usa "
            f"{move['name']}!"
        )

    def _apply_move(
        self,
        hero_turn,
        idx,
    ):

        actor=(
            self.game.hero
            if hero_turn
            else self.enemy
        )

        target=(
            self.enemy
            if hero_turn
            else self.game.hero
        )

        move=actor.moves[idx]

        # Cura

        if move.get("heal"):

            amount=min(
                actor.max_hp-actor.hp,
                max(
                    1,
                    int(
                        actor.max_hp
                        *
                        move["heal"]
                    ),
                ),
            )

            actor.hp+=amount

            self.message=(
                f"{actor.name} recupera "
                f"{amount} PS!"
            )

            self.spawn_particles(
                90
                if hero_turn
                else 244,
                105
                if hero_turn
                else 63,
                (
                    126,
                    213,
                    135,
                ),
                18,
                45,
            )

            return

        mult=effectiveness(
            move["type"],
            target.element,
        )

        stab=(
            1.2
            if
            move["type"]==actor.element
            else
            1.0
        )

        critical=(
            self.rng.random()
            <.065
        )

        raw=(
            (
                move["power"]
                +
                actor.level*.9
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

        dmg=max(
            1,
            int(
                raw
                *
                mult
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
                    else 1
                )
            ),
        )

        target.hp=max(
            0,
            target.hp-dmg,
        )

        suffix=""

        if mult>1:
            suffix=" Super efficace!"

        elif mult<1:
            suffix=" Poco efficace."

        if critical:
            suffix+=" Critico!"

        self.message=(
            f"{target.name} perde "
            f"{dmg} PS."
            f"{suffix}"
        )

        pos=(
            (239,66)
            if hero_turn
            else
            (78,111)
        )

        self.spawn_particles(
            *pos,
            TYPE_COLORS.get(
                move["type"],
                COLORS["white"],
            ),
            18,
            80,
        )

        self.flash=.12

        self.shake=.16

    # ========================================================
    # POZIONI
    # ========================================================

    def use_potion(self):

        if (
            self.phase!="input"
            or
            self.must_switch
        ):
            return

        if self.game.potions<=0:
            self.message=(
                "Non hai pozioni."
            )
            return

        h=self.game.hero

        if (
            h.hp<=0
            or
            h.hp>=h.max_hp
        ):
            self.message=(
                "Non puoi usare "
                "la pozione adesso."
            )
            return

        self.game.potions-=1

        amount=min(
            35,
            h.max_hp-h.hp,
        )

        h.hp+=amount

        self.message=(
            f"{h.name} recupera "
            f"{amount} PS."
        )

        self.phase="delay"

        self.delay=.35

        self.pending_enemy=True

    # ========================================================
    # CATTURA
    # ========================================================

    def capture(self):

        if (
            self.phase!="input"
            or
            self.must_switch
        ):
            return

        if not self.wild:
            self.message=(
                "Non puoi catturare "
                "le creature degli allenatori!"
            )
            return

        if len(self.game.team)>=3:
            self.message=(
                "Squadra piena: "
                "massimo 3 creature."
            )
            return

        if self.game.balls<=0:
            self.message=(
                "Non hai piu' sfere."
            )
            return

        self.game.balls-=1

        chance=min(
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
            *.70,
        )

        success=(
            self.rng.random()
            <chance
        )

        self.phase="capture"

        self.capture_anim={
            "t":0.0,
            "success":success,
            "shakes":0,
        }

        self.message=(
            "Lanci una Sfera Selva!"
        )

    # ========================================================
    # FUGA
    # ========================================================

    def run(self):

        if (
            self.phase!="input"
            or
            self.must_switch
        ):
            return

        if not self.wild:
            self.message=(
                "Non puoi fuggire "
                "da un allenatore."
            )
            return

        self.run_attempts+=1

        chance=min(
            1,
            .65
            +
            .18
            *
            (
                self.run_attempts-1
            ),
        )

        if self.rng.random()<chance:

            self.game.finish_battle(
                "Fuga riuscita."
            )

        else:

            self.message=(
                "Fuga fallita!"
            )

            self.phase="delay"

            self.delay=.3

            self.pending_enemy=True

    # ========================================================
    # CAMBIO CREATURE
    # ========================================================

    def switch(
        self,
        index,
    ):

        if not (
            0<=index<len(self.game.team)
        ):
            return False

        if (
            index==self.game.active
            or
            self.game.team[index].hp<=0
        ):
            return False

        forced=self.must_switch

        self.game.active=index

        self.must_switch=False

        self.display_hero_hp=float(
            self.game.hero.hp
        )

        self.message=(
            f"Vai, {self.game.hero.name}!"
        )

        if forced:
            self.phase="input"

        else:
            self.phase="delay"
            self.delay=.3
            self.pending_enemy=True

        return True

    # ========================================================
    # KO
    # ========================================================

    def _resolve_ko(self):

        # Nemico KO

        if self.enemy.hp<=0:

            defeated=self.enemy

            reward=(
                14
                +
                defeated.level*5
            )

            for i,c in enumerate(
                self.game.team
            ):

                if c.hp>0:
                    c.gain_xp(
                        reward
                        if
                        i==self.game.active
                        else
                        max(
                            1,
                            reward//2,
                        )
                    )

            self.game.coins+=(
                8
                +
                defeated.level
            )

            if (
                self.index+1
                <
                len(self.enemies)
            ):

                self.index+=1

                self.enemy_heals=0

                self.display_enemy_hp=float(
                    self.enemy.hp
                )

                self.message=(
                    f"Entra {self.enemy.name}, "
                    f"Lv.{self.enemy.level}!"
                )

                self.phase="delay"

                self.delay=.7

                self.pending_enemy=False

                return True

            trainer=self.trainer_index

            if trainer is not None:

                self.game.defeated.add(
                    trainer
                )

                self.game.coins+=(
                    TRAINERS[
                        trainer
                    ]["reward"]
                )

                self.game.potions+=2

                self.game.balls+=2

                if trainer==2:

                    self.game.completed=True

                    self.game.finish_battle(
                        "Hai battuto Alba!",
                        ending=True,
                    )

                    return True

                self.game.finish_battle(
                    "Medaglia ottenuta!"
                )

                return True

            self.game.finish_battle(
                "Vittoria! "
                "La squadra guadagna esperienza."
            )

            return True

        # Giocatore KO

        if self.game.hero.hp<=0:

            living=[
                i
                for i,c in enumerate(
                    self.game.team
                )
                if c.hp>0
            ]

            if living:

                self.must_switch=True

                self.phase="input"

                self.message=(
                    "Compagno KO! "
                    "Premi Q e scegline un altro."
                )

            else:

                for c in self.game.team:
                    c.heal_full()

                self.game.active=0

                self.game.coins=max(
                    0,
                    self.game.coins-20,
                )

                self.game.reset_to_spawn()

                self.game.finish_battle(
                    "Squadra KO: "
                    "ritorno al rifugio."
                )

            return True

        return False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self,dt):

        for p in self.particles:
            p.update(dt)

        self.particles[:]=[
            p
            for p in self.particles
            if p.life>0
        ]

        self.flash=max(
            0,
            self.flash-dt,
        )

        self.shake=max(
            0,
            self.shake-dt,
        )

        self.display_enemy_hp+=(
            self.enemy.hp
            -
            self.display_enemy_hp
        )*min(
            1,
            dt*10,
        )

        self.display_hero_hp+=(
            self.game.hero.hp
            -
            self.display_hero_hp
        )*min(
            1,
            dt*10,
        )

        # Cattura

        if self.phase=="capture":

            a=self.capture_anim

            a["t"]+=dt

            if a["t"]>=1.75:

                if a["success"]:

                    caught=self.enemy

                    self.game.team.append(
                        caught
                    )

                    self.game.finish_battle(
                        f"{caught.name} catturato!"
                    )

                else:

                    self.message=(
                        "La sfera si apre! "
                        "Indebolisci ancora la creatura."
                    )

                    self.phase="delay"

                    self.delay=.35

                    self.pending_enemy=True

            return

        # Animazione attacco

        if self.phase=="anim":

            a=self.anim

            a["t"]+=dt

            if (
                not a["applied"]
                and
                a["t"]>=a["impact"]
            ):

                a["applied"]=True

                self._apply_move(
                    a["hero"],
                    a["move"],
                )

            if a["t"]>=a["duration"]:

                hero_turn=a["hero"]

                self.anim=None

                if self._resolve_ko():
                    return

                if hero_turn:

                    self.phase="delay"

                    self.delay=.35

                    self.pending_enemy=True

                else:

                    self.phase="input"

        elif self.phase=="delay":

            self.delay-=dt

            if self.delay<=0:

                if self.pending_enemy:

                    self.pending_enemy=False

                    self._start_move(
                        False,
                        self._enemy_choice(),
                    )

                else:

                    self.phase="input"

    # ========================================================
    # HUD CREATURE
    # ========================================================

    def _status(
        self,
        surface,
        assets,
        creature,
        rect,
        hp_value,
    ):

        r=panel(
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
                r.x+7,
                r.y+6,
            ),
            COLORS["ink"],
            shadow=False,
        )

        text(
            surface,
            assets.font_small,
            f"Lv.{creature.level}",
            (
                r.right-6,
                r.y+7,
            ),
            COLORS["ink"],
            "topright",
            False,
        )

        type_badge(
            surface,
            assets.font_small,
            creature.element,
            (
                r.x+7,
                r.y+19,
                33,
                9,
            ),
        )

        hp_bar(
            surface,
            (
                r.x+44,
                r.y+20,
                r.width-52,
                6,
            ),
            hp_value/creature.max_hp,
        )

        text(
            surface,
            assets.font_small,
            f"{max(0,int(round(hp_value)))}/"
            f"{creature.max_hp}",
            (
                r.right-7,
                r.bottom-4,
            ),
            COLORS["ink"],
            "bottomright",
            False,
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
        # CAMPO BATTAGLIA
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
                    x+8,
                    30
                    +
                    (x%3)*3,
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
                    x+11,
                    22
                    +
                    (x%2)*4,
                ),
                18,
            )

        # Fiume

        pygame.draw.rect(
            surface,
            COLORS["water"],
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

            off=int(
                t*24+y
            )%20

            for x in range(
                -20,
                340,
                40,
            ):

                pygame.draw.line(
                    surface,
                    COLORS["water_light"],
                    (
                        x+off,
                        y,
                    ),
                    (
                        x+off+16,
                        y,
                    ),
                    1,
                )

        # Cascata

        pygame.draw.rect(
            surface,
            (
                88,
                165,
                202,
            ),
            (
                246,
                12,
                42,
                47,
            ),
        )

        for x in (
            251,
            260,
            274,
            283,
        ):

            pygame.draw.line(
                surface,
                (
                    185,
                    225,
                    232,
                ),
                (
                    x,
                    15,
                ),
                (
                    x-3,
                    56,
                ),
                2,
            )

        pygame.draw.rect(
            surface,
            (
                217,
                240,
                239,
            ),
            (
                244,
                55,
                47,
                5,
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

        # Erba foreground

        for x in range(
            0,
            320,
            13,
        ):

            pygame.draw.polygon(
                surface,
                (
                    42,
                    92,
                    61,
                ),
                [
                    (
                        x,
                        119,
                    ),
                    (
                        x+5,
                        101,
                    ),
                    (
                        x+9,
                        119,
                    ),
                ],
            )

            pygame.draw.polygon(
                surface,
                (
                    67,
                    128,
                    70,
                ),
                [
                    (
                        x+6,
                        119,
                    ),
                    (
                        x+10,
                        98,
                    ),
                    (
                        x+14,
                        119,
                    ),
                ],
            )

        hero_off=pygame.Vector2()

        enemy_off=pygame.Vector2()

        if self.anim:

            anim=self.anim

            pulse=math.sin(
                min(
                    1,
                    anim["t"]
                    /
                    anim["duration"],
                )
                *
                math.pi
            )

            offset=pygame.Vector2(
                25*pulse,
                -4*pulse,
            )

            if anim["hero"]:
                hero_off+=offset

            else:
                enemy_off-=offset

        shake=pygame.Vector2()

        if self.shake>0:
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

        enemy_sprite=assets.creature(
            self.enemy.species,
            "front",
            int(t*3)%2,
            2,
        )

        hero_sprite=assets.creature(
            self.game.hero.species,
            "back",
            int(t*3)%2,
            2,
        )

        surface.blit(
            enemy_sprite,
            (
                199
                +
                int(
                    enemy_off.x
                    +
                    shake.x
                ),
                25
                +
                int(
                    enemy_off.y
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
                    hero_off.x
                    +
                    shake.x
                ),
                56
                +
                int(
                    hero_off.y
                    +
                    shake.y
                ),
            ),
        )

        # ====================================================
        # ANIMAZIONE SFERA
        # ====================================================

        if (
            self.phase=="capture"
            and
            self.capture_anim
        ):

            capture_t=self.capture_anim[
                "t"
            ]

            if capture_t<.58:

                p=min(
                    1,
                    capture_t/.58,
                )

                x=(
                    72
                    +
                    (225-72)*p
                )

                y=(
                    88
                    +
                    (56-88)*p
                    -
                    40
                    *
                    math.sin(
                        math.pi*p
                    )
                )

            else:

                p=capture_t-.58

                x=(
                    225
                    +
                    math.sin(
                        p*18
                    )
                    *
                    3
                    *
                    (
                        1
                        if capture_t<1.35
                        else .3
                    )
                )

                y=60

            surface.blit(
                assets.ball(
                    int(t*6)%2
                ),
                (
                    int(x),
                    int(y),
                ),
            )

            if (
                capture_t>.58
                and
                self.capture_anim["success"]
            ):

                fade=min(
                    190,
                    int(
                        (
                            capture_t-.58
                        )
                        *280
                    ),
                )

                overlay=pygame.Surface(
                    (
                        62,
                        62,
                    ),
                    pygame.SRCALPHA,
                )

                overlay.fill(
                    (
                        255,
                        255,
                        255,
                        fade,
                    )
                )

                surface.blit(
                    overlay,
                    (
                        190,
                        34,
                    ),
                )

        # HUD

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

        # Particelle

        for particle in self.particles:

            pygame.draw.circle(
                surface,
                particle.color,
                (
                    int(particle.x),
                    int(particle.y),
                ),
                particle.size,
            )

        # ====================================================
        # UI INFERIORE
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

        # Dialogo

        dialogue(
            surface,
            assets,
            self.message,
            "1-4 mosse",
            rect=(
                4,
                120,
                132,
                56,
            ),
        )

        # Menu

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
        # PULSANTI SEMPRE VISIBILI
        # ====================================================

        if (
            self.phase=="input"
            and
            not self.must_switch
        ):

            bag_label=(
                "B MOSSE"
                if self.menu=="bag"
                else "B ZAINO"
            )

            action_buttons=[
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
                        self.game.balls>0
                        and
                        len(self.game.team)<3
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
                    len(self.game.team)>1,
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
            ) in action_buttons:

                button(
                    surface,
                    assets.font_tiny,
                    rect,
                    label,
                    False,
                    enabled,
                    label.startswith("C "),
                )

            # ------------------------------------------------
            # MOSSE
            # ------------------------------------------------

            if self.menu=="moves":

                for i,move in enumerate(
                    self.game.hero.moves
                ):

                    x=(
                        142
                        +
                        (i%2)*85
                    )

                    y=(
                        141
                        +
                        (i//2)*17
                    )

                    pp=self.game.hero.pp[i]

                    name=move["name"]

                    if len(name)>10:
                        name=name[:9]+"."

                    label=(
                        f"{i+1} "
                        f"{name}"
                    )

                    button(
                        surface,
                        assets.font_small,
                        (
                            x,
                            y,
                            82,
                            16,
                        ),
                        label,
                        False,
                        pp>0,
                        i==1,
                    )

            # ------------------------------------------------
            # ZAINO
            # ------------------------------------------------

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
                    f"1 SFERA x"
                    f"{self.game.balls}",
                    False,
                    (
                        self.wild
                        and
                        self.game.balls>0
                        and
                        len(self.game.team)<3
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
                    f"2 POZIONE x"
                    f"{self.game.potions}",
                    False,
                    self.game.potions>0,
                    False,
                )

        # Cambio obbligatorio

        elif self.must_switch:

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

        # Attesa

        elif self.phase in (
            "anim",
            "delay",
            "capture",
        ):

            text(
                surface,
                assets.font_small,
                "Attendi...",
                (
                    227,
                    150,
                ),
                COLORS["ink"],
                "center",
                False,
            )

        # Flash impatto

        if self.flash>0:

            overlay=pygame.Surface(
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