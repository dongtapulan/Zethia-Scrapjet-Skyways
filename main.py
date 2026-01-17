import pygame
import sys
import random
import math
from settings import *
from core.engine import Engine
from entities.player import Player
from world.parallax import ParallaxBackground
from entities.scrap import ScrapManager
from entities.enemy_manager import EnemyManager
from world.ground_logic import Ground       
from world.obstacle_gen import ObstacleManager 
from ui.menus import MainMenu, GameOverScreen
from ui.hud import HUD               
from ui.dialogue_box import DialogueBox 

# --- SYSTEMS IMPORTS ---
from systems.combat_system import CombatSystem
from systems.heat_system import HeatSystem
from systems.upgrade_manager import UpgradeManager
from ui.workshop_menu import WorkshopMenu 
from entities.projectiles import GravityWave, GloomLaser
from entities.enemies import BlightBeast, GloomBat, BushMonster, MonsterSaucer, BlightTitan

# --- COMPANION SYSTEM IMPORT ---
from entities.companions import CompanionManager

# --- CUTSCENE IMPORT ---
from cutscenes.intro_story import IntroCutscene

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MENU"
        self.menu = MainMenu(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        self.upgrade_manager = UpgradeManager()
        self.workshop = WorkshopMenu(self.screen, self.upgrade_manager) 
        
        self.intro_cutscene = None
        self.player = None
        self.parallax = None
        self.ground = None          
        self.obstacle_manager = None
        self.scrap_manager = None
        self.enemy_manager = None
        self.companion_manager = None 
        self.combat_system = None
        self.heat_system = HeatSystem()
        self.hud = HUD()            
        self.dialogue = DialogueBox() 
        self.score = 0
        self.difficulty_mult = 1.0 

        # --- AUDIO ASSETS ---
        try:
            self.sfx_scrap_normal = pygame.mixer.Sound("assets/sfx/scrap_pickup.mp3")
            self.sfx_scrap_special = pygame.mixer.Sound("assets/sfx/special_pickup.mp3")
            self.sfx_explosion = pygame.mixer.Sound("assets/sfx/explosion.wav") 
            try:
                self.sfx_gravity_boom = pygame.mixer.Sound("assets/sfx/explosion.wav") 
            except:
                self.sfx_gravity_boom = self.sfx_explosion

            self.sfx_scrap_normal.set_volume(0.5)
            self.sfx_scrap_special.set_volume(0.7)
            self.sfx_explosion.set_volume(0.4)
            if self.sfx_gravity_boom: self.sfx_gravity_boom.set_volume(0.8)
        except:
            self.sfx_scrap_normal = self.sfx_scrap_special = self.sfx_explosion = self.sfx_gravity_boom = None

        self.play_menu_music()

    def play_menu_music(self):
        try:
            pygame.mixer.music.load("assets/sfx/main_theme.mp3") 
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except: pass

    def play_random_bgm(self):
        """Randomly toggles between themes for gameplay variety."""
        themes = ["assets/sfx/main_theme.mp3", "assets/sfx/menu_theme.mp3"]
        chosen_theme = random.choice(themes)
        try:
            pygame.mixer.music.load(chosen_theme)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except: pass

    def stop_player_sfx(self):
        """Stops mechanical SFX on death/menu but leaves BGM alone."""
        if self.player:
            if hasattr(self.player, 'engine_channel') and self.player.engine_channel:
                self.player.engine_channel.stop()
            if hasattr(self.player, 'laser_channel') and self.player.laser_channel:
                self.player.laser_channel.stop()

    def reset_game(self):
        self.player = Player()
        self.heat_system = HeatSystem()
        self.combat_system = CombatSystem(self)
        self.player.heat_system = self.heat_system 
        self.player.combat_system = self.combat_system 
        
        stats = self.upgrade_manager.stats
        self.player.missiles = stats.get("missiles", {}).get("level", 0)
        self.player.lightning_charges = stats.get("lightning_charges", {}).get("level", 0)
        self.player.laser_fuel = float(stats.get("laser_fuel", {}).get("level", 0.0))
        self.player.bombs = stats.get("bombs", {}).get("level", 0)
        
        self.upgrade_manager.apply_all_upgrades(self.player)

        self.parallax = ParallaxBackground()
        self.ground = Ground()      
        self.obstacle_manager = ObstacleManager() 
        self.scrap_manager = ScrapManager()
        self.enemy_manager = EnemyManager(self)
        self.companion_manager = CompanionManager(self.player) 
        
        self.hud = HUD()            
        self.dialogue = DialogueBox() 
        self.score = 0
        self.difficulty_mult = 1.0
        self.state = "PLAYING"
        
        self.play_random_bgm()
        self.dialogue.trigger_random_quip("enemies")

    def handle_event(self, event):
        if self.state == "MENU":
            selection = self.menu.handle_input(event)
            if selection == "Start Game":
                self.intro_cutscene = IntroCutscene(self.screen)
                self.state = "STORY"
            elif selection == "Workshop": self.state = "WORKSHOP"
            elif selection == "Exit": sys.exit()
        
        elif self.state == "STORY":
            if self.intro_cutscene: self.intro_cutscene.handle_input(event)

        elif self.state == "WORKSHOP":
            if self.workshop.handle_input(event) == "BACK":
                self.state = "MENU"

        elif self.state == "GAMEOVER":
            selection = self.game_over_screen.handle_input(event)
            if selection == "Retry": self.reset_game()
            elif selection == "Main Menu":
                self.state = "MENU"
                self.play_menu_music()
            elif selection == "Exit": sys.exit()

        elif self.state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: self.state = "PAUSED"
                if event.key == pygame.K_ESCAPE:
                    self.stop_player_sfx()
                    self.state = "MENU"
                    self.play_menu_music()
                
                if event.key == pygame.K_r and self.player.missiles > 0:
                    self.player.missiles -= 1
                    self.combat_system.manager.launch_missile(self.player, self.enemy_manager.enemies)
                
                if event.key == pygame.K_g and self.player.bombs > 0:
                    self.player.bombs -= 1
                    self.combat_system.manager.trigger_gravity_bomb(self.player, self.enemy_manager.enemies)
                    if self.sfx_gravity_boom: self.sfx_gravity_boom.play()

                if event.key == pygame.K_q and self.player.lightning_charges > 0:
                    self.player.lightning_charges -= 1
                    if hasattr(self.player, 'play_lightning_sfx'): self.player.play_lightning_sfx()
                    targets = list(self.enemy_manager.enemies)[:3]
                    self.combat_system.manager.spawn_lightning(self.player.rect.center, targets)
        
        elif self.state == "PAUSED":
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_p, pygame.K_ESCAPE]:
                self.state = "PLAYING"

    def update(self, dt, flight_input, combat_input):
        if self.state == "STORY":
            if self.intro_cutscene:
                self.intro_cutscene.update(dt)
                if not self.intro_cutscene.active: self.reset_game()
            return

        if self.state != "PLAYING":
            if self.state == "MENU": self.menu.update(dt)
            elif self.state == "WORKSHOP": self.workshop.update(dt)
            elif self.state == "GAMEOVER": self.game_over_screen.update(dt)
            return

        self.difficulty_mult = min(2.0, 1.0 + (self.player.distance / 5000) * 0.1)
        current_scroll_speed = BASE_SCROLL_SPEED * self.difficulty_mult
        scroll_move = dt * current_scroll_speed if self.player.is_alive else 0
        self.player.distance += scroll_move
        
        if self.enemy_manager.boss_active:
            self.parallax.enter_boss_mode()
        else:
            self.parallax.target_boss_factor = 0.0

        self.parallax.update(self.player.distance, dt) 
        self.ground.update(dt, self.player.rect, self.player.is_skimming) 
        self.obstacle_manager.update(dt, self.difficulty_mult) 
        self.scrap_manager.update(dt, self.player.rect.center)
        
        self.player.handle_input(flight_input, dt) 
        self.player.update(dt)

        # --- BALANCED HEAT LOGIC ---
        keys = pygame.key.get_pressed()
        is_firing_any = False

        if self.player.is_alive:
            firing_mg = combat_input["firing"] 
            firing_laser = keys[pygame.K_e] and self.player.laser_fuel > 0
            
            if firing_mg:
                # Lowered from 120 to 45 for better sustain
                self.heat_system.add_heat(45 * dt) 
                self.combat_system.manager.fire_machine_gun(self.player, self.enemy_manager.enemies, dt)
                is_firing_any = True
            
            if firing_laser:
                # Lowered from 80 to 30
                self.heat_system.add_heat(30 * dt) 
                self.combat_system.manager.process_laser_beam(self.player, self.enemy_manager.enemies)
                self.player.laser_fuel -= 15 * dt 
                is_firing_any = True

        if self.companion_manager: self.companion_manager.update(dt, self.enemy_manager.enemies)
        
        if not self.player.is_alive and self.player.has_exploded:
            self.stop_player_sfx()
            self.upgrade_manager.convert_score_to_bolts(self.score)
            self.state = "GAMEOVER"

        self.heat_system.update(dt, is_firing_any)
        self.combat_system.update(dt)
        self.enemy_manager.update(dt, self.player.rect.center, self.combat_system.manager, self.difficulty_mult) 
        
        self.hud.update(dt, self.player)     
        self.dialogue.update(dt, self.player) 
        self._handle_collisions()

    def _handle_collisions(self):
        pm = self.combat_system.manager 
        if pygame.sprite.spritecollide(self.player, self.obstacle_manager.obstacles, True, pygame.sprite.collide_mask):
            self.player.take_damage(25) 
            pm.trigger_explosion(self.player.rect.centerx, self.player.rect.centery)
            if self.sfx_explosion: self.sfx_explosion.play()

        bullet_hits = pygame.sprite.spritecollide(self.player, pm.enemy_bullets, True)
        for bullet in bullet_hits:
            self.player.take_damage(10)
            pm.trigger_explosion(bullet.rect.centerx, bullet.rect.centery)
            if self.sfx_explosion: self.sfx_explosion.play()

        for enemy in self.enemy_manager.enemies:
            if enemy.hp <= 0:
                is_boss = isinstance(enemy, BlightTitan)
                self.enemy_manager.trigger_death_effect(enemy.rect.centerx, enemy.rect.centery)
                if self.sfx_explosion: self.sfx_explosion.play()
                
                if is_boss:
                    self.score += 15000
                    self.player.scrap += 250
                    self.enemy_manager.set_next_boss()
                    self.parallax.exit_boss_mode() 
                    self.play_random_bgm() 
                else:
                    self.score += 150
                    self.player.scrap += 1
                enemy.kill()

        scrap_hits = pygame.sprite.spritecollide(self.player, self.scrap_manager.scrap_group, True)
        for scrap in scrap_hits:
            self.score += scrap.value
            self.player.scrap += 5 
            self.player.weight = min(self.player.max_weight, self.player.weight + scrap.weight_value)
            
            if scrap.scrap_type in ["red_core", "tine_soul", "gold_oracle", "glowing_battery", "missile", "bomb"]:
                if self.sfx_scrap_special: self.sfx_scrap_special.play()
            else:
                if self.sfx_scrap_normal: self.sfx_scrap_normal.play()

            if scrap.scrap_type == "red_core": self.companion_manager.summon("RED")
            elif scrap.scrap_type == "tine_soul": self.companion_manager.summon("TINE")
            elif scrap.scrap_type == "gold_oracle": self.companion_manager.summon("CICI")
            elif scrap.scrap_type == "missile": self.player.missiles = min(self.player.max_missiles, self.player.missiles + 5)
            elif scrap.scrap_type == "bomb": self.player.bombs = min(self.player.max_bombs, self.player.bombs + 2)
            elif scrap.scrap_type == "glowing_battery": self.heat_system.heat = max(0, self.heat_system.heat - 30)

    def draw(self, screen):
        if self.state == "MENU": 
            self.menu.draw()
            return 
        if self.state == "STORY":
            if self.intro_cutscene: self.intro_cutscene.draw()
            return
        if self.state == "WORKSHOP": 
            self.workshop.draw()
            return

        self.parallax.draw(screen)
        self.ground.draw(screen)      
        self.obstacle_manager.draw(screen)
        self.scrap_manager.draw(screen)
        self.enemy_manager.draw(screen)
        if self.companion_manager: self.companion_manager.draw(screen)
        self.combat_system.draw(screen) 
        self.player.draw(screen)
        self.hud.draw(screen, self.player, self.score)
        self.dialogue.draw(screen)

        if self.state == "PAUSED": self._draw_pause_overlay(screen)
        if self.state == "GAMEOVER": self.game_over_screen.draw(self.player.distance, self.score)

    def _draw_pause_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        screen.blit(overlay, (0, 0))
        try:
            font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 72)
        except:
            font = pygame.font.SysFont("Impact", 72)
        text = font.render("PAUSED", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

if __name__ == "__main__":
    engine = Engine()
    game = Game(engine.screen)
    engine.run(game)