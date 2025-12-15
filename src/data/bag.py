import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.interface.components.button import Button, Slide_Button, OnOff_Button, Picture
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager

import math

class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

        self.page = 0
        self.max_show = 5
        #buttons
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.flat_button = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            px-400, py-300, 800, 600,
        )
        self.bag_x_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            px+325, py-275, 50, 50,
            lambda: scene_manager.change_bag()
        )
        self.page_left_button = Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px-325, py+225, 50, 50,
            lambda: self.change_page("left")
        )
        self.page_right_button = Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px-175, py+225, 50, 50,
            lambda: self.change_page("right")
        )
        font_ui = resource_manager.get_font("Minecraft.ttf", 40)
        self.text_left = font_ui.render("<-",True,(0,0,0))
        self.text_right = font_ui.render("->",True,(0,0,0))

    def change_page(self,text:str):
        if text == "left":
            if self.page > 0:
                self.page -= 1
        elif text == "right":
            if self.page < math.ceil(len(self._monsters_data)/self.max_show)-1:
                self.page += 1

    def update(self, dt: float):
        if scene_manager.bag_mode:
            self.bag_x_button.update(dt)
            self.page_left_button.update(dt)
            self.page_right_button.update(dt)
        pass

    def draw(self, screen: pg.Surface):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 128))
        screen.blit(dark_overlay,(0,0))

        self.flat_button.draw(screen)
        self.bag_x_button.draw(screen)
        self.page_left_button.draw(screen)
        self.page_right_button.draw(screen)
        screen.blit(self.text_left,(px-325, py+225))
        screen.blit(self.text_right,(px-175, py+225))

        font_title = resource_manager.get_font("Minecraft.ttf", 48)
        text_bag = font_title.render("SETTINGS",True,(0,0,0))
        screen.blit(text_bag,(px-350,py-250))

        font_page = resource_manager.get_font("Minecraft.ttf", 48)
        text_bag = font_page.render(f"{self.page+1}/{math.ceil(len(self._monsters_data)/self.max_show)}",True,(0,0,0))
        screen.blit(text_bag,(px-260,py+225))
        
        font_items = resource_manager.get_font("Minecraft.ttf", 20)
        font_amount = resource_manager.get_font("Minecraft.ttf", 16)
        for i in range(len(self._items_data)):
            picture = Picture(
                self._items_data[i]["sprite_path"],
                px, py-200+75*i, 50, 50,
            )
            picture.draw(screen)

            text_name = font_items.render(f"{self._items_data[i]["name"]}:",True,(0,0,0))
            screen.blit(text_name,(px+100,py-175+75*i))

            text_amount = font_amount.render(f"X{self._items_data[i]["count"]}",True,(0,0,0))
            screen.blit(text_amount,(px+250,py-175+75*i))

        
        font_monster = resource_manager.get_font("Minecraft.ttf", 16)
        font_ui = resource_manager.get_font("Minecraft.ttf", 10)
        for i in range(len(self._monsters_data[self.page*self.max_show:(self.page+1)*self.max_show])):
            monster_background = Picture(
                "UI/raw/UI_Flat_Banner03a.png",
                px-350, py-200+75*i, 300, 75,
            )
            monster_background.draw(screen)
            picture = Picture(
                self._monsters_data[i+self.page*self.max_show]["sprite_path"],
                px-340, py-190+75*i, 50, 50,
            )
            picture.draw(screen)

            block_max_hp = pg.Surface((100,10))
            block_max_hp.fill((255, 0, 0))
            screen.blit(block_max_hp,(px-290,py-170+75*i))

            block_hp = pg.Surface((100*(self._monsters_data[i+self.page*self.max_show]["hp"]/self._monsters_data[i+self.page*self.max_show]["max_hp"]),10))
            block_hp.fill((0, 255, 0))
            screen.blit(block_hp,(px-290,py-170+75*i))

            text_name = font_monster.render(f"{self._monsters_data[i+self.page*self.max_show]["name"]}",True,(0,0,0))
            screen.blit(text_name,(px-290,py-190+75*i))

            text_lv = font_monster.render(f"Lv{self._monsters_data[i+self.page*self.max_show]["level"]}",True,(0,0,0))
            screen.blit(text_lv,(px-125,py-185+75*i))

            text_hp = font_ui.render(f"{self._monsters_data[i+self.page*self.max_show]["hp"]}/",True,(0,0,0))
            screen.blit(text_hp,(px-290,py-160+75*i))

            text_max_hp = font_ui.render(f"{self._monsters_data[i+self.page*self.max_show]["max_hp"]}",True,(0,0,0))
            screen.blit(text_max_hp,(px-265,py-160+75*i))

            text_element = font_ui.render(f"element:{self._monsters_data[i+self.page*self.max_show]["element"]}",True,(0,0,0))
            screen.blit(text_element,(px-200,py-160+75*i))
        pass

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag