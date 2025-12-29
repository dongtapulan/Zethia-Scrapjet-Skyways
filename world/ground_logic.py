import pygame
import random
from settings import *

class SplashParticle:
    """Particles created when Huey skims the surface."""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        # Splash moves backward and slightly up
        self.vel = pygame.Vector2(random.uniform(-100, -200), random.uniform(-20, -50))
        self.life = 1.0
        self.decay = random.uniform(2.0, 4.0)
        self.color = random.choice([(200, 230, 255), (255, 255, 255), SKY_BLUE])

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= self.decay * dt

    def draw(self, screen):
        size = int(self.life * 5)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)

class Ground:
    def __init__(self):
        self.surface_y = GROUND_LINE
        
        # 1. Load the Ground Texture
        try:
            self.image = pygame.image.load("assets/backgrounds/ground.jpeg").convert_alpha()
            # Scale it to the height of your ground zone
            self.image = pygame.transform.scale(self.image, (self.image.get_width(), GROUND_HEIGHT))
        except:
            # Fallback if image is missing
            self.image = pygame.Surface((WIDTH, GROUND_HEIGHT))
            self.image.fill((30, 50, 80))
            
        self.width = self.image.get_width()
        self.scroll = 0
        
        # Systems
        self.particles = []
        self.splash_timer = 0

    def update(self, dt, player_rect, is_skimming):
        # 1. Scroll the texture based on player speed (tied to PLAYER_SPEED)
        self.scroll = (self.scroll + PLAYER_SPEED * dt) % self.width

        # 2. Spawn Splash Particles if player is skimming
        if is_skimming:
            self.splash_timer += dt
            if self.splash_timer > 0.05:
                spawn_x = player_rect.left + 10
                spawn_y = self.surface_y + random.randint(0, 5)
                self.particles.append(SplashParticle(spawn_x, spawn_y))
                self.splash_timer = 0

        # 3. Update existing particles
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    def check_crash(self, player):
        """Logic for hard landings."""
        if player.rect.bottom >= self.surface_y and player.physics.velocity_y > 15:
            return True
        return False

    def draw(self, screen):
        # 4. Tiled Drawing for Infinite Scroll
        # We draw enough tiles to cover the screen width + 1 extra to hide the seam
        tiles_needed = (WIDTH // self.width) + 2
        for i in range(tiles_needed):
            x_pos = (i * self.width) - self.scroll
            screen.blit(self.image, (x_pos, self.surface_y))
        
        # Subtle top-edge highlight to help the player see the collision line
        pygame.draw.line(screen, (100, 200, 255), (0, self.surface_y), (WIDTH, self.surface_y), 1)

        # Draw splashes on top of the texture
        for p in self.particles:
            p.draw(screen)