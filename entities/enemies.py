import pygame
import random
import math
from settings import WIDTH, HEIGHT
from entities.projectiles import EnemyBullet, GloomLaser

class GloomParticle:
    """Purple aura particles for enemies."""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.life = 255
        self.size = random.randint(2, 4)

    def update(self, dt):
        self.pos += self.vel * 20 * dt
        self.life -= 500 * dt

    def draw(self, screen):
        if self.life > 0:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            color = (120, 0, 200, int(max(0, self.life)))
            pygame.draw.circle(s, color, (self.size, self.size), self.size)
            screen.blit(s, self.pos)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, sprite_path, x, y, hp):
        super().__init__()
        try:
            self.image = pygame.image.load(sprite_path).convert_alpha()
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill((100, 0, 100))
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.hp = hp
        self.max_hp = hp
        self.particles = []
        self.explosion_manager = None  

    def take_damage(self, amount):
        self.hp -= amount
        # Visual feedback for damage
        self.pos.x += random.randint(-3, 3)
        
        if self.hp <= 0:
            # We don't call self.die() here because main.py handles 
            # the death logic (score, scrap, etc.) in the collision loop.
            return True
        return False

    def update_aura(self, dt):
        if random.random() < 0.3:
            off_x = random.randint(-15, 15)
            off_y = random.randint(-15, 15)
            self.particles.append(GloomParticle(self.rect.centerx + off_x, self.rect.centery + off_y))
        
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    def draw_aura(self, screen):
        for p in self.particles:
            p.draw(screen)

class GloomBat(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/gloombat.png", x, y, 2)
        self.shoot_timer = 0
        self.speed = 130

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(pygame.time.get_ticks() * 0.005) * 2
        self.rect.center = self.pos
        
        self.shoot_timer += dt
        if self.shoot_timer > 2.5:
            for angle in range(0, 360, 45):
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle)
                proj_manager.enemy_bullets.add(bullet)
            self.shoot_timer = 0

class BushMonster(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/corrupt_bushmonster.png", x, y, 6)
        self.attack_timer = 0
        self.speed = 60

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.pos.x -= self.speed * dt
        self.rect.center = self.pos
        
        self.attack_timer += dt
        if self.attack_timer > 3.5:
            laser = GloomLaser(0, self.rect.centery)
            proj_manager.enemy_bullets.add(laser)
            self.attack_timer = 0

class MonsterSaucer(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/monster_saucer.png", x, y, 4)
        self.speed = 180

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        # Vertical tracking
        if self.rect.centery < player_pos[1]:
            self.pos.y += 120 * dt
        else:
            self.pos.y -= 120 * dt
            
        self.pos.x -= self.speed * dt
        self.rect.center = self.pos

class BlightBeast(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/blight_beast.png", x, y, 40)
        self.speed = 220
        self.timer = 0
        self.glow_timer = 0

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.timer += dt
        self.glow_timer += dt
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(self.timer * 5) * 3
        self.rect.center = self.pos

    def draw_glow(self, screen):
        pulse = (math.sin(self.glow_timer * 8) + 1) * 0.5
        glow_radius = int(35 + (pulse * 15))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        color = (180, 50, 255, int(60 + pulse * 40)) 
        pygame.draw.circle(glow_surf, color, (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius), special_flags=pygame.BLEND_RGB_ADD)

class BlightTitan(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/blight_titan.png", x, y, 500)
        self.speed = 40
        self.attack_timer = 0
        self.angle_offset = 0
        self.is_boss = True 
        self.pos = pygame.Vector2(x, y)

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        
        # Entrance behavior
        if self.pos.x > WIDTH - 250:
            self.pos.x -= self.speed * 3 * dt
        else:
            # Hover movement
            self.pos.y += math.sin(pygame.time.get_ticks() * 0.002) * 1.5
            
        self.rect.center = self.pos

        # Spiral attack pattern
        self.attack_timer += dt
        if self.attack_timer > 0.15: 
            self.angle_offset += 20
            # Fire in a 6-way spiral
            for angle in range(0, 360, 60):
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle + self.angle_offset)
                proj_manager.enemy_bullets.add(bullet)
            self.attack_timer = 0

    def draw_glow(self, screen):
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        radius = int(140 + pulse * 30)
        glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Soft purple boss glow
        pygame.draw.circle(glow_surf, (150, 0, 255, 30), (radius, radius), radius)
        screen.blit(glow_surf, (self.rect.centerx - radius, self.rect.centery - radius), special_flags=pygame.BLEND_RGB_ADD)