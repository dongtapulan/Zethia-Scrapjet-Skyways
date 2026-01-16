import pygame
import random
import math
from settings import *

class SplashParticle:
    def __init__(self, x, y, is_astral=False):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-150, -300), random.uniform(-30, -80))
        self.life = 1.0
        self.decay = random.uniform(1.5, 3.0)
        
        if is_astral:
            self.color = random.choice([(130, 50, 255), (75, 0, 130), (200, 150, 255)])
        else:
            self.color = random.choice([(200, 230, 255), (255, 255, 255), (100, 150, 255)])

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= self.decay * dt

    def draw(self, screen):
        size = int(self.life * 6)
        if size > 0:
            glow = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, 50), (size*1.5, size*1.5), size*1.5)
            screen.blit(glow, glow.get_rect(center=(int(self.pos.x), int(self.pos.y))), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)

class CloudMist:
    """Soft rolling clouds that sit on the ground level."""
    def __init__(self):
        self.reset()
        self.x = random.randint(0, WIDTH) # Initial random spread

    def reset(self):
        self.x = WIDTH + random.randint(50, 500)
        self.y = GROUND_LINE - random.randint(10, 40)
        self.size_w = random.randint(150, 400)
        self.size_h = random.randint(40, 100)
        self.speed = random.uniform(100, 250)
        self.alpha = random.randint(40, 100)

    def update(self, dt):
        self.x -= self.speed * dt
        if self.x < -self.size_w:
            self.reset()

    def draw(self, screen):
        mist_surf = pygame.Surface((self.size_w, self.size_h), pygame.SRCALPHA)
        # Indigo-tinted white for the astral vibe
        pygame.draw.ellipse(mist_surf, (220, 230, 255, self.alpha), (0, 0, self.size_w, self.size_h))
        screen.blit(mist_surf, (self.x, self.y))

class Ground:
    def __init__(self):
        self.surface_y = GROUND_LINE
        
        try:
            self.image = pygame.image.load("assets/backgrounds/ground.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.image.get_width(), GROUND_HEIGHT))
        except:
            self.image = pygame.Surface((WIDTH, GROUND_HEIGHT))
            self.image.fill((20, 20, 40)) 
            
        self.width = self.image.get_width()
        self.scroll = 0
        self.particles = []
        self.splash_timer = 0
        
        self.streaks = []
        for _ in range(10):
            self.streaks.append({'x': random.randint(0, WIDTH), 'y': random.randint(2, GROUND_HEIGHT-2), 'w': random.randint(40, 100)})

        # New: Sea of Clouds system
        self.mist_layers = [CloudMist() for _ in range(6)]

    def update(self, dt, player_rect, is_skimming):
        self.scroll = (self.scroll + (PLAYER_SPEED * 1.2) * dt) % self.width

        # 1. Update Mist
        for mist in self.mist_layers:
            mist.update(dt)

        # 2. Skimming Logic
        if is_skimming:
            self.splash_timer += dt
            if self.splash_timer > 0.03: 
                spawn_x = player_rect.centerx - 20
                spawn_y = self.surface_y + random.randint(0, 8)
                self.particles.append(SplashParticle(spawn_x, spawn_y, is_astral=True))
                self.splash_timer = 0

        # 3. Update Streaks
        for s in self.streaks:
            s['x'] -= (PLAYER_SPEED * 1.5) * dt
            if s['x'] < -s['w']:
                s['x'] = WIDTH + random.randint(10, 100)
                s['y'] = random.randint(5, GROUND_HEIGHT - 10)

        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    def check_crash(self, player):
        if player.rect.bottom >= self.surface_y and player.physics.velocity_y > 15:
            for _ in range(15): # More particles for a heavy crash
                self.particles.append(SplashParticle(player.rect.centerx, self.surface_y))
            return True
        return False

    def draw(self, screen):
        # 1. Main Ground Texture
        tiles_needed = (WIDTH // self.width) + 2
        for i in range(tiles_needed):
            x_pos = (i * self.width) - self.scroll
            screen.blit(self.image, (x_pos, self.surface_y))
        
        # 2. Draw Mist (Behind the player/splashes but over the ground)
        for mist in self.mist_layers:
            mist.draw(screen)

        # 3. Draw Speed Streaks
        for s in self.streaks:
            streak_rect = pygame.Rect(s['x'], self.surface_y + s['y'], s['w'], 2)
            pygame.draw.rect(screen, (150, 180, 255, 80), streak_rect)

        # 4 Draw splashes
        for p in self.particles:
            p.draw(screen)