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
        self.spawn_delay = 3.0 
        
        # Boss Systems
        self.boss_active = False
        self.next_boss_dist = random.randint(3000, 6000)
        self.warning_timer = 0
        self.thunder_timer = 0
        self.sky_alpha = 0  # 0 to 150 (Dark purple intensity)

    def reset(self):
        self.enemies.empty()
        self.particles = []
        self.spawn_timer = 0
        self.spawn_delay = 3.0
        self.boss_active = False
        self.sky_alpha = 0
        self.next_boss_dist = random.randint(3000, 6000)

    def update(self, dt, player_pos, proj_manager):
        # 1. Check for Boss Spawning
        current_dist = self.game.player.distance
        if not self.boss_active and current_dist >= self.next_boss_dist:
            # Only trigger if there isn't another boss currently dying/fading
            self.trigger_boss_spawn()

        # 2. Atmospheric State Machine (Fading Logic)
        if self.boss_active:
            # Gradually darken the sky to purple
            if self.sky_alpha < 150:
                self.sky_alpha = min(150, self.sky_alpha + 60 * dt)
            
            # Handle Warning Text timer
            if self.warning_timer > 0:
                self.warning_timer -= dt
            
            # Random Thunder Flicker
            self.thunder_timer -= dt
            if self.thunder_timer <= 0:
                self.trigger_thunder()
                self.thunder_timer = random.uniform(3.0, 7.0)
        else:
            # SMOOTH TRANSITION: Fade sky back to normal after boss dies
            if self.sky_alpha > 0:
                self.sky_alpha = max(0, self.sky_alpha - 40 * dt) # Slow fade out

        # 3. Update Existing Enemies
        for enemy in self.enemies:
            enemy.update(dt, player_pos, proj_manager)
            # Kill enemies if they leave screen (unless it's the Boss)
            if enemy.rect.right < -100 and not getattr(enemy, 'is_boss', False):
                enemy.kill()

        # 4. Update Death Particles
        for p in self.particles[:]:
            p.update(dt)
            if p.alpha <= 0:
                self.particles.remove(p)

        # 5. Spawning Logic (Standard enemies pause when boss is active OR sky is still purple)
        if self.game.state == "PLAYING" and not self.boss_active and self.sky_alpha < 50:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_random()
                self.spawn_timer = 0
                self.spawn_delay = max(1.0, self.spawn_delay - 0.02)

    def trigger_boss_spawn(self):
        self.boss_active = True
        self.warning_timer = 4.0  # Show warning for 4 seconds
        self.enemies.add(BlightTitan(WIDTH + 200, HEIGHT // 2))
        
        # Switch Music
        try:
            pygame.mixer.music.load("assets/sfx/boss_theme.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Boss music file not found.")

    def trigger_thunder(self):
        try:
            sound = pygame.mixer.Sound("assets/sfx/explosion.wav")
            sound.set_volume(0.3) # Slightly quieter thunder
            sound.play()
        except:
            pass
        # Briefly flash the screen (this interacts with the draw call)
        # We use a flag or a direct screen fill if calling from engine, 
        # but here we can just perform a one-frame fill.
        self.game.screen.fill((220, 220, 255)) 

    def spawn_random(self):
        y = random.randint(100, HEIGHT - 100)
        x = WIDTH + 50
        choice = random.random()
        
        if choice < 0.15:
            self.enemies.add(BlightBeast(x, y))
        elif choice < 0.45:
            self.enemies.add(GloomBat(x, y))
        elif choice < 0.70:
            self.enemies.add(MonsterSaucer(x, y))
        else:
            self.enemies.add(BushMonster(x, y))

    def trigger_death_effect(self, x, y):
        # Normal enemies get 15 particles, we can check if it's a boss for more!
        count = 50 if self.boss_active else 15
        for _ in range(count):
            self.particles.append(DeathParticle(x, y))

    def draw(self, screen):
        # Layer 0: Blight Storm Sky Overlay (Smooth fade based on sky_alpha)
        if self.sky_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(int(self.sky_alpha))
            overlay.fill((40, 0, 80)) # Deep purple
            screen.blit(overlay, (0, 0))

        # Layer 1: Auras and Special Glows
        for enemy in self.enemies:
            enemy.draw_aura(screen)
            if hasattr(enemy, 'draw_glow'):
                enemy.draw_glow(screen)
        
        # Layer 2: Sprites
        self.enemies.draw(screen)
        
        # Layer 3: Particles
        for p in self.particles:
            p.draw(screen)

        # Layer 4: Boss Warning UI
        if self.warning_timer > 0:
            self.draw_warning(screen)

    def draw_warning(self, screen):
        # Flashing red text with pulse effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
        color = (255, int(50 * pulse), int(50 * pulse))
        
        font = pygame.font.SysFont("Impact", 50)
        warn_surf = font.render("!!! WARNING: BLIGHT TITAN DETECTED !!!", True, color)
        warn_rect = warn_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        
        # Black shadow for readability
        shadow = font.render("!!! WARNING: BLIGHT TITAN DETECTED !!!", True, (0, 0, 0))
        screen.blit(shadow, (warn_rect.x + 2, warn_rect.y + 2))
        screen.blit(warn_surf, warn_rect)