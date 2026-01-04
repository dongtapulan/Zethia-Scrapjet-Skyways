import pygame
import random
from settings import *

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed_mult):
        super().__init__()
        # 1. Image & Random Rotation
        self.original_image = image
        self.rotation = random.randint(0, 360)
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Stats
        self.health = 3 
        # Base speed scaled by the world difficulty multiplier
        self.base_speed = BASE_SCROLL_SPEED
        self.mask = pygame.mask.from_surface(self.image) 

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, dt, difficulty_mult):
        # Use the multiplier to match the parallax and enemy speed
        current_speed = self.base_speed * difficulty_mult
        self.rect.x -= current_speed * dt
        
        if self.rect.right < -100:
            self.kill()

class ObstacleManager:
    def __init__(self):
        self.obstacles = pygame.sprite.Group()
        self.spawn_timer = 0
        self.base_spawn_rate = 2.0 # Base seconds between spawns
        
        # Load the rock image
        try:
            self.rock_img = pygame.image.load("assets/sprites/corrupted_rock.png").convert_alpha()
        except:
            self.rock_img = pygame.Surface((60, 60))
            self.rock_img.fill(GLOOM_VIOLET)

    def update(self, dt, difficulty_mult):
        self.spawn_timer += dt
        
        # 1. Faster Spawning logic
        # As difficulty increases, the rate at which obstacles appear increases
        # e.g., at 2x difficulty, objects spawn every 1.0s instead of 2.0s
        dynamic_spawn_rate = max(0.4, self.base_spawn_rate / difficulty_mult)
        
        if self.spawn_timer >= dynamic_spawn_rate:
            self.spawn_obstacle(difficulty_mult)
            self.spawn_timer = 0

        # 2. Update existing obstacles with the multiplier
        for obstacle in self.obstacles:
            obstacle.update(dt, difficulty_mult)

    def spawn_obstacle(self, difficulty_mult):
        # Randomly scale the image for each specific rock to prevent repetitiveness
        size = random.randint(40, 110)
        scaled_img = pygame.transform.scale(self.rock_img, (size, size))
        
        spawn_y = random.randint(100, GROUND_LINE - 100)
        new_rock = Obstacle(WIDTH + 150, spawn_y, scaled_img, difficulty_mult)
        self.obstacles.add(new_rock)

    def draw(self, screen):
        self.obstacles.draw(screen)