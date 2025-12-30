import pygame
import sys
import random
from settings import *
from core.engine import Engine
from entities.player import Player
from world.parallax import ParallaxBackground
from entities.scrap import ScrapManager
from entities.enemies import EnemyManager
from world.ground_logic import Ground       
from world.obstacle_gen import ObstacleManager 
from ui.menus import MainMenu, GameOverScreen
from ui.hud import HUD             
from ui.dialogue_box import DialogueBox 

# --- NEW SYSTEMS IMPORTS ---
from systems.combat_system import CombatSystem
from systems.heat_system import HeatSystem
from systems.upgrade_manager import UpgradeManager
from ui.workshop_menu import WorkshopMenu # <--- Added Workshop Import
from entities.projectiles import GravityWave

class ExplosionParticle:
    """Fallback simple particles for non-bullet impacts (ambient smoke)."""
    def __init__(self, x, y, color=LUMEN_GOLD):
        self.pos = [x, y]
        self.vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.life = 1.0
        self.color = color

    def update(self, dt):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 2.0 * dt

    def draw(self, screen):
        if self.life > 0:
            radius = int(self.life * 6)
            if radius > 0:
                pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), radius)

class Game:
    def __init__(self, screen):
        self.screen = screen
        
        # State Machine
        self.state = "MENU"
        self.menu = MainMenu(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        # Persistent Systems (Loaded once)
        self.upgrade_manager = UpgradeManager()
        # Initialize the Workshop Menu
        self.workshop = WorkshopMenu(self.screen, self.upgrade_manager) # <--- Added Workshop instance
        
        # Game Entities & Managers
        self.player = None
        self.parallax = None
        self.ground = None          
        self.obstacle_manager = None
        self.scrap_manager = None
        self.enemy_manager = None
        
        # Modular Combat Systems
        self.combat_system = None
        self.heat_system = None
        
        self.hud = None             
        self.dialogue = None       
        self.explosions = [] 
        self.score = 0

    def reset_game(self):
        """Initializes Arcade Mode."""
        self.player = Player()
        self.parallax = ParallaxBackground()
        self.ground = Ground()      
        self.obstacle_manager = ObstacleManager() 
        self.scrap_manager = ScrapManager()
        self.enemy_manager = EnemyManager()
        
        # Initialize Combat & Heat
        self.combat_system = CombatSystem()
        self.heat_system = HeatSystem()
        
        # Link systems to player
        self.player.heat_system = self.heat_system 
        self.player.combat_system = self.combat_system 
        
        # APPLY PERMANENT UPGRADES FROM WORKSHOP
        self.upgrade_manager.apply_all_upgrades(self.player)
        
        self.hud = HUD()            
        self.dialogue = DialogueBox() 
        self.explosions = []
        self.score = 0
        self.state = "PLAYING"
        
        self.dialogue.trigger_random_quip("enemies")

    def handle_event(self, event):
        if self.state == "MENU":
            selection = self.menu.handle_input(event)
            if selection == "Arcade Mode":
                self.reset_game()
            elif selection == "Workshop": # <--- Link to Workshop
                self.state = "WORKSHOP"
            elif selection == "Exit":
                pygame.quit()
                sys.exit()
        
        elif self.state == "WORKSHOP":
            # Handle Workshop Input
            result = self.workshop.handle_input(event)
            if result == "BACK":
                self.state = "MENU"
                self.menu.menu_state = "READY"
            elif result in self.upgrade_manager.stats:
                # Attempt to buy the upgrade (no live player needed here, 
                # stats are applied during reset_game)
                self.upgrade_manager.attempt_upgrade(result, None)

        elif self.state == "GAMEOVER":
            selection = self.game_over_screen.handle_input(event)
            if selection == "Retry":
                self.reset_game()
            elif selection == "Main Menu":
                self.state = "MENU"
                self.menu.menu_state = "READY"
            elif selection == "Exit":
                pygame.quit()
                sys.exit()

        elif self.state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.state = "PAUSED"
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.menu.menu_state = "READY"
                
                if event.key == pygame.K_r and self.player.missiles > 0:
                    self.player.missiles -= 1
                    self.combat_system.selected_weapon = "missile"
                    self.combat_system.fire(self.player, self.enemy_manager.enemies, 0)
                
                if event.key == pygame.K_g and self.player.bombs > 0:
                    self.player.bombs -= 1
                    self.combat_system.manager.trigger_gravity_bomb(self.player)
        
        elif self.state == "PAUSED":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.state = "PLAYING"

    def update(self, dt, flight_input, combat_input):
        if self.state == "MENU":
            self.menu.update(dt)
            return 

        if self.state == "WORKSHOP": # <--- Update Workshop Particles
            self.workshop.update(dt)
            return

        if self.state == "PAUSED":
            return 
        
        if self.state == "GAMEOVER":
            self.game_over_screen.update(dt)
            return

        # --- CORE GAMEPLAY ---
        scroll_speed = 0 if not self.player.is_alive else 1.0
        self.player.distance += dt * 50 * scroll_speed
        
        self.parallax.update(self.player.distance, dt) 
        self.ground.update(dt, self.player.rect, self.player.is_skimming) 
        self.obstacle_manager.update(dt) 
        self.scrap_manager.update(dt, self.player.rect.center)
        
        self.player.handle_input(flight_input, dt) 
        self.player.update(dt)

        if not self.player.is_alive and self.player.has_exploded:
            if self.state == "PLAYING":
                earned = self.upgrade_manager.convert_score_to_bolts(self.score)
                self.state = "GAMEOVER"

        is_firing = False
        if self.player.is_alive and combat_input["firing"]:
            self.combat_system.selected_weapon = "machine_gun"
            heat_added = self.combat_system.fire(self.player, self.enemy_manager.enemies, dt)
            if heat_added > 0:
                self.heat_system.add_heat(heat_added)
                is_firing = True

        self.heat_system.update(dt, is_firing)
        self.combat_system.update(dt)
        self.enemy_manager.update(dt, self.player.rect.center, self.combat_system.manager)
        
        self.hud.update(dt, self.player)     
        self.dialogue.update(dt, self.player) 
        self._handle_collisions()

        for e in self.explosions[:]:
            e.update(dt)
            if e.life <= 0: self.explosions.remove(e)

    def _handle_collisions(self):
        pm = self.combat_system.manager
        rock_collision = pygame.sprite.spritecollide(self.player, self.obstacle_manager.obstacles, True, pygame.sprite.collide_mask)
        if rock_collision:
            self.player.take_damage(25) 
            pm.trigger_explosion(self.player.rect.centerx, self.player.rect.centery)

        bullet_hits = pygame.sprite.spritecollide(self.player, pm.enemy_bullets, True)
        for bullet in bullet_hits:
            self.player.take_damage(10)
            pm.trigger_explosion(bullet.rect.centerx, bullet.rect.centery)

        enemy_hits = pygame.sprite.groupcollide(self.enemy_manager.enemies, pm.player_bullets, False, False)
        for enemy, bullets in enemy_hits.items():
            for b in bullets:
                if not isinstance(b, GravityWave): 
                    pm.trigger_explosion(b.rect.centerx, b.rect.centery)
                    b.kill()
                if enemy.take_damage(b.damage):
                    enemy.kill()
                    self.score += 150

        scrap_hits = pygame.sprite.spritecollide(self.player, self.scrap_manager.scrap_group, True)
        for scrap in scrap_hits:
            self.score += scrap.value
            self.player.weight = min(self.player.max_weight, self.player.weight + scrap.weight_value)
            if scrap.scrap_type == "missile":
                self.player.missiles = min(self.player.max_missiles, self.player.missiles + 5)
            elif scrap.scrap_type == "bomb":
                self.player.bombs = min(self.player.max_bombs, self.player.bombs + 2)

    def draw(self, screen):
        if self.state == "MENU":
            self.menu.draw()
            return 
        
        if self.state == "WORKSHOP": # <--- Draw Workshop
            self.workshop.draw()
            return

        self.parallax.draw(screen)
        self.ground.draw(screen)      
        self.obstacle_manager.draw(screen)
        self.scrap_manager.draw(screen)
        
        for e in self.explosions: e.draw(screen)
            
        self.enemy_manager.draw(screen)
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
        font = pygame.font.SysFont("Impact", 72)
        text = font.render("PAUSED", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

if __name__ == "__main__":
    engine = Engine()
    game = Game(engine.screen)
    engine.run(game)