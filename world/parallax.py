import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE

# --- Procedural Elements ---

class Sun:
    def __init__(self):
        self.pos = (WIDTH - 150, 80)
        self.radius = 40
        self.glow_radius = 60

    def draw(self, screen):
        # Draw a soft glow effect
        glow_surf = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 200, 50), (self.glow_radius, self.glow_radius), self.glow_radius)
        screen.blit(glow_surf, (self.pos[0] - self.glow_radius, self.pos[1] - self.glow_radius))
        # Main sun body
        pygame.draw.circle(screen, (255, 253, 220), self.pos, self.radius)

class WindStreak:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(20, GROUND_LINE - 100)
        self.length = random.randint(20, 50)
        self.speed = random.randint(300, 500)
        self.alpha = random.randint(30, 80)

    def update(self, dt):
        self.x -= self.speed * dt
        if self.x < -self.length:
            self.x = WIDTH + 10
            self.y = random.randint(20, GROUND_LINE - 100)

    def draw(self, screen):
        streak_surf = pygame.Surface((self.length, 2), pygame.SRCALPHA)
        streak_surf.fill((255, 255, 255, self.alpha))
        screen.blit(streak_surf, (self.x, self.y))

class Bird:
    def __init__(self):
        self.x = WIDTH + 50
        self.y = random.randint(50, 200)
        self.speed = random.uniform(80, 150)
        self.wing_angle = random.uniform(0, 6) # Random start flap phase
        self.size = random.randint(4, 7)

    def update(self, dt):
        self.x -= self.speed * dt
        self.wing_angle += 10 * dt 
        if self.x < -20:
            self.x = WIDTH + random.randint(100, 1000)
            self.y = random.randint(50, 250)

    def draw(self, screen):
        flap = math.sin(self.wing_angle) * self.size
        color = (30, 30, 30)
        pygame.draw.line(screen, color, (self.x, self.y), (self.x - self.size, self.y - flap), 2)
        pygame.draw.line(screen, color, (self.x, self.y), (self.x + self.size, self.y - flap), 2)

# --- Layer Objects ---

class Cloud(pygame.sprite.Sprite):
    def __init__(self, image, start_on_screen=False):
        super().__init__()
        self.image = image.copy()
        self.width = self.image.get_width()
        self.x = random.randint(0, WIDTH) if start_on_screen else WIDTH + random.randint(50, 300)
        self.y = random.randint(20, HEIGHT // 2 - 50)
        self.speed = random.uniform(20, 50)
        self.alpha = 255 if start_on_screen else 0
        self.image.set_alpha(self.alpha)
        self.fade_speed = random.randint(80, 150)

    def update(self, dt):
        self.x -= self.speed * dt
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + (self.fade_speed * dt))
            self.image.set_alpha(int(self.alpha))
            
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class ParallaxLayer:
    def __init__(self, image_path, internal_speed, y_pos=0, stretch_to_bottom=False):
        original_surf = pygame.image.load(image_path).convert_alpha()
        if stretch_to_bottom:
            fill_height = HEIGHT - y_pos
            self.image = pygame.transform.scale(original_surf, (original_surf.get_width(), fill_height))
        else:
            self.image = original_surf

        self.width = self.image.get_width()
        self.y_pos = y_pos
        self.internal_speed = internal_speed
        self.x = 0

    def update(self, dt):
        self.x -= self.internal_speed * dt
        if self.x <= -self.width:
            self.x += self.width

    def draw(self, screen):
        tiles_needed = (WIDTH // self.width) + 2
        for i in range(tiles_needed):
            screen.blit(self.image, (self.x + (i * self.width), self.y_pos))

# --- Main Background Class (ONE VERSION ONLY) ---

class ParallaxBackground:
    def __init__(self):
        # 1. Procedural Setup
        self.sun = Sun()
        self.wind_streaks = [WindStreak() for _ in range(8)]
        self.birds = [Bird() for _ in range(3)]
        
        # 2. Cloud Setup
        self.cloud_img = pygame.image.load("assets/backgrounds/cloud.png").convert_alpha()
        self.active_clouds = []
        self.spawn_timer = 0
        for _ in range(5):
            self.active_clouds.append(Cloud(self.cloud_img, start_on_screen=True))

        # 3. Static/Looping Setup
        self.mountains = ParallaxLayer("assets/backgrounds/mountain.png", 50, GROUND_LINE - 280, True)
        self.ground = ParallaxLayer("assets/backgrounds/ground.png", 200, GROUND_LINE, True)

    def update(self, unused_speed, dt):
        # Update everything
        for s in self.wind_streaks: s.update(dt)
        for b in self.birds: b.update(dt)
        
        self.spawn_timer += dt
        if self.spawn_timer > random.uniform(2.0, 5.0):
            self.active_clouds.append(Cloud(self.cloud_img))
            self.spawn_timer = 0

        for cloud in self.active_clouds[:]:
            cloud.update(dt)
            if cloud.x < -cloud.width: 
                self.active_clouds.remove(cloud)

        self.mountains.update(dt)
        self.ground.update(dt)

    def draw(self, screen):
        # ORDER IS IMPORTANT (Back to Front)
        self.sun.draw(screen)             # Layer 1
        for cloud in self.active_clouds:  # Layer 2
            cloud.draw(screen)
        for b in self.birds:              # Layer 3
            b.draw(screen)
        self.mountains.draw(screen)       # Layer 4
        for s in self.wind_streaks:       # Layer 5
            s.draw(screen)
        self.ground.draw(screen)          # Layer 6