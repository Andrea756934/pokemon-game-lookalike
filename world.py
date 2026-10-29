from __future__ import annotations
import random
import pygame
from settings import TILE, BASE_W, BASE_H
from models import NPC, Particle
from data import TRAINERS

class World:
    def __init__(self, seed=72):
        self.rng = random.Random(seed)
        self.w, self.h = 40, 28
        self.grid = [["." for _ in range(self.w)] for _ in range(self.h)]
        self.npcs: list[NPC] = []
        self.chests = {"chest0": (9, 15), "chest1": (4, 8), "chest2": (31, 22), "chest3": (25, 9)}
        self.spawn = (7.5 * TILE, 23.5 * TILE)
        self.build()

    def build(self):
        g = self.grid
        for y in range(self.h):
            for x in range(self.w):
                if x < 2 or y < 2 or x >= self.w - 2 or y >= self.h - 2:
                    g[y][x] = "#"
        # river
        for y in range(2, self.h - 2):
            for x in (20, 21):
                g[y][x] = "~"
        # tall grass zones
        for y in range(4, 15):
            for x in range(3, 18):
                if self.rng.random() < .72:
                    g[y][x] = ","
        for y in range(10, 25):
            for x in range(24, 37):
                if self.rng.random() < .72:
                    g[y][x] = ","
        # forest masses
        blocks = [(3,3,3,4),(10,3,5,2),(15,9,3,5),(3,13,2,4),(25,3,2,3),(34,11,3,5),(24,22,3,3),(10,24,5,2)]
        for ax, ay, bw, bh in blocks:
            for y in range(ay, ay+bh):
                for x in range(ax, ax+bw):
                    g[y][x] = "#"
        # stone/cliff accents
        for x, y in [(17,6),(18,6),(18,7),(28,10),(29,10),(32,13),(7,18),(8,18),(34,21),(15,20)]:
            if g[y][x] == ".": g[y][x] = "r"
        for x, y in [(6,5),(7,5),(8,5),(6,6),(8,6),(6,7),(7,7),(8,7)]:
            g[y][x] = "a"
        # routes
        self._path((6,23),(16,23)); self._path((16,23),(16,18)); self._path((16,18),(31,18)); self._path((31,18),(31,5))
        self._path((7,23),(7,13)); self._path((7,13),(13,13)); self._path((13,13),(13,7)); self._path((13,7),(31,7))
        self._path((5,20),(5,23)); self._path((10,21),(10,23))
        # bridges
        for y in (8,19):
            for x in range(19,23):
                g[y][x] = "=" if x in (20,21) else ":"
        # house footprint
        for y in range(17,20):
            for x in range(3,8):
                g[y][x] = "h"
        # flowers
        for _ in range(85):
            x = self.rng.randrange(2,self.w-2); y = self.rng.randrange(2,self.h-2)
            if g[y][x] == "." and self.rng.random() < .75:
                g[y][x] = "f"
        # NPCs
        self.npcs = [NPC("clinic",5,20), NPC("guide",10,21)]
        for i, t in enumerate(TRAINERS):
            x,y = t["pos"]
            self.npcs.append(NPC(t["sprite"],x,y,t.get("facing","down"),i))

    def _path(self, a, b):
        x,y = a
        while True:
            self.grid[y][x] = "=" if x in (20,21) else ":"
            if (x,y) == b: break
            if x != b[0]: x += 1 if b[0] > x else -1
            else: y += 1 if b[1] > y else -1

    def tile(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return "#"

    def solid(self, x, y):
        return self.tile(x,y) in ("#","~","h","r")

    def entity_at(self, tx, ty):
        for n in self.npcs:
            if (n.x,n.y) == (tx,ty): return n
        for name, pos in self.chests.items():
            if pos == (tx,ty): return name
        return None

    def collide_rect(self, rect: pygame.Rect):
        left, right = rect.left // TILE, (rect.right-1)//TILE
        top, bottom = rect.top // TILE, (rect.bottom-1)//TILE
        for ty in range(top,bottom+1):
            for tx in range(left,right+1):
                if self.solid(tx,ty) or self.entity_at(tx,ty) is not None:
                    return True
        return False

    def draw(self, surface, assets, camera, opened_chests, t):
        cx, cy = int(camera.x), int(camera.y)
        sx=max(0,cx//TILE-1); ex=min(self.w,(cx+BASE_W)//TILE+2)
        sy=max(0,cy//TILE-1); ey=min(self.h,(cy+BASE_H)//TILE+2)
        frame=int(t*4)%4
        for y in range(sy,ey):
            for x in range(sx,ex):
                kind=self.tile(x,y)
                surface.blit(assets.tile(kind, frame if kind in (",","~") else 0, (x+y)&1),(x*TILE-cx,y*TILE-cy))
        # house: intentionally layered and more detailed than a single tile.
        hx,hy=3*TILE-cx,16*TILE-cy
        pygame.draw.rect(surface,(202,178,132),(hx+4,hy+18,76,34))
        pygame.draw.rect(surface,(235,219,181),(hx+8,hy+20,68,30))
        pygame.draw.polygon(surface,(126,66,54),[(hx,hy+20),(hx+10,hy+4),(hx+70,hy+4),(hx+84,hy+20)])
        pygame.draw.polygon(surface,(173,84,62),[(hx+5,hy+18),(hx+13,hy+7),(hx+69,hy+7),(hx+79,hy+18)])
        pygame.draw.rect(surface,(51,57,57),(hx+35,hy+30,13,20))
        pygame.draw.rect(surface,(83,127,145),(hx+15,hy+28,11,9)); pygame.draw.rect(surface,(83,127,145),(hx+57,hy+28,11,9))
        pygame.draw.rect(surface,(244,239,208),(hx+39,hy+10,5,14)); pygame.draw.rect(surface,(244,239,208),(hx+34,hy+14,15,5))
        # altar monument
        ax,ay=6*TILE-cx,4*TILE-cy
        pygame.draw.rect(surface,(111,119,111),(ax+3,ay+11,40,29))
        pygame.draw.rect(surface,(169,174,153),(ax+7,ay+8,32,29))
        pygame.draw.rect(surface,(202,203,177),(ax+10,ay+11,26,22))
        pygame.draw.polygon(surface,(101,143,86),[(ax+18,ay+27),(ax+14,ay+20),(ax+20,ay+23),(ax+24,ay+15),(ax+25,ay+27)])
        # chests
        for name,(tx,ty) in self.chests.items():
            x,y=tx*TILE-cx,ty*TILE-cy
            if name not in opened_chests:
                pygame.draw.rect(surface,(78,55,42),(x+2,y+5,12,9))
                pygame.draw.rect(surface,(171,117,62),(x+3,y+4,10,8))
                pygame.draw.rect(surface,(229,190,91),(x+7,y+8,2,3))

    def draw_entities(self, surface, assets, camera, t, player_y=None):
        cx,cy=int(camera.x),int(camera.y)
        for n in sorted(self.npcs, key=lambda q:q.y):
            x,y=n.x*TILE-cx,n.y*TILE-cy
            sprite=assets.npc(n.kind,n.facing,int(t*2)%2)
            surface.blit(sprite,(x,y-8))
