import pygame
import sys
import random
from settings import *
from core.engine import Engine
from entities.player import Player
from world.parallax import ParallaxBackground
from entities.scrap import ScrapManager
from entities.enemies import EnemyManager
from entities.projectiles import ProjectileManager
from ui.menus import MainMenu
from ui.hud import HUD             # New Import
from ui.dialogue_box import DialogueBox # New Import

class ExplosionParticle:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.vel = [random.uniform(-4, 4), random.uniform(-4, 4)]
        self.life = 1.0
        self.color = random.choice([LUMEN_GOLD, (255, 100, 50), (255, 255, 255)])

    def update(self, dt):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 2.0 * dt

    def draw(self, screen):
        if self.life > 0:
            radius = int(self.life * 4)
            if radius > 0:
                pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), radius)

class Game:
    def __init__(self, screen):
        self.screen = screen
        
        # State Machine
        self.state = "MENU"
        self.menu = MainMenu(self.screen)
        
        # Game Systems (initialized as None until Arcade starts)
        self.player = None
        self.parallax = None
        self.scrap_manager = None
        self.enemy_manager = None
        self.projectile_manager = None
        self.hud = None            # Initialize HUD placeholder
        self.dialogue = None       # Initialize Dialogue placeholder
        self.explosions = []
        self.score = 0

    def reset_game(self):
        """Initializes Arcade Mode."""
        self.player = Player()
        self.parallax = ParallaxBackground()
        self.scrap_manager = ScrapManager()
        self.enemy_manager = EnemyManager()
        self.projectile_manager = ProjectileManager()
        self.hud = HUD()            # Create HUD
        self.dialogue = DialogueBox() # Create Dialogue Box
        self.explosions = []
        self.score = 0
        self.state = "PLAYING"
        
        # Trigger an initial welcome quip
        self.dialogue.trigger_random_quip("enemies")

    def handle_event(self, event):
        """Called by Engine for manual event handling."""
        if self.state == "MENU":
            selection = self.menu.handle_input(event)
            if selection == "Arcade Mode":
                self.reset_game()
            elif selection == "Exit":
                pygame.quit()
                sys.exit()
        
        elif self.state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.menu.menu_state = "READY"
                    self.menu.button_alphas = [255] * len(self.menu.options)

    def update(self, dt, flight_input, combat_input):
        """The core update logic called by the Engine."""
        if self.state == "MENU":
            self.menu.update(dt)
            return

        # 1. Update Core World & Player
        self.parallax.update(0, dt)
        self.scrap_manager.update(dt, self.player.rect.center)
        self.player.handle_input(flight_input, dt) 
        self.player.update(dt)

        # 2. Fire Machine Gun
        if combat_input["firing"]:
            self.projectile_manager.fire_machine_gun(self.player, dt)

        # 3. Update Combat & UI Systems
        self.projectile_manager.update(dt)
        self.enemy_manager.update(dt, self.player.rect.center, self.projectile_manager)
        self.hud.update(dt, self.player)     # Update HUD (fades/hints)
        self.dialogue.update(dt, self.player) # Update Dialogue (animations/logic)

        # 4. Collision: Player vs Scrap
        scrap_hits = pygame.sprite.spritecollide(self.player, self.scrap_manager.scrap_group, True)
        for scrap in scrap_hits:
            self.score += scrap.value
            self.player.weight = min(self.player.max_weight, self.player.weight + scrap.weight_value)

        # 5. Collision: Player Bullets vs Enemies
        enemy_hits = pygame.sprite.groupcollide(
            self.enemy_manager.enemies, 
            self.projectile_manager.player_bullets, 
            False, True
        )
        for enemy, bullets in enemy_hits.items():
            # Trigger a quip when starting combat randomly
            if random.random() < 0.1: self.dialogue.trigger_random_quip("enemies")
            
            for b in bullets:
                for _ in range(5):
                    self.explosions.append(ExplosionParticle(b.rect.centerx, b.rect.centery))
                if enemy.take_damage(b.damage):
                    enemy.kill()
                    self.score += 150

        # 6. Collision: Enemy Projectiles vs Player
        if pygame.sprite.spritecollide(self.player, self.projectile_manager.enemy_bullets, True):
            self.player.weight = min(self.player.max_weight, self.player.weight + 15)
            # Huey complains when hit
            if random.random() < 0.3: self.dialogue.trigger_random_quip("frustration")

        # 7. Update Visual Effects
        for e in self.explosions[:]:
            e.update(dt)
            if e.life <= 0:
                self.explosions.remove(e)

    def draw(self, screen):
        if self.state == "MENU":
            self.menu.draw()
            return
        
        # Base Background
        screen.fill(SKY_BLUE)

        # Layered Drawing
        self.parallax.draw(screen)
        self.scrap_manager.draw(screen)
        
        for e in self.explosions:
            e.draw(screen)
            
        self.enemy_manager.draw(screen)
        self.projectile_manager.draw(screen)
        self.player.draw(screen)
        
        # Top-Level UI (Drawn last to be on top)
        self.hud.draw(screen, self.player, self.score)
        self.dialogue.draw(screen)

if __name__ == "__main__":
    engine = Engine()
    game = Game(engine.screen)
    engine.run(game)