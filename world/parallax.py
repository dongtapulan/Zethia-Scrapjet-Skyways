import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE, SKY_BLUE

# --- New Time Constants ---
SUNSET_ORANGE = (255, 110, 60)
NIGHT_NAVY = (15, 15, 35)
MIDNIGHT_PURPLE = (30, 20, 50)
LUMEN_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BOSS_SKY_COLOR = (45, 10, 50) # Dark Corrupted Purple

class Sun:
    def __init__(self):
        self.center_x = WIDTH // 2
        self.center_y = GROUND_LINE
        self.orbit_radius = WIDTH // 2 + 100
        self.pos = [0, 0]
        self.radius = 45
        self.color = list(LUMEN_GOLD)

    def update(self, angle):
        self.pos[0] = self.center_x + math.cos(angle) * self.orbit_radius
        self.pos[1] = self.center_y - math.sin(angle) * self.orbit_radius

    def draw(self, screen, is_night):
        color = (200, 210, 255) if is_night else self.color
        glow_color = (100, 100, 150, 40) if is_night else (255, 200, 50, 60)
        
        glow_size = self.radius * 2 if not is_night else self.radius * 1.5
        glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(glow_surf, (self.pos[0] - glow_size, self.pos[1] - glow_size))
        
        pygame.draw.circle(screen, color, (int(self.pos[0]), int(self.pos[1])), self.radius)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT // 2 + 100)
        self.size = random.randint(1, 3)
        self.flicker = random.uniform(0, math.pi)

    def draw(self, screen, alpha):
        current_alpha = max(0, min(255, int(alpha)))
        if current_alpha <= 0: return

        flicker_val = (0.4 + 0.6 * math.sin(pygame.time.get_ticks() * 0.003 + self.flicker))
        s_alpha = int(max(0, min(255, current_alpha * flicker_val)))
        
        star_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (255, 255, 255, s_alpha), (self.size, self.size), self.size)
        screen.blit(star_surf, (self.x, self.y))

class Bird:
    def __init__(self):
        self.x = WIDTH + 50
        self.y = random.randint(50, 200)
        self.speed = random.uniform(80, 150)
        self.wing_angle = random.uniform(0, 6)
        self.size = random.randint(4, 7)
    def update(self, dt):
        self.x -= self.speed * dt
        self.wing_angle += 10 * dt 
        if self.x < -20:
            self.x = WIDTH + random.randint(100, 1000)
            self.y = random.randint(50, 250)
    def draw(self, screen):
        flap = math.sin(self.wing_angle) * self.size
        pygame.draw.line(screen, (30, 30, 30), (self.x, self.y), (self.x - self.size, self.y - flap), 2)
        pygame.draw.line(screen, (30, 30, 30), (self.x, self.y), (self.x + self.size, self.y - flap), 2)

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

