import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE, SFX_MACHINE_GUN, BULLET_SHED_AMOUNT

# --- SPECIAL EFFECTS ---

class LightningBolt(pygame.sprite.Sprite):
    """Visual effect for Tine's Lightning."""
    def __init__(self, start_pos, end_pos):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.points = self._generate_lightning_points(start_pos, end_pos)
        self.timer = 0
        self.duration = 0.15
        self.color = (150, 230, 255)

    def _generate_lightning_points(self, start, end):
        points = [start]
        start_vec = pygame.Vector2(start)
        end_vec = pygame.Vector2(end)
        dist = start_vec.distance_to(end_vec)
        segments = max(2, int(dist / 20))
        for i in range(1, segments):
            progress = i / segments
            base_x = start[0] + (end[0] - start[0]) * progress
            base_y = start[1] + (end[1] - start[1]) * progress
            offset = 15
            points.append((base_x + random.randint(-offset, offset), 
                           base_y + random.randint(-offset, offset)))
        points.append(end)
        return points

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

    def draw_custom(self, screen):
        alpha = int(255 * (1 - self.timer / self.duration))
        color = (*self.color, alpha)
        if len(self.points) > 1:
            pygame.draw.lines(screen, color, False, self.points, 4)
            pygame.draw.lines(screen, (self.color[0], self.color[1], self.color[2], alpha // 2), False, self.points, 8)

class LaserBeam(pygame.sprite.Sprite):
    """Visual effect for Red's Laser."""
    def __init__(self, start_pos, end_pos):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.start = start_pos
        self.end = end_pos
        self.timer = 0
        self.duration = 0.05 

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

    def draw_custom(self, screen):
        width = random.randint(6, 12)
        pygame.draw.line(screen, (255, 50, 50), self.start, self.end, width)
        pygame.draw.line(screen, (255, 255, 255), self.start, self.end, width // 3)

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
        self.damage = 10 # Added: Fixes the BlightTitan Phase 3 error
        rad = math.radians(angle)
        self.vel = pygame.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()

class GloomLaser(pygame.sprite.Sprite):
    """The laser class for enemies."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WIDTH, 12), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midleft=(x, y))
        self.timer = 0
        self.duration = 0.6 
        self.start_pos = (x, y)
        self.end_pos = (0, y) 
        self.damage = 15 # Added damage attribute

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

    def draw_custom(self, screen):
        alpha = int(150 + math.sin(pygame.time.get_ticks() * 0.02) * 105)
        width = random.randint(4, 8)
        pygame.draw.line(screen, (180, 0, 255, alpha), self.start_pos, self.end_pos, width)
        pygame.draw.line(screen, (255, 255, 255, alpha), self.start_pos, self.end_pos, 2)

# --- EXPLOSION & WAVES ---

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        try:
            full_sheet = pygame.image.load("assets/sprites/explosion_effect.png").convert_alpha()
            size = int(32 * scale)
            self.image = pygame.transform.scale(full_sheet, (size, size))
        except:
            size = int(40 * scale)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 200, 50, 200), (size//2, size//2), size//2)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.duration = 0.2 * scale 

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.kill()

class GravityWave(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_group):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.radius = 10
        self.max_radius = 400 
        self.speed = 850
        self.enemy_group = enemy_group
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.damage = 100 
        self.hit_enemies = set()

    def update(self, dt):
        self.radius += self.speed * dt
        self.image.fill((0, 0, 0, 0))
        progress = self.radius / self.max_radius
        alpha = max(0, int(255 * (1 - progress)))
        
        if self.radius < self.max_radius:
            pygame.draw.circle(self.image, (100, 220, 255, alpha), 
                               (self.max_radius, self.max_radius), int(self.radius), 8)
            
            for enemy in self.enemy_group:
                if enemy not in self.hit_enemies:
                    if self.pos.distance_to(enemy.rect.center) <= self.radius:
                        enemy.take_damage(self.damage)
                        self.hit_enemies.add(enemy)
        else:
            self.kill()

# --- PLAYER WEAPONS ---

class FallingBomb(pygame.sprite.Sprite):
    def __init__(self, x, y, manager, enemy_group):
        super().__init__()
        self.manager = manager 
        self.enemy_group = enemy_group
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

    def update(self, dt):
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if self.rect.bottom >= GROUND_LINE:
            self.explode()

    def explode(self):
        wave = GravityWave(self.pos.x, self.pos.y, self.enemy_group)
        self.manager.effects.add(wave)
        self.manager.trigger_explosion(self.pos.x, self.pos.y, scale=2.5)
        self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_group):
        super().__init__()
        self.enemy_group = enemy_group
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
        self.damage = 80 
        self.speed = 750
        self.turn_rate = 7.0 
        self.trail_particles = [] 
        self.trail_timer = 0

    def update(self, dt):
        target = self.get_closest_enemy()
        if target:
            diff = pygame.Vector2(target.rect.center) - self.pos
            if diff.length() > 0:
                target_dir = diff.normalize()
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

        if not (-200 <= self.pos.x <= WIDTH + 500):
            self.kill()

    def get_closest_enemy(self):
        if not self.enemy_group: return None
        closest = None
        min_dist = 1000
        for enemy in self.enemy_group:
            dist = self.pos.distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                closest = enemy
        return closest

    def draw_trail(self, screen):
        for p in self.trail_particles:
            size = int(p["life"] * 8)
            color = (255, 150, 50) if p["life"] > 0.5 else (100, 100, 100)
            if size > 0:
                pygame.draw.circle(screen, color, (int(p["pos"].x), int(p["pos"].y)), size)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_group):
        super().__init__()
        self.enemy_group = enemy_group
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 100), (0, 0, 20, 8), border_radius=4)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(1400, random.uniform(-15, 15))
        self.damage = 4

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if self.rect.left > WIDTH: self.kill()

# --- PROJECTILE MANAGER ---

class ProjectileManager:
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() 
        self.fire_timer = 0
        self.fire_rate = 0.08 
        
        try:
            self.shoot_sfx = pygame.mixer.Sound(SFX_MACHINE_GUN)
            self.shoot_sfx.set_volume(0.15)
            # Load the hit SFX
            self.hit_sfx = pygame.mixer.Sound("assets/sfx/explosion_old.mp3")
            self.hit_sfx.set_volume(0.2)
        except:
            self.shoot_sfx = None
            self.hit_sfx = None

    def trigger_explosion(self, x, y, scale=1.0):
        self.effects.add(Explosion(x, y, scale))

    def spawn_lightning(self, start_pos, targets):
        current_start = start_pos
        for target in targets:
            end_pos = target.rect.center
            self.effects.add(LightningBolt(current_start, end_pos))
            target.take_damage(50)
            self.trigger_explosion(end_pos[0], end_pos[1], scale=0.8)
            current_start = end_pos 

    def process_laser_beam(self, player, enemies):
        start_pos = (player.rect.right, player.rect.centery + 5)
        end_pos = (WIDTH, player.rect.centery + 5) 
        self.effects.add(LaserBeam(start_pos, end_pos))
        
        beam_rect = pygame.Rect(start_pos[0], start_pos[1] - 15, WIDTH - start_pos[0], 30)
        for enemy in enemies:
            if beam_rect.colliderect(enemy.rect):
                enemy.take_damage(5) 
                if random.random() < 0.1: 
                    self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, scale=0.3)
                    if self.hit_sfx: self.hit_sfx.play()

    def fire_machine_gun(self, player, enemy_group, dt):
        if not player.is_alive or player.is_stalled: return False
        self.fire_timer += dt
        if self.fire_timer >= self.fire_rate:
            if player.weight > 0:
                player.weight = max(0, player.weight - BULLET_SHED_AMOUNT) 
            self.player_bullets.add(Bullet(player.rect.right, player.rect.centery + 10, enemy_group))
            if self.shoot_sfx: self.shoot_sfx.play()
            self.fire_timer = 0
            return True
        return False

    def launch_missile(self, player, enemy_group):
        self.player_bullets.add(Missile(player.rect.right, player.rect.centery, enemy_group))

    def trigger_gravity_bomb(self, player, enemy_group):
        bomb = FallingBomb(player.rect.right, player.rect.centery, self, enemy_group)
        self.player_bullets.add(bomb)

    def update(self, dt):
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.effects.update(dt)
        
        for bullet in self.player_bullets:
            if isinstance(bullet, (Bullet, Missile)):
                hit_enemies = pygame.sprite.spritecollide(bullet, bullet.enemy_group, False)
                for enemy in hit_enemies:
                    enemy.take_damage(bullet.damage)
                    self.trigger_explosion(bullet.rect.centerx, bullet.rect.centery, scale=0.5)
                    # Play the hit sound effect when a bullet/missile connects
                    if self.hit_sfx:
                        self.hit_sfx.play()
                    bullet.kill()

    def draw(self, screen):
        for sprite in self.player_bullets:
            if isinstance(sprite, Missile):
                sprite.draw_trail(screen)
        
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        
        for effect in self.effects:
            if hasattr(effect, 'draw_custom'):
                effect.draw_custom(screen)
            else:
                screen.blit(effect.image, effect.rect)