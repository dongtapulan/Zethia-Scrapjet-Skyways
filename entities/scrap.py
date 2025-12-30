import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE

class Scrap(pygame.sprite.Sprite):
    def __init__(self, x, y, scrap_type, images):
        super().__init__()
        self.scrap_type = scrap_type
        
        # --- STATS & POWERUPS ---
        if self.scrap_type == "battery":
            self.image = images['battery']
            self.weight_value = 1   
            self.value = 100        
            self.magnet_range = 350 
            self.drift_speed = 10   
        
        elif self.scrap_type == "gear":
            self.image = images['gear']
            self.weight_value = 45  
            self.value = 50         
            self.magnet_range = 90  
            self.drift_speed = 60   
            
        elif self.scrap_type == "missile":
            self.image = images['missile']
            self.weight_value = 5   
            self.value = 0          
            self.magnet_range = 250 
            self.drift_speed = 15   
            
        elif self.scrap_type == "bomb":
            self.image = images['bomb']
            self.weight_value = 15  
            self.value = 0          
            self.magnet_range = 150 
            self.drift_speed = 40   

        else: # Golden Bolt
            self.image = images['bolt']
            self.weight_value = 1   
            self.value = 10         
            self.magnet_range = 180 
            self.drift_speed = 25   

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.bob_timer = random.uniform(0, math.pi * 2)
        self.attract_speed = 0
        self.max_attract_speed = 750 

    def update(self, dt, player_pos):
        self.bob_timer += 4 * dt
        bob_offset = math.sin(self.bob_timer) * 0.5
        
        target_vec = pygame.Vector2(player_pos) - self.pos
        distance = target_vec.length()
        
        if distance < self.magnet_range:
            self.attract_speed = min(self.max_attract_speed, self.attract_speed + 1000 * dt)
            move_dir = target_vec.normalize()
            self.pos += move_dir * self.attract_speed * dt
        else:
            self.pos.x -= 200 * dt 
            self.pos.y += (self.drift_speed * dt) + bob_offset 
            self.attract_speed = 0 

        if self.pos.y > GROUND_LINE - 10:
            self.pos.y = GROUND_LINE - 10

        self.rect.center = self.pos

class ScrapManager:
    def __init__(self):
        self.scrap_group = pygame.sprite.Group()
        self.spawn_timer = 0
        
        path = "assets/sprites/scraps/"
        try:
            self.images = {
                'bolt': pygame.image.load(path + "golden_bolt.png").convert_alpha(),
                'gear': pygame.image.load(path + "heavy bronze gear.png").convert_alpha(),
                'battery': pygame.image.load(path + "glowing_battery.png").convert_alpha(),
                'missile': pygame.image.load(path + "missile_pickup.png").convert_alpha(),
                'bomb': pygame.image.load(path + "gravity_bomb_pickup.png").convert_alpha()
            }
        except:
            self.images = {k: pygame.Surface((20, 20)) for k in ['bolt', 'gear', 'battery', 'missile', 'bomb']}

    def spawn_pattern(self):
        # Weighted choice: Rare weapons (10%), Strategic (20%), Common (70%)
        roll = random.random()
        start_y = random.randint(100, GROUND_LINE - 150)
        
        if roll < 0.70:
            count = random.randint(3, 5)
            for i in range(count):
                self.scrap_group.add(Scrap(WIDTH + (i * 60), start_y, "bolt", self.images))
        elif roll < 0.90:
            choice = "battery" if random.random() < 0.2 else "gear"
            self.scrap_group.add(Scrap(WIDTH, start_y, choice, self.images))
        else:
            # WEAPONS ARE NOW RAREST
            choice = "bomb" if random.random() < 0.4 else "missile"
            self.scrap_group.add(Scrap(WIDTH, start_y, choice, self.images))

    def update(self, dt, player_pos):
        self.spawn_timer += dt
        # SPAWN TIME INCREASED TO 8-12 SECONDS
        if self.spawn_timer > random.uniform(8.0, 12.0):
            self.spawn_pattern()
            self.spawn_timer = 0
            
        self.scrap_group.update(dt, player_pos)
        for scrap in self.scrap_group:
            if scrap.rect.right < -100:
                scrap.kill()

    def draw(self, screen):
        self.scrap_group.draw(screen)