class Cloud(pygame.sprite.Sprite):
    def __init__(self, image, start_on_screen=False):
        super().__init__()
        self.image = image.copy()
        self.width = self.image.get_width()
        self.x = random.randint(0, WIDTH) if start_on_screen else WIDTH + random.randint(50, 300)
        self.y = random.randint(20, HEIGHT // 2 - 50)
        self.speed = random.uniform(20, 50)
        self.alpha = 180 if start_on_screen else 0
        self.image.set_alpha(self.alpha)
        self.fade_speed = random.randint(80, 150)
    def update(self, dt):
        self.x -= self.speed * dt
        if self.alpha < 180:
            self.alpha = min(180, self.alpha + (self.fade_speed * dt))
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
        if self.x <= -self.width: self.x += self.width
    def draw(self, screen):
        tiles_needed = (WIDTH // self.width) + 2
        for i in range(tiles_needed):
            screen.blit(self.image, (self.x + (i * self.width), self.y_pos))

class ParallaxBackground:
    def __init__(self):
        self.bg_color = list(SKY_BLUE)
        self.stars = [Star() for _ in range(70)]
        self.star_alpha = 0
        self.sun = Sun()
        self.boss_factor = 0.0
        self.target_boss_factor = 0.0
        self.wind_streaks = [WindStreak() for _ in range(8)]
        self.birds = [Bird() for _ in range(3)]
        
        try:
            self.cloud_img = pygame.image.load("assets/backgrounds/cloud.png").convert_alpha()
        except:
            self.cloud_img = pygame.Surface((100, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(self.cloud_img, (255, 255, 255, 150), (0, 0, 100, 50))
            
        self.active_clouds = []
        self.spawn_timer = 0
        for _ in range(5):
            self.active_clouds.append(Cloud(self.cloud_img, start_on_screen=True))

        self.mountains = ParallaxLayer("assets/backgrounds/mountain.png", 50, GROUND_LINE - 280, True)
        self.ground_layer = ParallaxLayer("assets/backgrounds/ground.jpeg", 200, GROUND_LINE, True)

    def enter_boss_mode(self):
        self.target_boss_factor = 1.0

    def exit_boss_mode(self):
        """Forces an immediate reset to prevent purple sky hanging around."""
        self.target_boss_factor = 0.0
        self.boss_factor = 0.0 

    def update(self, player_distance, dt):
        # 1. Update Boss Interpolation
        if self.boss_factor < self.target_boss_factor:
            self.boss_factor = min(self.target_boss_factor, self.boss_factor + 2.0 * dt)
        elif self.boss_factor > self.target_boss_factor:
            self.boss_factor = max(self.target_boss_factor, self.boss_factor - 4.0 * dt) # Faster fade out

        # 2. Cycle Math
        time_angle = (player_distance / 40000.0) * (2 * math.pi)
        normalized_angle = time_angle % (2 * math.pi)
        self.sun.update(normalized_angle)
        is_night = normalized_angle > math.pi
        day_intensity = max(0, math.sin(normalized_angle))
        
        if not is_night:
            base_r = SUNSET_ORANGE[0] * (1 - day_intensity) + SKY_BLUE[0] * day_intensity
            base_g = SUNSET_ORANGE[1] * (1 - day_intensity) + SKY_BLUE[1] * day_intensity
            base_b = SUNSET_ORANGE[2] * (1 - day_intensity) + SKY_BLUE[2] * day_intensity
            self.star_alpha = max(0, self.star_alpha - 250 * dt)
        else:
            night_intensity = abs(math.sin(normalized_angle))
            base_r = SUNSET_ORANGE[0] * (1 - night_intensity) + NIGHT_NAVY[0] * night_intensity
            base_g = SUNSET_ORANGE[1] * (1 - night_intensity) + NIGHT_NAVY[1] * night_intensity
            base_b = SUNSET_ORANGE[2] * (1 - night_intensity) + NIGHT_NAVY[2] * night_intensity
            self.star_alpha = min(255, self.star_alpha + 100 * dt)

        # 3. Boss Blending
        b_f = max(0.0, min(1.0, self.boss_factor))
        final_r = base_r * (1 - b_f) + BOSS_SKY_COLOR[0] * b_f
        final_g = base_g * (1 - b_f) + BOSS_SKY_COLOR[1] * b_f
        final_b = base_b * (1 - b_f) + BOSS_SKY_COLOR[2] * b_f

        self.bg_color = [int(final_r), int(final_g), int(final_b)]

        # --- Objects ---
        for s in self.wind_streaks: s.update(dt)
        for b in self.birds: b.update(dt)
        self.spawn_timer += dt
        if self.spawn_timer > 3.0:
            self.active_clouds.append(Cloud(self.cloud_img))
            self.spawn_timer = 0
        for cloud in self.active_clouds[:]:
            cloud.update(dt)
            if cloud.x < -cloud.width: self.active_clouds.remove(cloud)

        speed_mult = 1.0 + (b_f * 0.5)
        self.mountains.update(dt * speed_mult)
        self.ground_layer.update(dt * speed_mult)

    def draw(self, screen):
        screen.fill(tuple(self.bg_color))
        
        safe_star_alpha = int(max(0, min(255, self.star_alpha)))
        total_star_alpha = max(safe_star_alpha, int(self.boss_factor * 150))
        for star in self.stars:
            star.draw(screen, total_star_alpha)

        if self.boss_factor < 0.8:
            self.sun.draw(screen, safe_star_alpha > 120) 
        
        for cloud in self.active_clouds: cloud.draw(screen)
        for b in self.birds: b.draw(screen)
        
        self.mountains.draw(screen) 
        for s in self.wind_streaks: s.draw(screen)
        self.ground_layer.draw(screen)