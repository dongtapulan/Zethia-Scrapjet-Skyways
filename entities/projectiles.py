import pygame
import random
import math
from settings import WIDTH, HEIGHT, HEAT_RED, LUMEN_GOLD, SFX_MACHINE_GUN, BULLET_SHED_AMOUNT

# --- EXPLOSION EFFECT CLASS ---

class Explosion(pygame.sprite.Sprite):
    """Animated explosion effect for bullet impacts using your PNG and MP3."""
    def __init__(self, x, y):
        super().__init__()
        try:
            # Load the sprite image
            self.full_sheet = pygame.image.load("assets/sprites/explosion_effect.png").convert_alpha()
            self.image = pygame.transform.scale(self.full_sheet, (32, 32))
        except:
            # Fallback if image is missing
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 200, 50), (10, 10), 10)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.duration = 0.15 
        
        # Audio: Load and play the explosion sound immediately
        try:
            self.sfx = pygame.mixer.Sound("assets/sfx/explosion_old.mp3")
            self.sfx.set_volume(0.2)
            self.sfx.play() 
        except:
            pass

    def update(self, dt):
        self.timer += dt
        # Simple shrink animation for the sprite
        scale = 1.0 - (self.timer / self.duration)
        if scale <= 0:
            self.kill()

# --- PLAYER PROJECTILES ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_offset=0):
        super().__init__()
        self.image = pygame.Surface((14, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 50, 50), (0, 0, 14, 4), border_radius=2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 950
        self.vel = pygame.Vector2(self.speed, random.uniform(-25, 25) + angle_offset)
        self.damage = 1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

# --- ENEMY PROJECTILES ---

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.size = 8
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 50, 255), (self.size, self.size), self.size)
        pygame.draw.circle(self.image, (100, 0, 150), (self.size, self.size), self.size - 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 300
        
        rad = math.radians(angle)
        self.vel = pygame.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()

class GloomLaser(pygame.sprite.Sprite):
    """The Bushmonster's horizontal laser beam."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WIDTH, 6), pygame.SRCALPHA)
        self.image.fill((180, 0, 255, 150)) 
        pygame.draw.line(self.image, (255, 255, 255), (0, 3), (WIDTH, 3), 2)
        
        self.rect = self.image.get_rect(midleft=(x, y))
        self.timer = 0
        self.duration = 0.5 

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

# --- MANAGER ---

class ProjectileManager:
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() 
        self.fire_timer = 0
        self.fire_rate = 0.10 
        
        try:
            self.shoot_sfx = pygame.mixer.Sound(SFX_MACHINE_GUN)
            self.shoot_sfx.set_volume(0.15)
        except:
            self.shoot_sfx = None

    def trigger_explosion(self, x, y):
        """Creates a visual and audio explosion at the given coordinates."""
        self.effects.add(Explosion(x, y))

    def fire_machine_gun(self, player, dt):
        if not player.is_alive or player.is_stalled:
            return False

        self.fire_timer += dt
        if self.fire_timer >= self.fire_rate:
            if player.weight > 0:
                player.weight = max(0, player.weight - BULLET_SHED_AMOUNT) 
            
            bullet_x = player.rect.right - 5
            bullet_y = player.rect.centery + 8
            self.player_bullets.add(Bullet(bullet_x, bullet_y))
            
            if self.shoot_sfx:
                self.shoot_sfx.play()

            self.fire_timer = 0
            return True
        return False

    def update(self, dt):
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.effects.update(dt)

    def draw(self, screen):
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.effects.draw(screen)