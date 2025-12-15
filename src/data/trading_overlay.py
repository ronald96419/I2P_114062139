import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.interface.components.button import Button, Slide_Button, OnOff_Button, Picture
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager

class Trading_Overlay:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

        self.player_item_list_index = {}
        for i in range(len(scene_manager._scenes["game"].game_manager.bag._items_data)):
            self.player_item_list_index[scene_manager._scenes["game"].game_manager.bag._items_data[i]["name"]] = i
        self.show = "monster"
        self.mode = "buy"
        self.sold_monster = []
        self.player_sold_monster = []
        self.player_sold_monster_delete_list = []

        #buttons
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.flat_picture = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            px-400, py-300, 800, 600,
        )
        self.shop_x_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            px+325, py-275, 50, 50,
            lambda: self.exit_shop()
        )
        self.show_monster_button = Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px, py+225, 100, 50,
            lambda: self.change_page("monster")
        )
        self.show_item_button = Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px+100, py+225, 100, 50,
            lambda: self.change_page("item")
        )
        self.buy_buttom= Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px-350, py-275, 200, 75,
            lambda: self.change_mode("buy")
        )
        self.sell_button = Button(
            "UI/raw/UI_Flat_Button01a_4.png", "UI/raw/UI_Flat_Button01a_1.png",
            px-150, py-275, 200, 75,
            lambda: self.change_mode("sell")
        )
        self.coin_picture = Picture(
            "ingame_ui/coin.png",
            px, py+100, 50, 50,
        )

        font_ui = resource_manager.get_font("Minecraft.ttf", 10)
        
        self.monster_text = font_ui.render("Monsters",True,(0,0,0))
        self.item_text = font_ui.render("Items",True,(0,0,0))
        self.special_text = None
        self.special_text_number = 0
        
    def change_page(self,text:str):
        self.show = text
    def change_mode(self,text:str):
        self.mode = text
        if self.player_sold_monster_delete_list:
            for i in self.player_sold_monster_delete_list:
                scene_manager._scenes["game"].game_manager.bag._monsters_data.pop(i)
            self.player_sold_monster_delete_list = []
            self.player_sold_monster = []
    def exit_shop(self):
        if self.player_sold_monster_delete_list:
            for i in self.player_sold_monster_delete_list:
                scene_manager._scenes["game"].game_manager.bag._monsters_data.pop(i)
            self.player_sold_monster_delete_list = []
            self.player_sold_monster = []
        scene_manager.change_trading()

    def show_monster(self,screen):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        font_monster = resource_manager.get_font("Minecraft.ttf", 16)
        font_ui = resource_manager.get_font("Minecraft.ttf", 10)
        font_amount = resource_manager.get_font("Minecraft.ttf", 16)
        if self.mode == "buy":
            for i in range(len(self._monsters_data)):
                monster_background = Picture(
                    "UI/raw/UI_Flat_Banner03a.png",
                    px-350, py-200+75*i, 300, 75,
                )
                picture = Picture(
                    self._monsters_data[i]["sprite_path"],
                    px-340, py-190+75*i, 50, 50,
                )

                text_name = font_monster.render(f"{self._monsters_data[i]["name"]}",True,(0,0,0))
                text_name_place = (px-290,py-190+75*i)

                text_lv = font_monster.render(f"Lv{self._monsters_data[i]["level"]}",True,(0,0,0))
                text_lv_place = (px-125,py-185+75*i)

                text_hp = font_ui.render(f"{self._monsters_data[i]["hp"]}/",True,(0,0,0))
                text_hp_place = (px-290,py-160+75*i)

                text_max_hp = font_ui.render(f"{self._monsters_data[i]["max_hp"]}",True,(0,0,0))
                text_max_hp_place = (px-265,py-160+75*i)

                text_element = font_ui.render(f"element:{self._monsters_data[i]["element"]}",True,(0,0,0))
                text_element_place = (px-200,py-160+75*i)

                price = self._monsters_data[i]["level"]
                text_price = font_amount.render(f"${price}",True,(0,0,0))
                text_price_place = (px+250,py-175+75*i)

                buy_buttom = Button(
                    "UI/button_shop.png", "UI/button_shop_hover.png",
                    px+300, py-200+75*i, 50, 50,
                    lambda: self.buy_monster(self._monsters_data[i],price)
                )
                monster = {
                    "monster_background":monster_background,
                    "picture":picture,
                    "text_name":[text_name,text_name_place],
                    "text_lv":[text_lv,text_lv_place],
                    "text_hp":[text_hp,text_hp_place],
                    "text_max_hp":[text_max_hp,text_max_hp_place],
                    "text_price":[text_price,text_price_place],
                    "text_element":[text_element,text_element_place]
                }
                for k in monster:
                    if "text" in k:
                        screen.blit(monster[k][0],monster[k][1])
                    else:
                        monster[k].update(0)
                        monster[k].draw(screen)
                if i not in self.sold_monster:
                    buy_buttom.update(0)
                    buy_buttom.draw(screen)
                else:
                    dark_overlay = pg.Surface((300, 75), pg.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 128))
                    screen.blit(dark_overlay,(px-350, py-200+75*i))
        elif self.mode == "sell":
            for i in range(len(scene_manager._scenes["game"].game_manager.bag._monsters_data)):
                monster_background = Picture(
                    "UI/raw/UI_Flat_Banner03a.png",
                    px-350, py-200+75*i, 300, 75,
                )
                picture = Picture(
                    scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["sprite_path"],
                    px-340, py-190+75*i, 50, 50,
                )

                text_name = font_monster.render(f"{scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["name"]}",True,(0,0,0))
                text_name_place = (px-290,py-190+75*i)

                text_lv = font_monster.render(f"Lv{scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["level"]}",True,(0,0,0))
                text_lv_place = (px-125,py-185+75*i)

                text_hp = font_ui.render(f"{scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["hp"]}/",True,(0,0,0))
                text_hp_place = (px-290,py-160+75*i)

                text_max_hp = font_ui.render(f"{scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["max_hp"]}",True,(0,0,0))
                text_max_hp_place = (px-265,py-160+75*i)

                text_element = font_ui.render(f"element:{scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["element"]}",True,(0,0,0))
                text_element_place = (px-200,py-160+75*i)

                price = scene_manager._scenes["game"].game_manager.bag._monsters_data[i]["level"]
                text_price = font_amount.render(f"${price}",True,(0,0,0))
                text_price_place = (px+250,py-175+75*i)

                sell_buttom = Button(
                    "UI/button_shop.png", "UI/button_shop_hover.png",
                    px+300, py-200+75*i, 50, 50,
                    lambda: self.sell_monster(i,price)
                )
                monster = {
                    "monster_background":monster_background,
                    "picture":picture,
                    "text_name":[text_name,text_name_place],
                    "text_lv":[text_lv,text_lv_place],
                    "text_hp":[text_hp,text_hp_place],
                    "text_max_hp":[text_max_hp,text_max_hp_place],
                    "text_price":[text_price,text_price_place],
                    "text_element":[text_element,text_element_place]
                }
                for k in monster:
                    if "text" in k:
                        screen.blit(monster[k][0],monster[k][1])
                    else:
                        monster[k].update(0)
                        monster[k].draw(screen)
                if i not in self.player_sold_monster:
                    sell_buttom.update(0)
                    sell_buttom.draw(screen)
                else:
                    dark_overlay = pg.Surface((300, 75), pg.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 128))
                    screen.blit(dark_overlay,(px-350, py-200+75*i))
                

    def show_item(self,screen):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        font_items = resource_manager.get_font("Minecraft.ttf", 20)
        font_amount = resource_manager.get_font("Minecraft.ttf", 16)

        if self.mode == "buy":
            for i in range(len(self._items_data)):
                picture = Picture(
                    self._items_data[i]["sprite_path"],
                    px-340, py-190+75*i, 50, 50,
                )
                price = 5
                text_name = font_items.render(f"{self._items_data[i]["name"]}",True,(0,0,0))
                text_name_place = (px-240,py-190+75*i)

                text_amount = font_amount.render(f"X{self._items_data[i]["count"]}",True,(0,0,0))
                text_amount_place = (px-100,py-175+75*i)

                text_price = font_amount.render(f"${price}",True,(0,0,0))
                text_price_place = (px+250,py-175+75*i)

                

                buy_buttom = Button(
                    "UI/button_shop.png", "UI/button_shop_hover.png",
                    px+300, py-200+75*i, 50, 50,
                    lambda: self.buy_item(self._items_data[i],price)
                )
                item = {
                    "picture":picture,
                    "text_name":[text_name,text_name_place],
                    "text_amount":[text_amount,text_amount_place],
                    "text_price":[text_price,text_price_place]
                }
                for k in item:
                    if "text" in k:
                        screen.blit(item[k][0],item[k][1])
                    else:
                        item[k].update(0)
                        item[k].draw(screen)
                buy_buttom.update(0)
                buy_buttom.draw(screen)
        elif self.mode == "sell":
            for i in range(len(scene_manager._scenes["game"].game_manager.bag._items_data)):
                if scene_manager._scenes["game"].game_manager.bag._items_data[i]["name"] == "Coins":
                    continue
                picture = Picture(
                    scene_manager._scenes["game"].game_manager.bag._items_data[i]["sprite_path"],
                    px-340, py-190+75*i, 50, 50,
                )
                price = 5

                text_name = font_items.render(f"{scene_manager._scenes["game"].game_manager.bag._items_data[i]["name"]}",True,(0,0,0))
                text_name_place = (px-240,py-190+75*i)

                text_amount = font_amount.render(f"X{scene_manager._scenes["game"].game_manager.bag._items_data[i]["count"]}",True,(0,0,0))
                text_amount_place = (px-100,py-175+75*i)

                text_price = font_amount.render(f"${price}",True,(0,0,0))
                text_price_place = (px+250,py-175+75*i)

                

                sell_buttom = Button(
                    "UI/button_shop.png", "UI/button_shop_hover.png",
                    px+300, py-200+75*i, 50, 50,
                    lambda: self.sell_item(scene_manager._scenes["game"].game_manager.bag._items_data[i],price)
                )
                item = {
                    "picture":picture,
                    "text_name":[text_name,text_name_place],
                    "text_amount":[text_amount,text_amount_place],
                    "text_price":[text_price,text_price_place]
                }
                for k in item:
                    if "text" in k:
                        screen.blit(item[k][0],item[k][1])
                    else:
                        item[k].update(0)
                        item[k].draw(screen)
                sell_buttom.update(0)
                sell_buttom.draw(screen)

    def buy_monster(self, monster:Monster, price:int):
        if scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] >= price:
            scene_manager._scenes["game"].game_manager.bag._monsters_data.append(monster)
            scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] -= price
            self.sold_monster.append(self._monsters_data.index(monster))
        else:
            font_special = resource_manager.get_font("Minecraft.ttf", 50)
            self.special_text = font_special.render("No enough money!",True,(0,0,0))
            self.special_text_number = 120
    def buy_item(self, item:Item, price:int):
        if scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] >= price:
            if item["count"] > 0:
                scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index[item["name"]]]["count"] += 1
                scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] -= price
                item["count"] -= 1
            else:
                font_special = resource_manager.get_font("Minecraft.ttf", 50)
                self.special_text = font_special.render("No more!",True,(0,0,0))
                self.special_text_number = 120
        else:
            font_special = resource_manager.get_font("Minecraft.ttf", 50)
            self.special_text = font_special.render("No enough money!",True,(0,0,0))
            self.special_text_number = 120
    def sell_monster(self, index:int, price:int):
        if len(scene_manager._scenes["game"].game_manager.bag._monsters_data) > 1:
            self.player_sold_monster.append(index)
            self.player_sold_monster = sorted(self.player_sold_monster)
            self.player_sold_monster_delete_list = []
            for i in self.player_sold_monster:
                self.player_sold_monster_delete_list.append(i-len(self.player_sold_monster_delete_list))
            scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] += price
        else:
            font_special = resource_manager.get_font("Minecraft.ttf", 50)
            self.special_text = font_special.render("You can't sell your last monster!",True,(0,0,0))
            self.special_text_number = 120
    def sell_item(self, item:Item, price:int):
        if scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index[item["name"]]]["count"] > 0:
            scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index[item["name"]]]["count"] -= 1
            scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"] += price
        else:
            font_special = resource_manager.get_font("Minecraft.ttf", 50)
            self.special_text = font_special.render("Nothing to sell!",True,(0,0,0))
            self.special_text_number = 120
            

    def update(self, dt: float):
        self.show_item_button.update(dt)
        self.show_monster_button.update(dt)
        self.shop_x_button.update(dt)
        self.buy_buttom.update(dt)
        self.sell_button.update(dt)

    def draw(self, screen: pg.Surface):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        font_coin = resource_manager.get_font("Minecraft.ttf", 50)
        self.money_text = font_coin.render(f"{scene_manager._scenes["game"].game_manager.bag._items_data[self.player_item_list_index["Coins"]]["count"]}",True,(0,0,0))

        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 128))
        screen.blit(dark_overlay,(0,0))

        self.flat_picture.draw(screen)
        self.shop_x_button.draw(screen)
        self.show_item_button.draw(screen)
        self.show_monster_button.draw(screen)
        self.buy_buttom.draw(screen)
        self.sell_button.draw(screen)
        self.coin_picture.draw(screen)
        screen.blit(self.money_text,(px+60,py+100))
        screen.blit(self.monster_text,(px+25,py+240))
        screen.blit(self.item_text,(px+125,py+240))

        font_title = resource_manager.get_font("Minecraft.ttf", 48)
        text_buy = font_title.render("BUY",True,(0,0,0))
        screen.blit(text_buy,(px-325,py-275))
        text_sell = font_title.render("SELL",True,(0,0,0))
        screen.blit(text_sell,(px-125,py-275))

        if self.mode != "buy":
            dark_overlay = pg.Surface((200,75), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 128))
            screen.blit(dark_overlay,(px-350, py-275))
        if self.mode != "sell":
            dark_overlay = pg.Surface((200,75), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 128))
            screen.blit(dark_overlay,(px-150, py-275))


        if self.special_text:
            screen.blit(self.special_text,(px-150,py+150))
            self.special_text_number -= 1
            if self.special_text_number == 0:
                self.special_text = None

        if self.show == "monster":
            self.show_monster(screen)
        elif self.show == "item":
            self.show_item(screen)
        
        
        

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Trading_Overlay":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        trading_overlay = cls(monsters, items)
        return trading_overlay