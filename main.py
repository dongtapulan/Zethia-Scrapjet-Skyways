import pygame
import sys
import random
from settings import *
from core.engine import Engine
from entities.player import Player
from world.parallax import ParallaxBackground
from entities.scrap import ScrapManager
from entities.enemies import *
from entities.projectiles import ProjectileManager
from world.ground_logic import Ground      
from world.obstacle_gen import ObstacleManager 
from ui.menus import MainMenu, GameOverScreen
from ui.hud import HUD             
from ui.dialogue_box import DialogueBox 

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
        
        # Game Systems
        self.player = None
        self.parallax = None
        self.ground = None         
        self.obstacle_manager = None
        self.scrap_manager = None
        self.enemy_manager = None
        self.projectile_manager = None
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
        self.projectile_manager = ProjectileManager()
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
            elif selection == "Exit":
                pygame.quit()
                sys.exit()
        
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
        
        elif self.state == "PAUSED":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.state = "PLAYING"

    def update(self, dt, flight_input, combat_input):
        if self.state == "MENU":
            self.menu.update(dt)
            return 

        if self.state == "PAUSED":
            return 
        
        if self.state == "GAMEOVER":
            self.game_over_screen.update(dt)
            return

        # --- CORE GAMEPLAY LOGIC ---
        
        # 1. Update World & Interactivity
        scroll_speed = 0 if not self.player.is_alive else 1.0
        self.player.distance += dt * 50 * scroll_speed
        
        # Pass distance to parallax for Day/Night cycle
        self.parallax.update(self.player.distance, dt) 
        
        self.ground.update(dt, self.player.rect, self.player.is_skimming) 
        self.obstacle_manager.update(dt) 
        self.scrap_manager.update(dt, self.player.rect.center)
        
        # 2. Update Player
        self.player.handle_input(flight_input, dt) 
        self.player.update(dt)

        # 3. State Transition
        if not self.player.is_alive and self.player.has_exploded:
            self.state = "GAMEOVER"

        # 4. Combat Logic
        if self.player.is_alive and combat_input["firing"]:
            self.projectile_manager.fire_machine_gun(self.player, dt)

        self.projectile_manager.update(dt)
        self.enemy_manager.update(dt, self.player.rect.center, self.projectile_manager)
        
        # 5. UI & Narrative
        self.hud.update(dt, self.player)     
        self.dialogue.update(dt, self.player) 

        # 6. Collisions
        self._handle_collisions()

        # 7. Update Particles
        for e in self.explosions[:]:
            e.update(dt)
            if e.life <= 0: self.explosions.remove(e)

    def _handle_collisions(self):
        # Player vs Rocks
        rock_collision = pygame.sprite.spritecollide(
            self.player, self.obstacle_manager.obstacles, True, pygame.sprite.collide_mask
        )
        if rock_collision:
            self.player.take_damage(25) 
            self.dialogue.trigger_random_quip("frustration")
            self.projectile_manager.trigger_explosion(self.player.rect.centerx, self.player.rect.centery)

        # Enemy Bullets vs Player
        bullet_hits = pygame.sprite.spritecollide(self.player, self.projectile_manager.enemy_bullets, True)
        for bullet in bullet_hits:
            self.player.take_damage(10)
            self.projectile_manager.trigger_explosion(bullet.rect.centerx, bullet.rect.centery)

        # Player Projectiles vs Enemies
        # Note: This will automatically handle missiles once added to the player_bullets group
        enemy_hits = pygame.sprite.groupcollide(self.enemy_manager.enemies, self.projectile_manager.player_bullets, False, True)
        for enemy, bullets in enemy_hits.items():
            for b in bullets:
                self.projectile_manager.trigger_explosion(b.rect.centerx, b.rect.centery)
                if enemy.take_damage(b.damage):
                    enemy.kill()
                    self.score += 150

        # Scrap Collection
        scrap_hits = pygame.sprite.spritecollide(self.player, self.scrap_manager.scrap_group, True)
        for scrap in scrap_hits:
            self.score += scrap.value
            self.player.weight = min(self.player.max_weight, self.player.weight + scrap.weight_value)
            
            # Placeholder: Check for special Powerup scrap types here later
            # if scrap.type == "MISSILE": ...

    def draw(self, screen):
        if self.state == "MENU":
            self.menu.draw()
            return
        
        # Parallax handles the screen.fill now based on the Day/Night color
        self.parallax.draw(screen)
        
        self.ground.draw(screen)      
        self.obstacle_manager.draw(screen)
        self.scrap_manager.draw(screen)
        
        for e in self.explosions:
            e.draw(screen)
            
        self.enemy_manager.draw(screen)
        self.projectile_manager.draw(screen) 
        self.player.draw(screen)
        
        self.hud.draw(screen, self.player, self.score)
        self.dialogue.draw(screen)

        if self.state == "PAUSED":
            self._draw_pause_overlay(screen)

        if self.state == "GAMEOVER":
            self.game_over_screen.draw(self.player.distance, self.score)

    def _draw_pause_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont("Impact", 72)
        text = font.render("PAUSED", True, WHITE)
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, rect)
        
        small_font = pygame.font.SysFont("Arial", 24)
        hint = small_font.render("Press 'P' to Resume", True, LUMEN_GOLD)
        h_rect = hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        screen.blit(hint, h_rect)

if __name__ == "__main__":
    engine = Engine()
    game = Game(engine.screen)
    engine.run(game)