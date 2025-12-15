from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, PositionCamera, Direction, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance
        

        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= ...
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += ...
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= ...
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += ...
        
        self.position = ...
        '''
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            self.direction = Direction.LEFT
            if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
                dis.x -= self.speed*dt / (2**(1/2))
            elif input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
                dis.x -= self.speed*dt / (2**(1/2))
            else:
                dis.x -= self.speed*dt
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            self.direction = Direction.RIGHT
            if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
                dis.x += self.speed*dt / (2**(1/2))
            elif input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
                dis.x += self.speed*dt / (2**(1/2))
            else:
                dis.x += self.speed*dt
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            self.direction = Direction.UP
            if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
                dis.y -= self.speed*dt / (2**(1/2))
            elif input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
                dis.y -= self.speed*dt / (2**(1/2))
            else:
                dis.y -= self.speed*dt
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            self.direction = Direction.DOWN
            if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
                dis.y += self.speed*dt / (2**(1/2))
            elif input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
                dis.y += self.speed*dt / (2**(1/2))
            else:
                dis.y += self.speed*dt
        
        if self.direction == Direction.RIGHT:
            self.animation.switch("right")
        elif self.direction == Direction.LEFT:
            self.animation.switch("left")
        elif self.direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")

        if not scene_manager.setting_mode and not scene_manager.bag_mode and not scene_manager.file_mode and not scene_manager.battle_loading and not scene_manager.trading_mode:
            check = pg.Rect(self.position.x+dis.x,self.position.y,GameSettings.TILE_SIZE,GameSettings.TILE_SIZE)
            if self.game_manager.check_collision(check):
                self.position.x = Entity._snap_to_grid(self.position.x)
            else:
                self.position.x += dis.x
            check = pg.Rect(self.position.x,self.position.y+dis.y,GameSettings.TILE_SIZE,GameSettings.TILE_SIZE)
            if self.game_manager.check_collision(check):
                self.position.y = Entity._snap_to_grid(self.position.y)
            else:
                self.position.y += dis.y
        player_rect = pg.Rect(self.position.x,self.position.y,GameSettings.TILE_SIZE,GameSettings.TILE_SIZE)
        if self.game_manager.check_bush_collision(player_rect) and input_manager.key_pressed(pg.K_SPACE):
            if not scene_manager.battle_loading:
                scene_manager.change_battle_loading()
                scene_manager.change_bush_battle()
                scene_manager.loading_number = 255
        

        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            dest = tp.destination
            self.game_manager.switch_map(dest)
                
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

