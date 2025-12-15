import pygame as pg
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components.button import Button, Slide_Button, OnOff_Button, Picture, Hover_Picture
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
from typing import override

import random
from src.utils.definition import Monster, Item
from src.data.bag import Bag



class BattleScene(Scene):
    # Background Image
    background: BackgroundSprite
    
    bag: Bag


    

    def __init__(self):
        super().__init__()
        
        self.opponent_monster = Monster()
        self.player_monster = Monster()
        self.can_evolute_monster = {
            "menu_sprites/menusprite1.png":["menu_sprites/menusprite2.png","Charizard"],
            "menu_sprites/menusprite2.png":["menu_sprites/menusprite3.png","Blastoise"],
            "menu_sprites/menusprite7.png":["menu_sprites/menusprite8.png","no_name_8"],
            "menu_sprites/menusprite8.png":["menu_sprites/menusprite9.png","no_name_9"],
            "menu_sprites/menusprite12.png":["menu_sprites/menusprite13.png","no_name_13"],
            "menu_sprites/menusprite13.png":["menu_sprites/menusprite14.png","no_name_14"],
            "menu_sprites/menusprite15.png":["menu_sprites/menusprite16.png","no_name_16"]
        }
        self.background = BackgroundSprite("backgrounds/background1.png")
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        self.font_dialog = resource_manager.get_font("Minecraft.ttf", 24)
        self.font_monster = resource_manager.get_font("Minecraft.ttf", 16)
        self.font_ui = resource_manager.get_font("Minecraft.ttf", 10)
        self.font_notice = resource_manager.get_font("Minecraft.ttf", 28)
        self.font_questionmark = resource_manager.get_font("Minecraft.ttf", 50)

        self.text_notice_1 = self.font_notice.render(f"***element***",True,(0,0,0))
        self.text_notice_2 = self.font_notice.render(f"fire > grass > water > fire",True,(0,0,0))
        self.text_questionmark = self.font_questionmark.render("?",True,(0,0,0))

        #Pictures
        self.dialog_box = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            0, 520, 1280, 200,
        )
        self.notice_picture = Hover_Picture(
            "UI/raw/UI_Flat_FrameSlot01c.png",
            0, 0, 50, 50,
            lambda: self.change_notice()
        )
        self.notice_box = Picture(
            "UI/raw/UI_Flat_Frame03a.png",
            px-200, 0, 400, 200,
        )
        

        #Buttoms
        self.attack_button = Button(
            "ingame_ui/options1.png", "ingame_ui/options1.png",
            px-600, py+250, 100, 100,
            lambda: self.player_attack()
        )
        self.defend_button = Button(
            "ingame_ui/options2.png", "ingame_ui/options2.png",
            px-450, py+250, 100, 100,
            lambda: self.player_defend()
        )
        self.item_button = Button(
            "ingame_ui/potion.png", "ingame_ui/potion.png",
            px-300, py+250, 100, 100,
            lambda: self.player_choose_item()
        )
        self.change_button = Button(
            "ingame_ui/options7.png", "ingame_ui/options7.png",
            px-150, py+250, 100, 100,
            lambda: self.change_progress("selecting_character")
        )
        self.run_button = Button(
            "ingame_ui/baricon1.png", "ingame_ui/baricon1.png",
            px, py+250, 100, 100,
            lambda: self.player_run()
        )
        self.evolution_button = Button(
            "ingame_ui/baricon7.png", "ingame_ui/baricon7.png",
            px+150, py+250, 100, 100,
            lambda: self.player_evolution()
        )

        #catching Pokemon
        self.catch_yes_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px-150, py+250, 100, 100,
            lambda: self.catch()
        )
        self.catch_no_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+50, py+250, 100, 100,
            lambda: self.change_progress("ending")
        )

        #using item
        self.potion_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px-150, py+250, 100, 100,
            lambda: self.player_use_item("Potion")
        )
        self.powerpotion_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+50, py+250, 100, 100,
            lambda: self.player_use_item("PowerPotion")
        )
        self.defendpotion_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+250, py+250, 100, 100,
            lambda: self.player_use_item("DefendPotion")
        )
        self.item_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px+450, py+250, 100, 100,
            lambda: self.change_player_action("choosing")
        )
        
        self.attack_effects = pg.image.load("assets/images/ingame_ui/baricon3.png").convert_alpha()
        self.attack_effects = pg.transform.scale(self.attack_effects,(200,200))
        self.defend_effects = pg.image.load("assets/images/ingame_ui/options6.png").convert_alpha()
        self.defend_effects = pg.transform.scale(self.defend_effects,(200,200))

        self.pokemon_ball = pg.image.load("assets/images/ingame_ui/ball.png").convert_alpha()
        self.pokemon_ball = pg.transform.scale(self.pokemon_ball,(200,200))
        

        self.potion = pg.image.load("assets/images/ingame_ui/potion.png").convert_alpha()
        self.potion = pg.transform.scale(self.potion,(200,200))

        self.player_buff_icon_attack = pg.image.load("assets/images/ingame_ui/options1.png")
        self.player_buff_icon_attack = pg.transform.scale(self.player_buff_icon_attack,(50,50))
        self.player_buff_icon_defend = pg.image.load("assets/images/ingame_ui/options2.png")
        self.player_buff_icon_defend = pg.transform.scale(self.player_buff_icon_defend,(50,50))

        self.opponent_buff_icon_attack = pg.image.load("assets/images/ingame_ui/options1.png")
        self.opponent_buff_icon_attack = pg.transform.scale(self.opponent_buff_icon_attack,(50,50))
        self.opponent_buff_icon_defend = pg.image.load("assets/images/ingame_ui/options2.png")
        self.opponent_buff_icon_defend = pg.transform.scale(self.opponent_buff_icon_defend,(50,50))
    #element notice
    def change_notice(self):
        self.notice = True


    #battle progression
    def change_progress(self,next):
        self.next_progress = next
        if self.wait > 0:
            self.battle_progress = "wait"
            self.wait -= 1
        else:
            self.wait = 1
            self.battle_progress = next
    def change_player_action(self,next):
        self.next_action = next
        if self.wait > 0:
            self.player_action = "wait"
            self.wait -= 1
        else:
            self.wait = 1
            self.player_action = next
    def change_opponent_action(self,next):
        self.next_action = next
        if self.wait > 0:
            self.opponent_action = "wait"
            self.wait -= 1
        else:
            self.wait = 1
            self.opponent_action = next

    def select_character(self,screen):
        self.player_monster_ui_position = -self.dialog_number*2.5
        self.player_monster_position = -self.dialog_number*2.5
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        font_monster = resource_manager.get_font("Minecraft.ttf", 10)
        text_question = self.font_dialog.render("Choose your Pokemon!",True,(255,255,255))
        screen.blit(text_question,(px-600,py+200))
        for i in range(len(self.bag._monsters_data)):
            monster_background = Button(
                "UI/raw/UI_Flat_Button02a_2.png","UI/raw/UI_Flat_Button02a_1.png",
                px-600+100*i, py+250, 100, 100,
                lambda: self.choose_character(self.bag._monsters_data[i],i)
            )
            monster_background.update(0)
            monster_background.draw(screen)
            picture = Picture(
                self.bag._monsters_data[i]["sprite_path"],
                px-575+100*i, py+250, 50, 50,
            )
            picture.draw(screen)

            block_max_hp = pg.Surface((80,10))
            block_max_hp.fill((255, 0, 0))
            screen.blit(block_max_hp,(px-590+100*i,py+320))

            block_hp = pg.Surface((80*(self.bag._monsters_data[i]["hp"]/self.bag._monsters_data[i]["max_hp"]),10))
            block_hp.fill((0, 255, 0))
            screen.blit(block_hp,(px-590+100*i,py+320))

            screen.blit(font_monster.render(f"{self.bag._monsters_data[i]["name"]}",True,(0,0,0)),(px-575+100*i,py+310))

            if self.bag._monsters_data[i]["hp"] == 0:
                dark = pg.Surface((100,100),pg.SRCALPHA)
                dark.fill((0,0,0,128))
                screen.blit(dark,(px-600+100*i,py+250))

    def choose_character(self,monster:Monster,number):
        if monster["hp"]>0:
            self.player_monster = monster
            self.player_monster_number = number
            self.change_progress("pre_battle")
        else:
            pass
    def check_alive(self,monster:Monster):
        return monster["hp"] > 0

    def check_player_monsters_alive(self):
        return any(self.check_alive(i) for i in self.bag._monsters_data)

    def catch(self):
        if self.bag._items_data[self.pokeball_number]["count"] > 0:
            self.bag._monsters_data.append(self.opponent_monster)
            self.change_progress("catching")
        else:
            self.special_texts = ["You don't have Pokeball!"]

    def battle_over(self,screen):
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dark_overlay.fill((0, 0, 0, min(255,255-scene_manager.loading_number)))
        screen.blit(dark_overlay,(0,0))
        scene_manager.loading_number -= 5
        if scene_manager.loading_number <= 0:
            scene_manager.loading_number = 255
            scene_manager.change_scene("game")

    #player actions
    def player_choose(self):
        if self.player_defense:
            self.player_defense -= 1
        if self.player_strong:
            self.player_strong -= 1
        self.change_player_action("choosing")
    def player_attack(self):
        self.dialogues = 2
        self.player_damage = self.player_monster["level"]*5
        if self.opponent_defense:
            self.player_damage *= 0.5
        if self.player_strong:
            self.player_damage *= 2
        if self.player_monster["element"] == "fire":
            if self.opponent_monster["element"] == "water":
                self.player_damage *= 0.8
            elif self.opponent_monster["element"] == "grass":
                self.player_damage *= 1.5
        elif self.player_monster["element"] == "water":
            if self.opponent_monster["element"] == "grass":
                self.player_damage *= 0.8
            elif self.opponent_monster["element"] == "fire":
                self.player_damage *= 1.5
        elif self.player_monster["element"] == "grass":
            if self.opponent_monster["element"] == "fire":
                self.player_damage *= 0.8
            elif self.opponent_monster["element"] == "water":
                self.player_damage *= 1.5
        self.player_damage = round(self.player_damage)
        self.texts = [f"{self.player_monster["name"]} is attacking!", f"{self.player_monster["name"]} causes {self.player_damage} damage!"]
        self.change_player_action("attack")
        pass
    def player_defend(self):
        self.dialogues = 1
        self.player_defense += 2
        self.texts = ["You choose to defend!"]
        self.change_player_action("defend")
        pass
    def player_choose_item(self):
        self.change_player_action("choose item")
    def player_use_item(self,text:str):
        for i in self.bag._items_data:
            if i["name"] == text:
                if i["count"] > 0:
                    self.dialogues = 1
                    self.texts = [f"You use {text}!"]
                    i["count"] -= 1
                    if text == "Potion":
                        self.dialogues += 1
                        self.player_monster["hp"] = min(self.player_monster["hp"]+200,self.player_monster["max_hp"])
                        self.texts.append("Your hp heals by 200!")
                    elif text == "DefendPotion":
                        self.player_defense += 5
                    elif text == "PowerPotion":
                        self.player_strong += 5
                    self.change_player_action("use item")
                else:
                    break
    def player_run(self):
        self.dialogues = 1
        self.texts = ["You run as fast as you can..."]
        self.change_player_action("run")
        pass
    def player_evolution(self):
        if self.player_monster["sprite_path"] in self.can_evolute_monster:
            self.player_monster["name"] = self.can_evolute_monster[self.player_monster["sprite_path"]][1]
            self.player_monster["sprite_path"] = self.can_evolute_monster[self.player_monster["sprite_path"]][0]
            self.player_monster["max_hp"] += 200
            self.player_monster["hp"] += 200
            self.player_monster["level"] += 20
            self.dialogues = 1
            self.texts = [f"Your Pokemon evolute to {self.player_monster["name"]}!"]
            self.change_player_action("evolution")
        else:
            self.special_texts = ["This Pokemon can't evolute..."]
        pass
    
    #opponent actions
    def opponent_choose(self):
        if self.opponent_defense:
            self.opponent_defense -= 1
        if self.opponent_strong:
            self.opponent_strong -= 1
        self.dialogues = 2
        self.texts = ["Opponent is thinking of what to do..."]
        self.opponent_todo = random.choice(["attack","defend","use item"])
        self.texts.append(f"Opponent choose to {self.opponent_todo}!")
        self.change_opponent_action("choosing")
    def opponent_attack(self):
        self.dialogues = 2
        self.opponent_damage = self.opponent_monster["level"]*5
        if self.player_defense:
            self.opponent_damage *= 0.5
        if self.opponent_strong:
            self.opponent_damage *= 2
        if self.opponent_monster["element"] == "fire":
            if self.player_monster["element"] == "water":
                self.opponent_damage *= 0.8
            elif self.player_monster["element"] == "grass":
                self.opponent_damage *= 1.5
        elif self.opponent_monster["element"] == "water":
            if self.player_monster["element"] == "grass":
                self.opponent_damage *= 0.8
            elif self.player_monster["element"] == "fire":
                self.opponent_damage *= 1.5
        elif self.opponent_monster["element"] == "grass":
            if self.player_monster["element"] == "fire":
                self.opponent_damage *= 0.8
            elif self.player_monster["element"] == "water":
                self.opponent_damage *= 1.5
        self.opponent_damage = round(self.opponent_damage)
        self.texts = [f"{self.opponent_monster["name"]} is attacking!", f"{self.opponent_monster["name"]} causes {self.opponent_damage} damage!"]
        self.change_opponent_action("attack")
        pass
    def opponent_defend(self):
        self.dialogues = 1
        self.opponent_defense += 2
        self.texts = ["Opponent choose to defend!"]
        self.change_opponent_action("defend")
        pass
    def opponent_use_item(self):
        self.dialogues = 2
        self.texts = ["Opponent is using potion...","Opponent's hp heals by 200!"]
        self.change_opponent_action("use item")
        pass

    @override
    def enter(self) -> None:
        #default data
        self.bag = scene_manager._scenes["game"].game_manager.bag
        self.player_monster = self.bag._monsters_data[0]
        self.opponent_monster_ui_position = GameSettings.SCREEN_WIDTH
        self.player_monster_ui_position = -300
        self.opponent_monster_position = GameSettings.SCREEN_WIDTH
        self.player_monster_position = -200
        self.winner = None

        for i in range(len(self.bag._items_data)):
            if self.bag._items_data[i]["name"] == "Pokeball":
                self.pokeball_number = i
            elif self.bag._items_data[i]["name"] == "Potion":
                self.potion_number = i
        
        #others
        self.battle_progress = "loading"
        self.turn = "player"
        self.dialogues = 2
        self.player_defense = 0
        self.player_strong = 0
        self.opponent_defense = 0
        self.opponent_strong = 0

        self.battling = False
        self.battle_progress = "loading"
        self.dialog_number = 120
        self.special_dialog_number = 120
        self.texts = []
        self.special_texts = []
        self.wait = 1
        self.notice = False

        self.pokemon_ball.set_alpha(0)
        sound_manager.play_bgm("RBY 110 Battle! (Wild Pokemon).ogg")
        pass

    @override
    def exit(self) -> None:
        if scene_manager.bush_battle:
            scene_manager.change_bush_battle()
        if scene_manager.battle_mode:
            scene_manager.change_battle()
        pass

    @override
    def update(self, dt: float) -> None:
        
        #default
        self.notice_picture.update(dt)

        #opponent
        self.opponent_block_max_hp = pg.Surface((100,10))
        self.opponent_block_max_hp.fill((255, 0, 0)) 
        if self.winner == "player":
            self.opponent_block_hp = pg.Surface((0,10))
        else:
            self.opponent_block_hp = pg.Surface((100*(self.opponent_monster["hp"]/self.opponent_monster["max_hp"]),10))
        self.opponent_block_hp.fill((0, 255, 0))
        
        self.text_opponent_name = self.font_monster.render(f"{self.opponent_monster["name"]}",True,(0,0,0))
        self.text_opponent_lv = self.font_monster.render(f"Lv{self.opponent_monster["level"]}",True,(0,0,0)) 
        self.text_opponent_hp = self.font_ui.render(f"{self.opponent_monster["hp"]}/",True,(0,0,0))       
        self.text_opponent_max_hp = self.font_ui.render(f"{self.opponent_monster["max_hp"]}",True,(0,0,0))
        self.text_opponent_element = self.font_ui.render(f"element:{self.opponent_monster["element"]}",True,(0,0,0))

        #player
        self.player_block_max_hp = pg.Surface((100,10))
        self.player_block_max_hp.fill((255, 0, 0))      
        self.player_block_hp = pg.Surface((100*(self.player_monster["hp"]/self.player_monster["max_hp"]),10))
        self.player_block_hp.fill((0, 255, 0))
        
        self.text_player_name = self.font_monster.render(f"{self.player_monster["name"]}",True,(0,0,0))
        self.text_player_lv = self.font_monster.render(f"Lv{self.player_monster["level"]}",True,(0,0,0))       
        self.text_player_hp = self.font_ui.render(f"{self.player_monster["hp"]}/",True,(0,0,0))       
        self.text_player_max_hp = self.font_ui.render(f"{self.player_monster["max_hp"]}",True,(0,0,0))
        self.text_player_element = self.font_ui.render(f"element:{self.player_monster["element"]}",True,(0,0,0))

        if self.battle_progress == "battling" and self.turn == "player":
            if self.player_action == "choosing":
                self.attack_button.update(dt)
                self.defend_button.update(dt)
                self.item_button.update(dt)
                self.change_button.update(dt)
                self.run_button.update(dt)
                self.evolution_button.update(dt)
            if self.player_action == "choose item":
                self.potion_button.update(dt)
                self.defendpotion_button.update(dt)
                self.powerpotion_button.update(dt)
                self.item_back_button.update(dt)
        if self.battle_progress == "choose_to_catch":
            self.catch_yes_button.update(dt)
            self.catch_no_button.update(dt)
        pass


    @override
    def draw(self, screen: pg.Surface) -> None:
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        self.background.draw(screen)
        self.dialog_box.draw(screen)
        self.notice_picture.draw(screen)
        screen.blit(self.text_questionmark,(15,0))
        if self.notice:
            self.notice_box.draw(screen)
            screen.blit(self.text_notice_1,(px-125,50))
            screen.blit(self.text_notice_2,(px-175,100))
        self.notice = False

        #opponent character
        self.opponent_monster_background = Picture(
            "UI/raw/UI_Flat_Banner03a.png",
            self.opponent_monster_ui_position, py-300, 300, 75,
        )
        self.opponent_monster_background.draw(screen)
        self.opponent_monster_picture = Picture(
            self.opponent_monster["sprite_path"],
            self.opponent_monster_position, py-200, 200, 200,
        )
        self.opponent_monster_picture.draw(screen)

        if self.opponent_defense:
            text = self.font_ui.render(f"{self.opponent_defense}",True,(0,0,0))
            screen.blit(self.opponent_buff_icon_defend,(px+350,0))
            screen.blit(text,(px+350,50))

        screen.blit(self.opponent_block_max_hp,(self.opponent_monster_ui_position+60,py-270))
        screen.blit(self.opponent_block_hp,(self.opponent_monster_ui_position+60,py-270))
        screen.blit(self.text_opponent_name,(self.opponent_monster_ui_position+60,py-290))
        screen.blit(self.text_opponent_lv,(self.opponent_monster_ui_position+225,py-285))
        screen.blit(self.text_opponent_hp,(self.opponent_monster_ui_position+60,py-260))
        screen.blit(self.text_opponent_max_hp,(self.opponent_monster_ui_position+85,py-260))
        screen.blit(self.text_opponent_element,(self.opponent_monster_ui_position+150,py-260))



        #player character
        self.player_monster_background = Picture(
            "UI/raw/UI_Flat_Banner03a.png",
            self.player_monster_ui_position, py+25, 300, 75,
        )
        self.player_monster_background.draw(screen)
        self.player_monster_picture = Picture(
            self.player_monster["sprite_path"],
            self.player_monster_position, py-200, 200, 200,
        )
        self.player_monster_picture.draw(screen)

        if self.player_defense:
            text = self.font_ui.render(f"{self.player_defense}",True,(0,0,0))
            screen.blit(self.player_buff_icon_defend,(50,py+100))
            screen.blit(text,(50,py+150))
        if self.player_strong:
            text = self.font_ui.render(f"{self.player_strong}",True,(0,0,0))
            screen.blit(self.player_buff_icon_attack,(0,py+100))
            screen.blit(text,(0,py+150))

        screen.blit(self.player_block_max_hp,(self.player_monster_ui_position+60,py+55))
        screen.blit(self.player_block_hp,(self.player_monster_ui_position+60,py+55))
        screen.blit(self.text_player_name,(self.player_monster_ui_position+60,py+35))
        screen.blit(self.text_player_lv,(self.player_monster_ui_position+225,py+40))
        screen.blit(self.text_player_hp,(self.player_monster_ui_position+60,py+65))
        screen.blit(self.text_player_max_hp,(self.player_monster_ui_position+85,py+65))
        screen.blit(self.text_player_element,(self.player_monster_ui_position+150,py+65))

        if scene_manager.bush_battle:
            screen.blit(self.pokemon_ball,(self.opponent_monster_position,py-200))




        if self.battle_progress == "loading":
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, max(0,scene_manager.loading_number)))
            screen.blit(dark_overlay,(0,0))
            scene_manager.loading_number -= 5
            if scene_manager.loading_number <= 0:
                scene_manager.loading_number = 255
                if scene_manager.bush_battle:
                    self.texts = ["You found a Pokemon in the bush!",f"{self.opponent_monster["name"]} appears!"]                    
                else:
                    self.texts = ["You start a battle!",f"Opponent send out {self.opponent_monster["name"]}."]
                self.change_progress("dialogue")

        elif self.battle_progress == "dialogue":
            if self.dialogues > 0:
                dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                screen.blit(dialog,(px-600,py+200))
                self.dialog_number -= 1
                if self.dialogues == 1:
                    self.opponent_monster_ui_position = GameSettings.SCREEN_WIDTH-300+self.dialog_number*2.5
                    self.opponent_monster_position = GameSettings.SCREEN_WIDTH-300+self.dialog_number*2.5
                    
                if self.dialog_number == 0:
                    self.dialog_number = 120
                    self.dialogues -= 1
            else:
                self.change_progress("selecting_character")

        elif self.battle_progress == "selecting_character":
            self.select_character(screen)
            
        elif self.battle_progress == "pre_battle":
            dialog = self.font_dialog.render(f"Go, {self.player_monster["name"]}!",True,(255,255,255))
            screen.blit(dialog,(px-600,py+200))
            self.dialog_number -= 1
            self.player_monster_ui_position = -self.dialog_number*2.5
            self.player_monster_position = 100-self.dialog_number*2.5
            if self.dialog_number == 0:
                self.dialog_number = 120
                self.dialogues -= 1
                self.change_progress("battling")
                if self.battling:
                    self.turn = "opponent"
                    self.opponent_choose()
                else:
                    self.battling = True
                    self.turn = "player"
                    self.player_choose()

        elif self.battle_progress == "battling":
            if self.turn == "player":
                if self.player_action == "choosing":
                    if self.special_texts:
                        dialog = self.font_dialog.render(self.special_texts[0],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.special_dialog_number -= 1
                        if self.special_dialog_number == 0:
                            self.special_dialog_number = 120
                            self.special_texts.pop(0)
                    else:
                        action_chooseing = self.font_dialog.render("What should you do?",True,(255,255,255))
                        screen.blit(action_chooseing,(px-600,py+200))
                    self.attack_button.draw(screen)
                    self.defend_button.draw(screen)
                    self.item_button.draw(screen)
                    self.change_button.draw(screen)
                    self.run_button.draw(screen)
                    self.evolution_button.draw(screen)
                elif self.player_action == "attack":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialogues == 2:
                            self.player_monster_position = 200+5*120*(self.dialog_number//60)-5*2*(self.dialog_number%60)*((-1)**(1+self.dialog_number//60))
                            if 30<self.dialog_number<60:
                                attack_effect_transparent = (self.dialog_number-30)*255/30
                                self.attack_effects.set_alpha(attack_effect_transparent)
                                screen.blit(self.attack_effects,(self.opponent_monster_position,py-200))
                            elif self.dialog_number == 60:
                                self.opponent_monster["hp"] -= min(self.opponent_monster["hp"],self.player_damage)
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_player_action("end")   
                elif self.player_action == "defend":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialogues == 1:
                            if 90<self.dialog_number<120:
                                defend_effect_transparent = (self.dialog_number-90)*255/30
                                self.defend_effects.set_alpha(defend_effect_transparent)
                                screen.blit(self.defend_effects,(self.player_monster_position,py-200))
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_player_action("end")   
                    pass
                elif self.player_action == "choose item":
                    dialog = self.font_dialog.render("Which item do you want to use?",True,(255,255,255))
                    screen.blit(dialog,(px-600,py+200))
                    self.potion_button.draw(screen)
                    self.defendpotion_button.draw(screen)
                    self.powerpotion_button.draw(screen)
                    self.item_back_button.draw(screen)
                    for i in self.bag._items_data:
                        if "Potion" in i["name"]:
                            text = self.font_ui.render(f"{i['name']}",True,(0,0,0))
                            screen.blit(text,(px-125+200*self.bag._items_data.index(i),py+275))
                            text2 = self.font_ui.render(f"{i["count"]}",True,(0,0,0))
                            screen.blit(text2,(px-125+200*self.bag._items_data.index(i),py+285))
                            if i["count"] == 0:
                                dark_overlay = pg.Surface((100,100), pg.SRCALPHA)
                                dark_overlay.fill((0, 0, 0, 128))
                                screen.blit(dark_overlay,(px-150+200*self.bag._items_data.index(i),py+250))
                elif self.player_action == "use item":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_player_action("end")   
                elif self.player_action == "run":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.battling = False
                        self.change_progress("end")
                elif self.player_action == "evolution":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_player_action("end")  
                elif self.player_action == "wait":
                    self.change_player_action(self.next_action)
                elif self.player_action == "end":
                    if self.opponent_monster["hp"] == 0:
                        self.winner = "player"
                        self.battling = False
                        self.opponent_monster["hp"] = self.opponent_monster["max_hp"]
                        self.change_progress("end")
                    else:
                        self.turn = "opponent"
                        self.opponent_choose()
            elif self.turn == "opponent":
                if self.opponent_action == "choosing":
                    if self.dialogues > 0:
                        dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        if self.opponent_todo == "attack":
                            self.opponent_attack()
                        elif self.opponent_todo == "defend":
                            self.opponent_defend()
                        elif self.opponent_todo == "use item":
                            self.opponent_use_item()
                elif self.opponent_action == "attack":
                    if self.dialogues > 0:
                        dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialogues == 2:
                            self.opponent_monster_position = GameSettings.SCREEN_WIDTH-300-5*120*(self.dialog_number//60)+5*2*(self.dialog_number%60)*((-1)**(1+self.dialog_number//60))
                            if 30<self.dialog_number<60:
                                attack_effect_transparent = (self.dialog_number-30)*255/30
                                self.attack_effects.set_alpha(attack_effect_transparent)
                                screen.blit(self.attack_effects,(self.player_monster_position,py-200))
                            elif self.dialog_number == 60:
                                self.player_monster["hp"] -= min(self.player_monster["hp"],self.opponent_damage)
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_opponent_action("end")
                        
                elif self.opponent_action == "defend":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialogues == 1:
                            if 90<self.dialog_number<120:
                                defend_effect_transparent = (self.dialog_number-90)*255/30
                                self.defend_effects.set_alpha(defend_effect_transparent)
                                screen.blit(self.defend_effects,(self.opponent_monster_position,py-200))
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_opponent_action("end")  
                elif self.opponent_action == "use item":
                    if self.dialogues > 0:
                        dialog = dialog = self.font_dialog.render(self.texts[len(self.texts)-self.dialogues],True,(255,255,255))
                        screen.blit(dialog,(px-600,py+200))
                        self.dialog_number -= 1
                        if self.dialogues == 2:
                            if 30<self.dialog_number<60:
                                potion_effect_transparent = (self.dialog_number-30)*255/30
                                self.potion.set_alpha(potion_effect_transparent)
                                screen.blit(self.potion,(self.opponent_monster_position,py-200))
                            elif self.dialog_number == 30:
                                self.opponent_monster["hp"] = min(self.opponent_monster["hp"]+200,self.opponent_monster["max_hp"])
                        if self.dialog_number == 0:
                            self.dialog_number = 120
                            self.dialogues -= 1
                    else:
                        self.change_opponent_action("end")  
                elif self.opponent_action == "wait":
                    self.change_opponent_action(self.next_action)
                elif self.opponent_action == "end":
                    if self.player_monster["hp"] == 0:
                        if self.check_player_monsters_alive():
                            self.turn = "player"
                            self.battling = False
                            self.change_progress("selecting_character")
                        else: 
                            self.winner = "opponent"
                            self.change_progress("end")
                    else:
                        self.turn = "player"
                        self.player_choose()

        elif self.battle_progress == "end":
            scene_manager._scenes["game"].game_manager.bag = self.bag
            if self.winner == "player":
                dialog = self.font_dialog.render("You win!",True,(255,255,255))
                screen.blit(dialog,(px-600,py+200))
                self.dialog_number -= 1
                if self.dialog_number == 0:
                    self.dialog_number = 120
                    self.dialogues -= 1
                    if scene_manager.bush_battle:
                        self.change_progress("choose_to_catch")
                    else:
                        self.change_progress("ending")
            elif self.winner == "opponent":
                dialog = self.font_dialog.render("You lose...",True,(255,255,255))
                screen.blit(dialog,(px-600,py+200))
                self.dialog_number -= 1
                if self.dialog_number == 0:
                    self.dialog_number = 120
                    self.dialogues -= 1
                    self.change_progress("ending")
            else:
                self.change_progress("ending")
        elif self.battle_progress == "choose_to_catch":
            if self.special_texts:
                dialog = self.font_dialog.render(self.special_texts[0],True,(255,255,255))
                screen.blit(dialog,(px-600,py+200))
                self.special_dialog_number -= 1
                if self.special_dialog_number == 0:
                    self.special_dialog_number = 120
                    self.special_texts.pop(0)
            else:
                dialog = self.font_dialog.render(f"Do you want to catch {self.opponent_monster["name"]}?",True,(255,255,255))
                screen.blit(dialog,(px-600,py+200))
            self.catch_yes_button.draw(screen)
            self.catch_no_button.draw(screen)

            text_yes = self.font_dialog.render("YES",True,(0,0,0))
            text_no = self.font_dialog.render("No",True,(0,0,0))
            screen.blit(text_yes,(px-125,py+275))
            screen.blit(text_no,(px+75,py+275))

        elif self.battle_progress == "catching":
            dialog = self.font_dialog.render(f"You got {self.opponent_monster["name"]}!",True,(255,255,255))
            screen.blit(dialog,(px-600,py+200))
            self.dialog_number -= 1

            pokemon_ball_transparent = min((120-self.dialog_number)*510/120,255)
            self.pokemon_ball.set_alpha(pokemon_ball_transparent)
            screen.blit(self.pokemon_ball,(self.opponent_monster_position,py-200))

            

            if self.dialog_number == 0:
                self.bag._items_data[self.pokeball_number]["count"] -= 1
                self.dialog_number = 120
                self.dialogues -= 1
                self.change_progress("ending")
        elif self.battle_progress == "ending":
            self.battle_over(screen)
        elif self.battle_progress == "wait":
            self.change_progress(self.next_progress)