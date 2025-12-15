import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, resource_manager
from src.sprites import Sprite, Animation
from typing import override

from src.interface.components.button import Button, Slide_Button, OnOff_Button, Picture
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils.definition import Monster
import json, random

from src.utils import Position, PositionCamera, Direction

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Animation
    
    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Animation(
            "character/ow1.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )

        #default
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.volume_location = 775-(325-GameSettings.AUDIO_VOLUME*325)
        self.current_volume = 0.5
        
        #in game
        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            GameSettings.SCREEN_WIDTH-100, 0, 100, 100,
            lambda: scene_manager.change_setting()
        )
        self.bag_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            GameSettings.SCREEN_WIDTH-250, 0, 100, 100,
            lambda: scene_manager.change_bag()
        )

        #settings
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px+250, py-250, 100, 100,
            lambda: scene_manager.change_setting()
        )
        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            px+125, py-250, 100, 100,
            lambda: scene_manager.change_file("load")
        )
        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            px, py-250, 100, 100,
            lambda: scene_manager.change_file("save")
        )
        self.flat_button = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            px-400, py-300, 800, 600
        )
        self.bar_button = Slide_Button(
            "UI/raw/UI_Flat_Bar06a.png", "UI/raw/UI_Flat_Bar06a.png",
            px-200, py-100, 400, 50,
            lambda: self.set_volume()
        )
        self.volume_button = Picture(
            "UI/raw/UI_Flat_IconPoint01b.png",
            self.volume_location, py-100, 50, 50
        )
        self.mute_button = OnOff_Button(
            "UI/raw/UI_Flat_Bar06a.png", "UI/raw/UI_Flat_Bar05a.png",
            px-200, py-50, 50, 50,
            lambda: self.mute()
        )

        #save/load
        self.file_background = Picture(
            "UI/raw/UI_Flat_InputField02a.png",
            px-400, py-300, 800, 600
        )
        self.file_x_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            px+325, py-275, 50, 50,
            lambda: scene_manager.change_file(False)
        )

        #minimap player
        self.minimap_player_size = 25
        self.minimap_player = pg.image.load("assets/images/ingame_ui/baricon3.png")
        self.minimap_player = pg.transform.scale(self.minimap_player,(self.minimap_player_size,self.minimap_player_size))
        
        

 
    
    def set_volume(self):
        if not scene_manager.mute_mode:
            if input_manager.mouse_pos[0]-25 > 765:
                self.volume_location = 775
            elif input_manager.mouse_pos[0]-25 < 450:
                self.volume_location = 450
            else:
                self.volume_location = input_manager.mouse_pos[0]-25
            self.volume_button = Button(
                "UI/raw/UI_Flat_IconPoint01b.png", "UI/raw/UI_Flat_IconPoint01b.png",
                self.volume_location, GameSettings.SCREEN_HEIGHT // 2-100, 50, 50,
                None
            )
            GameSettings.set_volume((325-(775-self.volume_location))/325)
            sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
        
    def mute(self):
        if scene_manager.mute_mode:
            GameSettings.set_volume(self.current_volume)
            sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
            self.volume_location = 775-(325-GameSettings.AUDIO_VOLUME*325)
            self.volume_button = Button(
                "UI/raw/UI_Flat_IconPoint01b.png", "UI/raw/UI_Flat_IconPoint01b.png",
                self.volume_location, GameSettings.SCREEN_HEIGHT // 2-100, 50, 50,
                None
            )
            scene_manager.change_mute()
        else:
            self.current_volume = GameSettings.AUDIO_VOLUME
            self.volume_location = 450
            self.volume_button = Button(
                "UI/raw/UI_Flat_IconPoint01b.png", "UI/raw/UI_Flat_IconPoint01b.png",
                self.volume_location, GameSettings.SCREEN_HEIGHT // 2-100, 50, 50,
                None
            )
            GameSettings.set_volume((325-(775-self.volume_location))/325)
            sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
            scene_manager.change_mute()

    def draw_file(self,mode,screen: pg.Surface):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        self.file_background.draw(screen)
        self.file_x_button.draw(screen)

        font_title = resource_manager.get_font("Minecraft.ttf", 48)
        text_title = font_title.render(f"{mode}",True,(0,0,0))
        screen.blit(text_title,(px-350,py-250))

        font_text = resource_manager.get_font("Minecraft.ttf", 40)
        font_date = resource_manager.get_font("Minecraft.ttf", 20)
        for i in range(6):
            file_buttom = Button(
                "UI/raw/UI_Flat_FrameSlot03a.png", "UI/raw/UI_Flat_FrameSlot03c.png",
                px-350+(i//3)*350, py-125+150*(i%3), 300, 100,
                lambda: self.edit_file(mode,i)
            )
            file_buttom.update(0)
            file_buttom.draw(screen)
            text_file = font_text.render(f"File {i}",True,(0,0,0))
            screen.blit(text_file,(px-300+(i//3)*350,py-100+150*(i%3)))

            try:
                with open(f"saves/game{i}.json","r") as json_file:
                    data = json.load(json_file)
                    date_list = data["date"]
                    text_date = font_date.render(f"{date_list[0]}/{date_list[1]}/{date_list[2]}",True,(0,0,0))
                    screen.blit(text_date,(px-200+(i//3)*350,py-50+150*(i%3)))
            except:
                text_date = font_date.render("empty",True,(0,0,0))
                screen.blit(text_date,(px-200+(i//3)*350,py-50+150*(i%3)))


    
    def edit_file(self,mode,file):
        if mode == "save":
            self.game_manager.save(f"saves/game{file}.json")
            scene_manager.change_file(False)
        elif mode == "load":
            try:
                self.game_manager = GameManager.load(f"saves/game{file}.json")
                scene_manager.change_scene("game")
                scene_manager.change_file(False)
                scene_manager.change_setting()
            except:
                pass

    def check_alive(self,monster:Monster):
        return monster["hp"] > 0
    
    def check_player_monsters_alive(self):
        return any(self.check_alive(i) for i in self.game_manager.bag._monsters_data)

    def create_bush_monster(self):
        monster_names = ["Pikachu","Charizard","Blastoise","Venusaur","Gengar","Dragonite","no_name_7","no_name_8","no_name_9","no_name_10","no_name_11","no_name_12","no_name_13","no_name_14","no_name_15","no_name_16"]
        monster_choose = min(len(monster_names)-1,int(len(monster_names)*random.random()))
        monster_level = int(1+50*random.random())
        if monster_choose in [0,1,2,6,7,8]:
            monster_element = "fire"
        elif monster_choose in [5,10,11,12,13]:
            monster_element = "water"
        elif monster_choose in [3,4,9,14,15]:
            monster_element = "grass"
        monster_data = {
            "name":monster_names[monster_choose],
            "hp":monster_level*10,
            "max_hp":monster_level*10,
            "level":monster_level,
            "sprite_path":f"menu_sprites/menusprite{1+monster_choose}.png",
            "element":monster_element
            }
        monster = Monster(monster_data)
        return monster
        

    @override
    def enter(self) -> None:
        self.volume_location = 775-(325-GameSettings.AUDIO_VOLUME*325)
        self.volume_button = Picture(
            "UI/raw/UI_Flat_IconPoint01b.png",
            self.volume_location, GameSettings.SCREEN_HEIGHT // 2-100, 50, 50
        )
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        for trader in self.game_manager.current_traders:
            trader.update(dt)
            
        # Update others
        if not scene_manager.bag_mode:
            self.bag_button.update(dt)
        if scene_manager.setting_mode:
            self.back_button.update(dt)
            self.volume_button.update(dt)
            self.bar_button.update(dt)
            self.mute_button.update(dt)
            self.save_button.update(dt)
            self.load_button.update(dt)
        else:
            self.setting_button.update(dt)
        if scene_manager.file_mode:
            self.file_x_button.update(dt)
        if scene_manager.trading_mode:
            scene_manager.trading_overflow.update(dt)
        self.game_manager.bag.update(dt)
        
        
        if self.game_manager.player is not None and self.online_manager is not None:
            if self.game_manager.player.direction == Direction.DOWN:
                direction = "down"
            elif self.game_manager.player.direction == Direction.UP:
                direction = "up"
            elif self.game_manager.player.direction == Direction.LEFT:
                direction = "left"
            elif self.game_manager.player.direction == Direction.RIGHT:
                direction = "right"
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                direction
            )
        self.game_manager.current_map.spawn = self.game_manager.player.position
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py
            
            camera = self.game_manager.player.camera
            '''
            
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
            
            screen.blit(self.minimap_player,((self.game_manager.player.position.x/GameSettings.TILE_SIZE)*self.game_manager.current_map.minitile_size[0]-(self.minimap_player_size-self.game_manager.current_map.minitile_size[0])/2,(self.game_manager.player.position.y/GameSettings.TILE_SIZE)*self.game_manager.current_map.minitile_size[1]-(self.minimap_player_size-self.game_manager.current_map.minitile_size[1])/2))
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        for trader in self.game_manager.current_traders:
            trader.draw(screen, camera)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.switch(player["direction"])
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
                    print(f"self:{self.game_manager.player.position}")
                    print(f"other:{pos}")
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        if scene_manager.setting_mode:
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 128))
            screen.blit(dark_overlay,(0,0))
            self.flat_button.draw(screen)
            self.bar_button.draw(screen)
            self.back_button.draw(screen)
            self.mute_button.draw(screen)
            self.volume_button.draw(screen)
            self.save_button.draw(screen)
            self.load_button.draw(screen)

            font_title = resource_manager.get_font("Minecraft.ttf", 48)
            text_setting = font_title.render("SETTINGS",True,(255,255,255))
            screen.blit(text_setting,(px-350,py-250))

            font_volume_mute = resource_manager.get_font("Minecraft.ttf", 24)
            text_voulme = font_volume_mute.render(f"Volume: {round(GameSettings.AUDIO_VOLUME*100)}%", True, (255,255,255))
            screen.blit(text_voulme,(px-350,py-80))

            if scene_manager.mute_mode:
                mute = "ON"
            else:
                mute = "OFF"
            text_mute = font_volume_mute.render(f"Mute: {mute}", True, (255,255,255))
            screen.blit(text_mute,(px-350,py-30))
        elif scene_manager.bag_mode:
            self.game_manager.bag.draw(screen)
        elif scene_manager.file_mode:
            self.draw_file(scene_manager.file_mode,screen)
        elif scene_manager.battle_loading:
            if self.check_player_monsters_alive():
                dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
                dark_overlay.fill((0, 0, 0, min(255,255-scene_manager.loading_number)))
                screen.blit(dark_overlay,(0,0))
                scene_manager.loading_number -= 5
                if scene_manager.loading_number <= 0:
                    scene_manager.loading_number = 255
                    scene_manager.change_battle_loading()
                    scene_manager.change_battle()
            else:
                scene_manager.change_battle_loading()
        elif scene_manager.battle_mode:
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
            dark_overlay.fill((0, 0, 0))
            screen.blit(dark_overlay,(0,0))
            if scene_manager.bush_battle:
                scene_manager._scenes["battle"].opponent_monster = self.create_bush_monster()
                scene_manager.change_scene("battle")
        elif scene_manager.trading_mode:
            scene_manager.trading_overflow.draw(screen)
        else:
            self.setting_button.draw(screen)
            self.bag_button.draw(screen)
