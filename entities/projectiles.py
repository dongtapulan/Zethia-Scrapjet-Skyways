import pygame
import random
import math
from settings import WIDTH, HEIGHT, HEAT_RED, LUMEN_GOLD

# --- PLAYER PROJECTILES ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_offset=0):
        super().__init__()
        self.image = pygame.Surface((14, 4), pygame.SRCALPHA)
        # Yellow streak with a slight glow
        pygame.draw.rect(self.image, (255, 50, 50), (0, 0, 14, 4), border_radius=2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 950
        # Horizontal movement with slight spread
        self.vel = pygame.Vector2(self.speed, random.uniform(-25, 25) + angle_offset)
        self.damage = 1

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

# --- ENEMY PROJECTILES ---

class EnemyBullet(pygame.sprite.Sprite):
    """Circular purple bullets fired by Gloombats."""
    def __init__(self, x, y, angle):
        super().__init__()
        self.size = 8
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        # Dark purple core with light purple glow
        pygame.draw.circle(self.image, (200, 50, 255), (self.size, self.size), self.size)
        pygame.draw.circle(self.image, (100, 0, 150), (self.size, self.size), self.size - 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 300
        
        # Calculate velocity based on angle
        rad = math.radians(angle)
        self.vel = pygame.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        # Kill if off-screen
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()

class GloomLaser(pygame.sprite.Sprite):
    """The Bushmonster's horizontal laser beam."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WIDTH, 6), pygame.SRCALPHA)
        self.image.fill((180, 0, 255, 150)) # Transparent purple beam
        pygame.draw.line(self.image, (255, 255, 255), (0, 3), (WIDTH, 3), 2) # White core
        
        self.rect = self.image.get_rect(midleft=(x, y))
        self.timer = 0
        self.duration = 0.5 # Beam stays for half a second

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

# --- MANAGER ---

class ProjectileManager:
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.fire_timer = 0
        self.fire_rate = 0.12

    def fire_machine_gun(self, player, dt):
        self.fire_timer += dt
        if self.fire_timer >= self.fire_rate:
            if player.weight > 0:
                player.weight = max(0, player.weight - 0.4) 
            
            bullet_x = player.rect.right - 5
            bullet_y = player.rect.centery + 8
            self.player_bullets.add(Bullet(bullet_x, bullet_y))
            self.fire_timer = 0
            return True
        return False

    def update(self, dt):
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)

    def draw(self, screen):
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)