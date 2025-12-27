import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE

class Scrap(pygame.sprite.Sprite):
    def __init__(self, x, y, scrap_type, images):
        super().__init__()
        self.scrap_type = scrap_type
        
        # --- DETAILED TRADE-OFFS ---
        if self.scrap_type == "battery":
            self.image = images['battery']
            self.weight_value = 1   # Extremely light
            self.value = 100        # Jackpot
            self.magnet_range = 350 # Huge attraction distance
            self.drift_speed = 10   # Floats almost perfectly still
        
        elif self.scrap_type == "gear":
            self.image = images['gear']
            self.weight_value = 45  # HUGE weight penalty
            self.value = 50         # Medium reward
            self.magnet_range = 90  # Weak magnetism (must fly close)
            self.drift_speed = 60   # Sinks toward the ground (looks heavy)
        
        else: # Golden Bolt
            self.image = images['bolt']
            self.weight_value = 1   # Very light
            self.value = 10         # Standard score
            self.magnet_range = 180 # Normal magnetism
            self.drift_speed = 25   # Natural drift

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.bob_timer = random.uniform(0, math.pi * 2)
        
        # Magnetism State
        self.attract_speed = 0
        self.max_attract_speed = 750 # Top speed when being sucked in

    def update(self, dt, player_pos):
        # 1. Visual Bobbing
        self.bob_timer += 4 * dt
        bob_offset = math.sin(self.bob_timer) * 0.5
        
        # 2. Magnetic Pull Logic
        target_vec = pygame.Vector2(player_pos) - self.pos
        distance = target_vec.length()
        
        if distance < self.magnet_range:
            # Accelerate toward Huey
            self.attract_speed = min(self.max_attract_speed, self.attract_speed + 1000 * dt)
            move_dir = target_vec.normalize()
            self.pos += move_dir * self.attract_speed * dt
        else:
            # Standard World Movement
            self.pos.x -= 200 * dt # Scroll with world
            self.pos.y += (self.drift_speed * dt) + bob_offset # Sinking/Bobbing
            self.attract_speed = 0 # Reset speed if out of range

        # Keep scrap above the floor
        if self.pos.y > GROUND_LINE - 10:
            self.pos.y = GROUND_LINE - 10

        self.rect.center = self.pos

class ScrapManager:
    def __init__(self):
        self.scrap_group = pygame.sprite.Group()
        self.spawn_timer = 0
        
        path = "assets/sprites/scraps/"
        self.images = {
            'bolt': pygame.image.load(path + "golden_bolt.png").convert_alpha(),
            'gear': pygame.image.load(path + "heavy bronze gear.png").convert_alpha(),
            'battery': pygame.image.load(path + "glowing_battery.png").convert_alpha()
        }

    def spawn_pattern(self):
        # We now choose between a "Common" bolt run, or a "Strategic" solo item
        pattern = random.choice(["bolts", "bolts", "bolts", "strategic"])
        start_y = random.randint(100, GROUND_LINE - 150)
        
        if pattern == "bolts":
            # Spawn a small line of common bolts
            count = random.randint(3, 5)
            for i in range(count):
                self.scrap_group.add(Scrap(WIDTH + (i * 60), start_y, "bolt", self.images))
        
        elif pattern == "strategic":
            # Spawn a single high-value item: either a heavy choice or a rare find
            # 80% chance for Gear, 20% for Battery
            choice = "battery" if random.random() < 0.2 else "gear"
            self.scrap_group.add(Scrap(WIDTH, start_y, choice, self.images))

    def update(self, dt, player_pos):
        self.spawn_timer += dt
        
        # REDUCED SPAWN FREQUENCY: 
        # Spawns an item/pattern every 4 to 7 seconds instead of 2.5
        if self.spawn_timer > random.uniform(4.0, 7.0):
            self.spawn_pattern()
            self.spawn_timer = 0
            
        self.scrap_group.update(dt, player_pos)
        
        # Cleanup off-screen
        for scrap in self.scrap_group:
            if scrap.rect.right < -100:
                scrap.kill()

    def draw(self, screen):
        self.scrap_group.draw(screen)