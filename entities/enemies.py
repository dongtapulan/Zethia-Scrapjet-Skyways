import pygame
import random
import math
from settings import *
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
        self.is_boss = False

    def take_damage(self, amount):
        self.hp -= amount
        # Small visual flinch
        self.pos.x += random.randint(-2, 2)
        return self.hp <= 0

    def update_aura(self, dt):
        if random.random() < 0.3:
            off_x = random.randint(-15, 15)
            off_y = random.randint(-15, 15)
            self.particles.append(GloomParticle(self.rect.centerx + off_x, self.rect.centery + off_y))
        
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)

    def draw_aura(self, screen):
        for p in self.particles: p.draw(screen)

class GloomBat(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/gloombat.png", x, y, 2)
        self.shoot_timer = 0
        self.speed = 140

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(pygame.time.get_ticks() * 0.005) * 2
        self.rect.center = self.pos
        
        self.shoot_timer += dt
        if self.shoot_timer > 3.0:
            angle_to_player = math.degrees(math.atan2(player_pos[1] - self.rect.centery, player_pos[0] - self.rect.centerx))
            for spread in [-20, 0, 20]:
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle_to_player + spread)
                proj_manager.enemy_bullets.add(bullet)
            self.shoot_timer = 0

class BushMonster(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/corrupt_bushmonster.png", x, y, 8)
        self.attack_timer = 0
        self.speed = 50
        self.is_charging = False

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.pos.x -= self.speed * dt
        self.rect.center = self.pos
        
        self.attack_timer += dt
        if self.attack_timer > 2.5: self.is_charging = True
            
        if self.attack_timer > 3.5:
            laser = GloomLaser(0, self.rect.centery)
            proj_manager.enemy_bullets.add(laser)
            self.attack_timer = 0
            self.is_charging = False

    def draw_charge(self, screen):
        if self.is_charging:
            alpha = int(100 + math.sin(pygame.time.get_ticks() * 0.02) * 50)
            warning_surf = pygame.Surface((WIDTH, 4), pygame.SRCALPHA)
            pygame.draw.line(warning_surf, (255, 0, 0, alpha), (0, 2), (WIDTH, 2), 2)
            screen.blit(warning_surf, (0, self.rect.centery - 2))

class MonsterSaucer(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/monster_saucer.png", x, y, 5)
        self.speed = 200 
        self.sin_timer = random.random() * 10

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.sin_timer += dt * 5
        self.pos.y += math.sin(self.sin_timer) * 3
        self.pos.x -= self.speed * dt
        self.rect.center = self.pos

class BlightBeast(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/blight_beast.png", x, y, 40)
        self.speed = 240
        self.timer = 0
        self.glow_timer = 0

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.timer += dt
        self.glow_timer += dt
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(self.timer * 5) * 4
        self.rect.center = self.pos

    def draw_glow(self, screen):
        pulse = (math.sin(self.glow_timer * 8) + 1) * 0.5
        glow_radius = int(40 + (pulse * 20))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (180, 50, 255, 50), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius), special_flags=pygame.BLEND_RGB_ADD)

class BlightTitan(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/blight_titan.png", x, y, 800)
        self.speed = 45
        self.attack_timer = 0
        self.angle_offset = 0
        self.is_boss = True 
        self.phase = 1 
        
        try:
            self.img_normal = pygame.image.load("assets/sprites/enemies/blight_titan.png").convert_alpha()
            self.img_damaged = pygame.image.load("assets/sprites/enemies/blight_titan_damaged.png").convert_alpha()
            self.img_enraged = pygame.image.load("assets/sprites/enemies/blight_titan_enraged.png").convert_alpha()
        except:
            self.img_normal = self.image
            self.img_damaged = self.image
            self.img_enraged = self.image

        self.is_transforming = False
        self.transition_timer = 0
        self.aura_timer = 0
        
        try:
            self.snd_shoot = pygame.mixer.Sound("assets/sfx/titan_shoot.mp3")
            self.snd_lightning = pygame.mixer.Sound("assets/sfx/tine_lightning.mp3")
            self.snd_phase = pygame.mixer.Sound("assets/sfx/titan_roar.mp3")
            self.snd_shoot.set_volume(0.3)
        except: self.snd_shoot = self.snd_lightning = self.snd_phase = None

    def take_damage(self, amount):
        if self.is_transforming: return False
        
        old_hp_percent = self.hp / self.max_hp
        self.hp -= amount
        new_hp_percent = self.hp / self.max_hp

        if old_hp_percent > 0.5 and new_hp_percent <= 0.5:
            self.trigger_transition(2, self.img_damaged)
        elif old_hp_percent > 0.3 and new_hp_percent <= 0.3:
            self.trigger_transition(3, self.img_enraged)

        return self.hp <= 0

    def trigger_transition(self, next_phase, next_img):
        self.phase = next_phase
        self.image = next_img
        self.is_transforming = True
        self.transition_timer = 2.0
        if self.snd_phase: self.snd_phase.play()

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        self.aura_timer += dt
        
        if self.is_transforming:
            self.transition_timer -= dt
            self.pos.x += random.randint(-4, 4)
            if self.transition_timer <= 0: self.is_transforming = False
            self.rect.center = self.pos
            return 

        # Entrance Movement
        if self.pos.x > WIDTH - 350:
            self.pos.x -= self.speed * 4 * dt
        else:
            # Hover Movement
            amp = 1.0 if self.phase < 3 else 2.5
            self.pos.y += math.sin(pygame.time.get_ticks() * 0.0015) * amp
            
        self.rect.center = self.pos

        # Attack Patterns
        self.attack_timer += dt
        if self.phase == 1 and self.attack_timer > 0.35:
            self.fire_spiral(proj_manager, 4, 15)
        elif self.phase == 2 and self.attack_timer > 0.28:
            self.fire_spiral(proj_manager, 5, 22)
            if random.random() < 0.01: self.fire_lightning(proj_manager)
        elif self.phase == 3 and self.attack_timer > 0.22:
            self.fire_spiral(proj_manager, 6, 30)
            if random.random() < 0.04: self.fire_lightning(proj_manager)

    def fire_spiral(self, proj_manager, count, rot_speed):
        self.angle_offset += rot_speed
        for i in range(count):
            angle = (i * (360 // count)) + self.angle_offset
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle)
            # Enraged damage boost
            if self.phase == 3 and hasattr(bullet, 'damage'):
                bullet.damage *= 1.3 
            proj_manager.enemy_bullets.add(bullet)
        if self.snd_shoot: self.snd_shoot.play()
        self.attack_timer = 0

    def fire_lightning(self, proj_manager):
        lightning = GloomLaser(0, self.rect.centery)
        proj_manager.enemy_bullets.add(lightning)
        if self.snd_lightning: self.snd_lightning.play()

    def draw_aura(self, screen):
        pulse = (math.sin(self.aura_timer * 4) + 1) * 0.5
        colors = [(100, 0, 255), (0, 80, 255), (60, 0, 120)]
        
        for i, col in enumerate(colors):
            radius = int((170 + (i * 35)) + pulse * 25)
            alpha = int(35 - (i * 10))
            if self.is_transforming: 
                radius += 60
                alpha += 30
            
            aura_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*col, alpha), (radius, radius), radius)
            screen.blit(aura_surf, (self.rect.centerx - radius, self.rect.centery - radius), special_flags=pygame.BLEND_RGB_ADD)

    def draw_health_bar(self, screen):
        bar_width = 600
        x = (WIDTH - bar_width) // 2
        y = 30
        pygame.draw.rect(screen, (40, 10, 50), (x - 4, y - 4, bar_width + 8, 28))
        
        fill = (self.hp / self.max_hp) * bar_width
        col = (200, 0, 255) if self.phase == 1 else (100, 100, 255) if self.phase == 2 else (255, 50, 50)
        
        pygame.draw.rect(screen, col, (x, y, fill, 20))
        glow = pygame.Surface((bar_width, 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 255, 50), (0, 0, fill, 10))
        screen.blit(glow, (x, y))

    def draw_glow(self, screen):
        pass