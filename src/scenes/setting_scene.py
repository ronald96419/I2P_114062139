'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
import pygame as pg
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components.button import Button, Slide_Button, OnOff_Button, Picture
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
from typing import override



class SettingScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    flat_button: Button


    

    def __init__(self):
        super().__init__()
        
        self.background = BackgroundSprite("backgrounds/background1.png")
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.volume_location = 775-(325-GameSettings.AUDIO_VOLUME*325)

        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px+250, py+150, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )
        self.flat_button = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            px-400, py-300, 800, 600,
        )
        self.bar_button = Slide_Button(
            "UI/raw/UI_Flat_Bar06a.png", "UI/raw/UI_Flat_Bar06a.png",
            px-200, py-100, 400, 50,
            lambda: self.set_volume()
        )
        self.volume_button = Picture(
            "UI/raw/UI_Flat_IconPoint01b.png",
            self.volume_location, py-100, 50, 50,
        )
        self.mute_button = OnOff_Button(
            "UI/raw/UI_Flat_Bar05a.png", "UI/raw/UI_Flat_Bar06a.png",
            px-200, py-50, 50, 50,
            lambda: self.mute()
        )

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

    @override
    def enter(self) -> None:
        self.volume_location = 775-(325-GameSettings.AUDIO_VOLUME*325)
        self.volume_button = Picture(
            "UI/raw/UI_Flat_IconPoint01b.png",
            self.volume_location, GameSettings.SCREEN_HEIGHT // 2-100, 50, 50
        )
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("menu")
            return
        self.back_button.update(dt)
        self.bar_button.update(dt)
        self.volume_button.update(dt)
        self.mute_button.update(dt)


    @override
    def draw(self, screen: pg.Surface) -> None:

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        self.background.draw(screen)

        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 128))
        screen.blit(dark_overlay,(0,0))

        self.flat_button.draw(screen)
        self.bar_button.draw(screen)
        self.back_button.draw(screen)
        self.mute_button.draw(screen)
        self.volume_button.draw(screen)
        
        font_setting = resource_manager.get_font("Minecraft.ttf", 48)
        text_setting = font_setting.render("SETTINGS",True,(255,255,255))
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

        
        