import pygame
import random
from settings import *

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        # 1. Image & Random Rotation for variety
        self.original_image = image
        self.rotation = random.randint(0, 360)
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Stats
        self.health = 3 # Takes 3 hits to break
        self.speed = PLAYER_SPEED # Moves with the world
        self.mask = pygame.mask.from_surface(self.image) # For pixel-perfect collision

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, dt):
        # Move left to simulate Huey flying forward
        self.rect.x -= self.speed * dt
        
        # Remove if off-screen
        if self.rect.right < -50:
            self.kill()

class ObstacleManager:
    def __init__(self):
        self.obstacles = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_rate = 2.0 # Spawn every 2 seconds
        
        # Load the rock image
        try:
            self.rock_img = pygame.image.load("assets/sprites/corrupted_rock.png").convert_alpha()
            # Randomly scale it between 40 and 90 pixels
            size = random.randint(40, 90)
            self.rock_img = pygame.transform.scale(self.rock_img, (size, size))
        except:
            # Fallback square if image is missing
            self.rock_img = pygame.Surface((50, 50))
            self.rock_img.fill(GLOOM_VIOLET)

    def update(self, dt):
        self.spawn_timer += dt
        
        # Procedural Spawning
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_obstacle()
            self.spawn_timer = 0
            # Gradually speed up spawning as distance increases
            self.spawn_rate = max(0.8, self.spawn_rate - 0.01)

        self.obstacles.update(dt)

    def spawn_obstacle(self):
        # Avoid spawning rocks too close to the ground or ceiling
        spawn_y = random.randint(100, GROUND_LINE - 100)
        new_rock = Obstacle(WIDTH + 100, spawn_y, self.rock_img)
        self.obstacles.add(new_rock)

    def draw(self, screen):
        self.obstacles.draw(screen)