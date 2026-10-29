from __future__ import annotations
from dataclasses import dataclass, field
from data import SPECIES, MOVESETS
from settings import MAX_LEVEL

@dataclass
class Creature:
    species: str
    level: int = 5
    xp: int = 0
    hp: int = -1
    pp: list[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.pp:
            self.pp = [m["pp"] for m in self.moves]
        if self.hp < 0:
            self.hp = self.max_hp

    @property
    def info(self):
        return SPECIES[self.species]

    @property
    def name(self):
        return self.info["name"]

    @property
    def element(self):
        return self.info["type"]

    @property
    def max_hp(self):
        return self.info["hp"] + self.level * 5

    @property
    def attack(self):
        return self.info["atk"] + self.level * 2

    @property
    def defense(self):
        return self.info["def"] + self.level * 2

    @property
    def speed(self):
        return self.info["spd"] + self.level * 2

    @property
    def moves(self):
        return MOVESETS[self.element]

    @property
    def xp_needed(self):
        return 14 + self.level * 5

    def heal_full(self):
        self.hp = self.max_hp
        self.pp = [m["pp"] for m in self.moves]

    def gain_xp(self, amount: int) -> bool:
        if self.level >= MAX_LEVEL:
            return False
        leveled = False
        self.xp += amount
        while self.level < MAX_LEVEL and self.xp >= self.xp_needed:
            need = self.xp_needed
            self.xp -= need
            self.level += 1
            self.hp = min(self.max_hp, self.hp + 8)
            leveled = True
        if self.level >= MAX_LEVEL:
            self.xp = 0
        return leveled

    def serialize(self):
        return {
            "species": self.species,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "pp": list(self.pp),
        }

    @classmethod
    def deserialize(cls, data):
        c = cls(
            str(data["species"]), int(data["level"]), int(data.get("xp", 0)),
            int(data.get("hp", -1)), list(data.get("pp", []))
        )
        c.hp = max(0, min(c.max_hp, c.hp))
        return c

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]
    size: int = 2
    gravity: float = 0.0

    def update(self, dt: float):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt

@dataclass
class NPC:
    kind: str
    x: int
    y: int
    facing: str = "down"
    trainer_index: int | None = None
