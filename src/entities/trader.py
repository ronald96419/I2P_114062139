from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite, Animation
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera

import random
from src.utils.definition import Monster
from src.data.trading_overlay import Trading_Overlay


class TraderClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, enemy: "Trader", dt: float) -> None:
        return

class Trader(Entity):
    classification: TraderClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction
    detect_rect: pygame.Rect

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: TraderClassification = TraderClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
    ) -> None:
        super().__init__(x, y, game_manager)
        self.classification = classification
        self.max_tiles = max_tiles
        if classification == TraderClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False
        self.animation = Animation(
            "character/ow2.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        

        monster_names = ["Pikachu","Charizard","Blastoise","Venusaur","Gengar","Dragonite","no_name_7","no_name_8","no_name_9","no_name_10","no_name_11","no_name_12","no_name_13","no_name_14","no_name_15","no_name_16"]
        self.monster_names = random.sample(monster_names,5)
        self.monsters = []
        self.items = []
        for i in self.monster_names:
            if monster_names.index(i) in [0,1,2,6,7,8]:
                monster_element = "fire"
            elif monster_names.index(i) in [5,10,11,12,13]:
                monster_element = "water"
            elif monster_names.index(i) in [3,4,9,14,15]:
                monster_element = "grass"
            monster_level = int(1+50*random.random())
            monster_data = {
                "name":i,
                "hp":monster_level*10,
                "max_hp":monster_level*10,
                "level":monster_level,
                "sprite_path":f"menu_sprites/menusprite{1+monster_names.index(i)}.png",
                "element":monster_element
                }
            self.monsters.append(Monster(monster_data))
        item_names = ["Potion","PowerPotion","DefendPotion","Pokeball"]
        for i in item_names:
            if "Potion" in i:
                item_data = {
                    "name":i,
                    "count":5,
                    "sprite_path":"ingame_ui/potion.png"
                }
            elif i == "Pokeball":
                item_data = {
                    "name":i,
                    "count":5,
                    "sprite_path":"ingame_ui/ball.png"
                }
            self.items.append(item_data)
        

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        self.animation.update_pos(self.position)
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            if not scene_manager.battle_loading and not scene_manager.trading_mode:
                scene_manager.trading_overflow = Trading_Overlay(self.monsters,self.items)
                scene_manager.change_trading()

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)
                       

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        '''
        TODO: Create hitbox to detect line of sight of the enemies towards the player
        '''
        (x,y) = (self.position.x,self.position.y)
        unit = GameSettings.TILE_SIZE
        if self.los_direction == Direction.RIGHT:
            self.detect_rect = pygame.Rect(x+unit,y,3*unit,unit)
        elif self.los_direction == Direction.LEFT:
            self.detect_rect = pygame.Rect(x-3*unit,y,3*unit,unit)
        elif self.los_direction == Direction.DOWN:
            self.detect_rect = pygame.Rect(x,y+unit,unit,3*unit)
        else:
            self.detect_rect = pygame.Rect(x,y-3*unit,unit,3*unit)
        return self.detect_rect

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return
        '''
        TODO: Implement line of sight detection
        If it's detected, set self.detected to True
        '''
        check_player = pygame.Rect(player.position.x,player.position.y,GameSettings.TILE_SIZE,GameSettings.TILE_SIZE)
        check_self = self._get_los_rect()
        if check_self.colliderect(check_player):
            self.detected = True
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "Trader":
        classification = TraderClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == TraderClassification.STATIONARY:
            facing = Direction.DOWN
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base