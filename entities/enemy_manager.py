import pygame
import random
import math
from settings import WIDTH, HEIGHT
from entities.enemies import GloomBat, BushMonster, MonsterSaucer, BlightBeast, BlightTitan

class DeathParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-150, -50) 
        self.vel_y = random.uniform(-50, 50)
        self.radius = random.randint(4, 10)
        self.color = random.choice([(180, 50, 255), (255, 80, 220), (120, 20, 200)])
        self.alpha = 255
        self.fade_speed = random.uniform(150, 250)

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.alpha -= self.fade_speed * dt
        self.radius = max(0, self.radius - 2 * dt)

    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            draw_alpha = max(0, min(255, int(self.alpha)))
            pygame.draw.circle(s, (*self.color, draw_alpha), (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(s, (self.x - self.radius, self.y - self.radius))

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemies = pygame.sprite.Group()
        self.particles = [] 
        self.spawn_timer = 0
        self.spawn_delay = 3.5 
        
        self.boss_active = False
        self.next_boss_dist = random.randint(8000, 15000)
        self.warning_timer = 0
        self.thunder_timer = 0
        self.sky_alpha = 0

    def reset(self):
        self.enemies.empty()
        self.particles = []
        self.spawn_timer = 0
        self.spawn_delay = 3.5
        self.boss_active = False
        self.sky_alpha = 0
        self.next_boss_dist = random.randint(8000, 15000)

    def update(self, dt, player_pos, proj_manager, difficulty_mult):
        current_dist = self.game.player.distance
        
        # Check for boss trigger
        if not self.boss_active and current_dist >= self.next_boss_dist:
            self.trigger_boss_spawn()

        # Handle Boss Environment Effects
        if self.boss_active:
            if self.sky_alpha < 150:
                self.sky_alpha = min(150, self.sky_alpha + 100 * dt) # Faster transition in
            if self.warning_timer > 0: self.warning_timer -= dt
            
            self.thunder_timer -= dt
            if self.thunder_timer <= 0:
                self.trigger_thunder()
                self.thunder_timer = random.uniform(3.0, 7.0)
        else:
            # SNAP sky alpha to zero if no boss is present
            self.sky_alpha = 0

        # Update Enemies
        scaled_dt = dt * difficulty_mult
        for enemy in self.enemies:
            enemy.update(scaled_dt, player_pos, proj_manager)
            # Kill enemies that go off-screen (unless they are the boss)
            if enemy.rect.right < -100 and not getattr(enemy, 'is_boss', False):
                enemy.kill()

        # Update Death Particles
        for p in self.particles[:]:
            p.update(dt)
            if p.alpha <= 0: self.particles.remove(p)

        # SPAWNING LOGIC
        # FIXED: Removed the 'sky_alpha < 50' restriction which caused the spawn freeze
        if self.game.state == "PLAYING" and not self.boss_active:
            self.spawn_timer += dt
            current_delay = max(0.8, self.spawn_delay / math.sqrt(difficulty_mult))
            
            if self.spawn_timer >= current_delay:
                self.spawn_random()
                self.spawn_timer = 0

    def trigger_boss_spawn(self):
        self.boss_active = True
        self.warning_timer = 4.0
        # Ensure the boss is added to the group
        boss = BlightTitan(WIDTH + 200, HEIGHT // 2)
        boss.is_boss = True # Tag it so it isn't killed for going off-screen
        self.enemies.add(boss)
        try:
            pygame.mixer.music.load("assets/audio/boss_theme.wav") # Ensure path is correct
            pygame.mixer.music.play(-1)
        except: pass

    def trigger_thunder(self):
        # A quick flash effect
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.fill((220, 220, 255))
        flash.set_alpha(100)
        self.game.screen.blit(flash, (0,0))

    def spawn_random(self):
        y = random.randint(100, HEIGHT - 100)
        x = WIDTH + 50
        choice = random.random()
        if choice < 0.15: self.enemies.add(BlightBeast(x, y))
        elif choice < 0.45: self.enemies.add(GloomBat(x, y))
        elif choice < 0.70: self.enemies.add(MonsterSaucer(x, y))
        else: self.enemies.add(BushMonster(x, y))

    def trigger_death_effect(self, x, y):
        # Increased particle count for satisfying boss kills
        count = 60 if self.boss_active else 15
        for _ in range(count): 
            self.particles.append(DeathParticle(x, y))

    def draw(self, screen):
        # Draw the boss sky overlay
        if self.sky_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(int(self.sky_alpha))
            overlay.fill((40, 0, 80)) # Purple tint
            screen.blit(overlay, (0, 0))

        for enemy in self.enemies:
            if hasattr(enemy, 'draw_aura'): enemy.draw_aura(screen)
            if hasattr(enemy, 'draw_glow'): enemy.draw_glow(screen)
        
        self.enemies.draw(screen)
        for p in self.particles: p.draw(screen)
        if self.warning_timer > 0: self.draw_warning(screen)

    def draw_warning(self, screen):
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
        color = (255, int(100 * pulse), int(100 * pulse))
        font = pygame.font.SysFont("Impact", 50)
        warn_surf = font.render("!!! WARNING: BLIGHT TITAN DETECTED !!!", True, color)
        warn_rect = warn_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(warn_surf, warn_rect)