import pygame
import random
import math
from settings import WIDTH, HEIGHT
from entities.projectiles import EnemyBullet, GloomLaser

class GloomParticle:
    """Purple aura particles for enemies."""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        # Random drift for the aura
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.life = 255
        self.size = random.randint(2, 4)

    def update(self, dt):
        self.pos += self.vel * 20 * dt
        self.life -= 500 * dt # Fades out quickly

    def draw(self, screen):
        if self.life > 0:
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            # Dark purple core to light purple edge
            color = (120, 0, 200, int(self.life))
            pygame.draw.circle(s, color, (self.size, self.size), self.size)
            screen.blit(s, self.pos)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, sprite_path, x, y, hp):
        super().__init__()
        try:
            self.image = pygame.image.load(sprite_path).convert_alpha()
        except:
            # Fallback if image is missing
            self.image = pygame.Surface((40, 40))
            self.image.fill((100, 0, 100))
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.hp = hp
        self.particles = []

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

    def update_aura(self, dt):
        # Spawn new particles randomly around the sprite
        if random.random() < 0.4:
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
        # Wave movement
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(pygame.time.get_ticks() * 0.005) * 2
        self.rect.center = self.pos
        
        # Shoot 8-way circular burst
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
        
        # Horizontal Laser Attack
        self.attack_timer += dt
        if self.attack_timer > 3.5:
            laser = GloomLaser(0, self.rect.centery) # Spans across screen
            proj_manager.enemy_bullets.add(laser)
            self.attack_timer = 0

class MonsterSaucer(Enemy):
    def __init__(self, x, y):
        super().__init__("assets/sprites/enemies/monster_saucer.png", x, y, 4)
        self.speed = 180

    def update(self, dt, player_pos, proj_manager):
        self.update_aura(dt)
        # Aggressive Distraction: Glides toward player's Y level
        if self.rect.centery < player_pos[1]:
            self.pos.y += 100 * dt
        else:
            self.pos.y -= 100 * dt
            
        self.pos.x -= self.speed * dt
        self.rect.center = self.pos

class EnemyManager:
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_delay = 3.0 # Spawns enemy every 3 seconds

    def spawn(self):
        y = random.randint(100, HEIGHT - 100)
        choice = random.random()
        
        if choice < 0.5:
            self.enemies.add(GloomBat(WIDTH + 50, y))
        elif choice < 0.8:
            self.enemies.add(MonsterSaucer(WIDTH + 50, y))
        else:
            self.enemies.add(BushMonster(WIDTH + 50, y))

    def update(self, dt, player_pos, proj_manager):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn()
            self.spawn_timer = 0
            # Slowly speed up spawning over time
            self.spawn_delay = max(1.2, self.spawn_delay - 0.05)
            
        for enemy in self.enemies:
            # Note: We pass the proj_manager so enemies can add bullets to its groups
            enemy.update(dt, player_pos, proj_manager)
            if enemy.rect.right < -100:
                enemy.kill()

    def draw(self, screen):
        # Draw aura first so it's behind the enemy sprite
        for enemy in self.enemies:
            enemy.draw_aura(screen)
        self.enemies.draw(screen)