import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE, SFX_MACHINE_GUN, BULLET_SHED_AMOUNT

# --- EXPLOSION & WAVES ---

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        try:
            full_sheet = pygame.image.load("assets/sprites/explosion_effect.png").convert_alpha()
            size = int(32 * scale)
            self.image = pygame.transform.scale(full_sheet, (size, size))
        except:
            size = int(20 * scale)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 200, 50), (size//2, size//2), size//2)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.duration = 0.2 * scale 

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

class GravityWave(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.radius = 10
        self.max_radius = 400 
        self.speed = 850
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.damage = 100 

    def update(self, dt):
        self.radius += self.speed * dt
        self.image.fill((0, 0, 0, 0))
        progress = self.radius / self.max_radius
        alpha = max(0, int(255 * (1 - progress)))
        
        if self.radius < self.max_radius:
            pygame.draw.circle(self.image, (100, 220, 255, alpha), 
                               (self.max_radius, self.max_radius), int(self.radius), 8)
        
        if self.radius >= self.max_radius:
            self.kill()

# --- PLAYER WEAPONS ---

class FallingBomb(pygame.sprite.Sprite):
    def __init__(self, x, y, manager):
        super().__init__()
        self.manager = manager # Reference to manager for explosion
        try:
            self.image = pygame.image.load("assets/sprites/scraps/gravity_bomb_pickup.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (25, 25))
        except:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (50, 50, 255), (10, 10), 10)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(300, -350) 
        self.gravity = 1000
        self.damage = 50 

    def update(self, dt):
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.rect.center = self.pos

        if self.rect.bottom >= GROUND_LINE:
            self.explode()

    def explode(self):
        # Trigger wave and the sound/visual explosion via manager
        wave = GravityWave(self.pos.x, self.pos.y)
        self.manager.effects.add(wave)
        self.manager.trigger_explosion(self.pos.x, self.pos.y, scale=2.5)
        self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_group):
        super().__init__()
        try:
            self.orig_image = pygame.image.load("assets/sprites/scraps/missile_pickup.png").convert_alpha()
            self.orig_image = pygame.transform.scale(self.orig_image, (35, 18))
        except:
            self.orig_image = pygame.Surface((30, 10))
            self.orig_image.fill((255, 100, 0))
        
        self.image = self.orig_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(400, 0)
        self.enemy_group = enemy_group
        self.damage = 80 
        self.speed = 700
        self.turn_rate = 6.0 
        self.trail_particles = [] 
        self.trail_timer = 0

    def update(self, dt):
        target = self.get_closest_enemy()
        if target:
            target_dir = (pygame.Vector2(target.rect.center) - self.pos).normalize()
            self.vel = self.vel.lerp(target_dir * self.speed, self.turn_rate * dt)
        else:
            self.vel.x += 150 * dt

        self.pos += self.vel * dt
        self.trail_timer += dt
        if self.trail_timer > 0.02:
            self.trail_particles.append({"pos": pygame.Vector2(self.pos), "life": 1.0})
            self.trail_timer = 0

        for p in self.trail_particles[:]:
            p["life"] -= 2.5 * dt
            if p["life"] <= 0: self.trail_particles.remove(p)

        angle = -math.degrees(math.atan2(self.vel.y, self.vel.x))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect(center=self.pos)

        if not (-200 <= self.pos.x <= WIDTH + 200 and -200 <= self.pos.y <= HEIGHT + 200):
            self.kill()

    def get_closest_enemy(self):
        closest = None
        min_dist = 1500
        for enemy in self.enemy_group:
            dist = self.pos.distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                closest = enemy
        return closest

    def draw_trail(self, screen):
        for p in self.trail_particles:
            size = int(p["life"] * 6)
            if size > 0:
                pygame.draw.circle(screen, (200, 200, 200), (int(p["pos"].x), int(p["pos"].y)), size)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((18, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 18, 6), border_radius=3)
        pygame.draw.rect(self.image, (255, 0, 0), (2, 1, 14, 4), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(1200, random.uniform(-10, 10))
        self.damage = 1

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if self.rect.left > WIDTH: self.kill()

# --- ENEMY PROJECTILES ---

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.size = 8
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 50, 255), (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 350
        rad = math.radians(angle)
        self.vel = pygame.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()

class GloomLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WIDTH, 8), pygame.SRCALPHA)
        self.image.fill((180, 0, 255, 100)) 
        pygame.draw.line(self.image, (255, 255, 255), (0, 4), (WIDTH, 4), 3)
        self.rect = self.image.get_rect(midleft=(x, y))
        self.timer = 0
        self.duration = 0.5 

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

# --- PROJECTILE MANAGER ---

class ProjectileManager:
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() 
        self.fire_timer = 0
        self.fire_rate = 0.08 
        
        # Audio setup
        try:
            self.shoot_sfx = pygame.mixer.Sound(SFX_MACHINE_GUN)
            self.shoot_sfx.set_volume(0.15)
            # Load explosion sound correctly
            self.explosion_sfx = pygame.mixer.Sound("assets/sfx/explosion_old.mp3")
            self.explosion_sfx.set_volume(0.3)
        except:
            self.shoot_sfx = None
            self.explosion_sfx = None

    def trigger_explosion(self, x, y, scale=1.0):
        """Creates visual explosion and plays the collision sound."""
        self.effects.add(Explosion(x, y, scale))
        if self.explosion_sfx:
            self.explosion_sfx.play()

    def fire_machine_gun(self, player, dt):
        if not player.is_alive or player.is_stalled: return False
        self.fire_timer += dt
        if self.fire_timer >= self.fire_rate:
            if player.weight > 0:
                player.weight = max(0, player.weight - BULLET_SHED_AMOUNT) 
            self.player_bullets.add(Bullet(player.rect.right, player.rect.centery + 10))
            if self.shoot_sfx: self.shoot_sfx.play()
            self.fire_timer = 0
            return True
        return False

    def launch_missile(self, player, enemy_group):
        self.player_bullets.add(Missile(player.rect.right, player.rect.centery, enemy_group))

    def trigger_gravity_bomb(self, player):
        # Pass self (manager) to the bomb so it can trigger the explosion sound later
        bomb = FallingBomb(player.rect.right, player.rect.centery, self)
        self.player_bullets.add(bomb)

    def update(self, dt):
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.effects.update(dt)

    def draw(self, screen):
        for sprite in self.player_bullets:
            if isinstance(sprite, Missile):
                sprite.draw_trail(screen)
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.effects.draw(screen)