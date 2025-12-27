import pygame
import random
from settings import WIDTH, HEAT_RED, LUMEN_GOLD

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_offset=0):
        super().__init__()
        # Visuals: A small glowing streak
        self.image = pygame.Surface((12, 4), pygame.SRCALPHA)
        self.image.fill((255, 255, 100)) # Bright yellow
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        
        # Velocity: Fast horizontal movement with a tiny bit of spread
        self.speed = 900
        self.vel = pygame.Vector2(self.speed, random.uniform(-20, 20) + angle_offset)
        
        self.damage = 1

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        # Kill if it leaves the screen
        if self.rect.left > WIDTH:
            self.kill()

class ProjectileManager:
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.fire_timer = 0
        self.fire_rate = 0.12  # Seconds between shots (Fast!)

    def fire_machine_gun(self, player, dt):
        """Logic for firing the main gun."""
        self.fire_timer += dt
        
        if self.fire_timer >= self.fire_rate:
            # --- SCRAP AMMO LOGIC ---
            # Every shot costs a tiny bit of weight, helping Huey stay light!
            if player.weight > 0:
                player.weight = max(0, player.weight - 0.5) 
            
            # Position bullet at the front of Huey's gun
            bullet_x = player.rect.right - 10
            bullet_y = player.rect.centery + 10 # Offset slightly for the nose gun
            
            new_bullet = Bullet(bullet_x, bullet_y)
            self.player_bullets.add(new_bullet)
            
            self.fire_timer = 0
            return True # Signal that a shot was fired (for sound effects later)
        return False

    def update(self, dt):
        self.player_bullets.update(dt)

    def draw(self, screen):
        self.player_bullets.draw(screen)