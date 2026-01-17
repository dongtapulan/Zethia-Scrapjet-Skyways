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
        self.next_boss_dist = random.randint(8000, 12000)
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
        self.next_boss_dist = random.randint(8000, 12000)

    def set_next_boss(self):
        """Called when a boss dies to schedule the next one."""
        self.next_boss_dist = self.game.player.distance + random.randint(15000, 25000)
        self.boss_active = False

    def update(self, dt, player_pos, proj_manager, difficulty_mult):
        current_dist = self.game.player.distance
        
        # 1. BOSS TRIGGER CHECK
        if not self.boss_active and current_dist >= self.next_boss_dist:
            self.trigger_boss_spawn()

        # 2. BOSS VISUALS (Thunder & Sky Tint)
        if self.boss_active:
            if self.sky_alpha < 150:
                self.sky_alpha = min(150, self.sky_alpha + 100 * dt)
            if self.warning_timer > 0: self.warning_timer -= dt
            
            self.thunder_timer -= dt
            if self.thunder_timer <= 0:
                self.trigger_thunder()
                self.thunder_timer = random.uniform(4.0, 8.0) # Slightly rarer thunder
        else:
            if self.sky_alpha > 0:
                self.sky_alpha = max(0, self.sky_alpha - 100 * dt)

        # 3. UPDATE ENEMIES
        scaled_dt = dt * difficulty_mult
        for enemy in self.enemies:
            # Pass player position for the new tracking GloomBats
            enemy.update(scaled_dt, player_pos, proj_manager)
            if enemy.rect.right < -150 and not getattr(enemy, 'is_boss', False):
                enemy.kill()

        # 4. UPDATE PARTICLES
        for p in self.particles[:]:
            p.update(dt)
            if p.alpha <= 0: self.particles.remove(p)

        # 5. REGULAR SPAWNING (Only if no boss)
        if self.game.state == "PLAYING" and not self.boss_active:
            self.spawn_timer += dt
            current_delay = max(0.7, self.spawn_delay / math.sqrt(difficulty_mult))
            
            if self.spawn_timer >= current_delay:
                self.spawn_random()
                self.spawn_timer = 0

    def trigger_boss_spawn(self):
        self.boss_active = True
        self.warning_timer = 4.0
        # Blight Titan spawn (Start him further back for entrance)
        boss = BlightTitan(WIDTH + 400, HEIGHT // 2)
        self.enemies.add(boss)
        
        if hasattr(self.game, 'bg'):
            self.game.bg.enter_boss_mode()

        try:
            # Play boss theme from consistent audio folder
            pygame.mixer.music.load("assets/audio/boss_theme.wav")
            pygame.mixer.music.play(-1)
        except: pass

    def trigger_thunder(self):
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.fill((200, 200, 255)) # Cooler blue thunder
        flash.set_alpha(70)
        self.game.screen.blit(flash, (0,0))

    def spawn_random(self):
        y = random.randint(100, HEIGHT - 100)
        x = WIDTH + 50
        choice = random.random()
        
        # Probabilities adjusted for "Monster Saucer" dominance (40% chance)
        if choice < 0.10: 
            self.enemies.add(BlightBeast(x, y))
        elif choice < 0.35: 
            self.enemies.add(GloomBat(x, y))
        elif choice < 0.75: # Saucer: 0.35 to 0.75 = 40% spawn rate!
            self.enemies.add(MonsterSaucer(x, y))
        else: 
            self.enemies.add(BushMonster(x, y))

    def trigger_death_effect(self, x, y, is_boss=False):
        count = 120 if is_boss else 15
        for _ in range(count): 
            self.particles.append(DeathParticle(x, y))

    def draw(self, screen):
        # 1. Sky Tint (Darker for Boss)
        if self.sky_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(int(self.sky_alpha))
            overlay.fill((30, 0, 60)) # Deep Indigo
            screen.blit(overlay, (0, 0))

        # 2. Draw Aura/Glow/Charge behind sprites
        for enemy in self.enemies:
            if hasattr(enemy, 'draw_aura'): enemy.draw_aura(screen)
            if hasattr(enemy, 'draw_glow'): enemy.draw_glow(screen)
            if hasattr(enemy, 'draw_charge'): enemy.draw_charge(screen)
        
        # 3. Main Sprite Group
        self.enemies.draw(screen)
        
        # 4. Boss Specific UI (Health Bar)
        for enemy in self.enemies:
            if getattr(enemy, 'is_boss', False):
                enemy.draw_health_bar(screen)

        # 5. Particles & Warning
        for p in self.particles: p.draw(screen)
        if self.warning_timer > 0: self.draw_warning(screen)

    def draw_warning(self, screen):
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
        color = (255, int(50 * pulse), int(50 * pulse))
        try:
            font = pygame.font.Font("assets/fonts/Impact.ttf", 60)
        except:
            font = pygame.font.SysFont("Impact", 60)
            
        warn_surf = font.render("!!! BLIGHT TITAN DETECTED !!!", True, color)
        warn_rect = warn_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(warn_surf, warn_rect)