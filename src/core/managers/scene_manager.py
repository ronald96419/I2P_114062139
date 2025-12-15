import pygame as pg

from src.scenes.scene import Scene
from src.utils import Logger
from src.utils import GameSettings

class SceneManager:
    
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None
    
    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}

        self.setting_mode = False
        self.mute_mode = False
        self.bag_mode = False
        self.file_mode = False
        self.trading_mode = False
        self.battle_loading = False
        self.loading_number = 0
        self.battle_mode = False
        self.bush_battle = False
        
    
    def change_setting(self):
        if self.setting_mode:
            self.setting_mode = False
        else:
            self.setting_mode = True
    def change_mute(self):
        if self.mute_mode:
            self.mute_mode = False
        else:
            self.mute_mode = True
    def change_bag(self):
        if self.bag_mode:
            self.bag_mode = False
        else:
            self._scenes["game"].game_manager.bag.page = 0
            self.bag_mode = True
    def change_file(self,mode):
        self.file_mode = mode
        self.change_setting()
    def change_battle_loading(self):
        if self.battle_loading:
            self.battle_loading = False
        else:
            self.battle_loading = True
    def change_battle(self):
        if self.battle_mode:
            self.battle_mode = False
        else:
            self.battle_mode = True
    def change_bush_battle(self):
        if self.bush_battle:
            self.bush_battle = False
        else:
            self.bush_battle = True
    def change_trading(self):
        self.trading_mode = not self.trading_mode
        
    def register_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene
        
    def change_scene(self, scene_name: str) -> None:
        if scene_name in self._scenes:
            Logger.info(f"Changing scene to '{scene_name}'")
            self._next_scene = scene_name
        else:
            raise ValueError(f"Scene '{scene_name}' not found")
            
    def update(self, dt: float) -> None:
        # Handle scene transition
        if self._next_scene is not None:
            self._perform_scene_switch()
            
        # Update current scene
        if self._current_scene:
            self._current_scene.update(dt)
            
    def draw(self, screen: pg.Surface) -> None:
        if self._current_scene:
            self._current_scene.draw(screen)
            
    def _perform_scene_switch(self) -> None:
        if self._next_scene is None:
            return
            
        # Exit current scene
        if self._current_scene:
            self._current_scene.exit()
        
        self._current_scene = self._scenes[self._next_scene]
        
        # Enter new scene
        if self._current_scene:
            Logger.info(f"Entering {self._next_scene} scene")
            self._current_scene.enter()
            
        # Clear the transition request
        self._next_scene = None
        