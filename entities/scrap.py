import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE

class Scrap(pygame.sprite.Sprite):
    def __init__(self, x, y, scrap_type, images):
        super().__init__()
        self.scrap_type = scrap_type
        
        # --- STATS & POWERUPS ---
        self.weight_value = 1
        self.value = 10
        self.magnet_range = 180
        self.drift_speed = 25
        self.is_companion_scrap = False

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

        # --- COMPANION SCRAPS ---
        elif self.scrap_type == "red_core":
            self.image = images['red_core']
            self.weight_value = 0   
            self.value = 500
            self.magnet_range = 600 
            self.drift_speed = 10   
            self.is_companion_scrap = True

        elif self.scrap_type == "tine_soul":
            self.image = images['tine_soul']
            self.weight_value = 0
            self.value = 500
            self.magnet_range = 600
            self.drift_speed = 10
            self.is_companion_scrap = True
            
        elif self.scrap_type == "gold_oracle":
            self.image = images['gold_oracle']
            self.weight_value = 0
            self.value = 1000 # Cici is legendary!
            self.magnet_range = 800 # Super high attraction
            self.drift_speed = 5
            self.is_companion_scrap = True

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
        self.max_attract_speed = 900 

    def update(self, dt, player_pos):
        self.bob_timer += 4 * dt
        bob_offset = math.sin(self.bob_timer) * 0.8
        
        target_vec = pygame.Vector2(player_pos) - self.pos
        distance = target_vec.length()
        
        if distance < self.magnet_range:
            self.attract_speed = min(self.max_attract_speed, self.attract_speed + 1500 * dt)
            move_dir = target_vec.normalize()
            self.pos += move_dir * self.attract_speed * dt
        else:
            self.pos.x -= 250 * dt 
            self.pos.y += (self.drift_speed * dt) + bob_offset 
            self.attract_speed = 0 

        if self.pos.y > GROUND_LINE - 20:
            self.pos.y = GROUND_LINE - 20

        self.rect.center = self.pos

class ScrapManager:
    def __init__(self):
        self.scrap_group = pygame.sprite.Group()
        self.spawn_timer = 0
        self.next_spawn_time = random.uniform(2.5, 4.5) 
        
        # --- SFX LOADING ---
        try:
            self.collect_sfx = pygame.mixer.Sound("assets/sfx/scrap_pickup.mp3")
            self.collect_sfx.set_volume(0.2)
            self.special_sfx = pygame.mixer.Sound("assets/sfx/special_pickup.mp3") # For cores/batteries
            self.special_sfx.set_volume(0.4)
        except:
            self.collect_sfx = None
            self.special_sfx = None

        path = "assets/sprites/scraps/"
        try:
            self.images = {
                'bolt': pygame.image.load(path + "golden_bolt.png").convert_alpha(),
                'gear': pygame.image.load(path + "heavy bronze gear.png").convert_alpha(),
                'battery': pygame.image.load(path + "glowing_battery.png").convert_alpha(),
                'missile': pygame.image.load(path + "missile_pickup.png").convert_alpha(),
                'bomb': pygame.image.load(path + "gravity_bomb_pickup.png").convert_alpha(),
                'red_core': pygame.image.load(path + "aether_core_red.png").convert_alpha(),
                'tine_soul': pygame.image.load(path + "witch_soul_purple.png").convert_alpha(),
                'gold_oracle': pygame.image.load(path + "goldencore.png").convert_alpha()
            }
        except:
            self.images = {k: pygame.Surface((30, 30)) for k in ['bolt', 'gear', 'battery', 'missile', 'bomb', 'red_core', 'tine_soul', 'gold_oracle']}
            self.images['red_core'].fill((255, 0, 0))
            self.images['tine_soul'].fill((200, 0, 255))
            self.images['gold_oracle'].fill((255, 215, 0))

    def play_pickup_sound(self, scrap_type):
        """Plays the appropriate sound based on what was collected."""
        if scrap_type in ["red_core", "tine_soul", "gold_oracle", "battery"]:
            if self.special_sfx: self.special_sfx.play()
        else:
            if self.collect_sfx: self.collect_sfx.play()

    def spawn_pattern(self):
        roll = random.random()
        start_y = random.randint(100, GROUND_LINE - 200)
        
        if roll < 0.20:
            sub_roll = random.random()
            if sub_roll < 0.55: # Lowered to 10% of the 20% for Cici
                choice = "gold_oracle"
            elif sub_roll < 0.60: 
                choice = "red_core"
            else:
                choice = "tine_soul"
            self.scrap_group.add(Scrap(WIDTH + 100, start_y, choice, self.images))

        elif roll < 0.60:
            choice = random.choice(["bomb", "missile", "battery", "gear"])
            self.scrap_group.add(Scrap(WIDTH + 50, start_y, choice, self.images))
            
        else:
            count = random.randint(6, 12)
            for i in range(count):
                wave_y = start_y + math.sin(i * 0.5) * 25
                self.scrap_group.add(Scrap(WIDTH + (i * 55), wave_y, "bolt", self.images))

    def update(self, dt, player_pos):
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_pattern()
            self.spawn_timer = 0
            self.next_spawn_time = random.uniform(2.5, 4.5) 
            
        self.scrap_group.update(dt, player_pos)
        for scrap in self.scrap_group:
            if scrap.rect.right < -200:
                scrap.kill()

    def draw(self, screen):
        for scrap in self.scrap_group:
            if getattr(scrap, 'is_companion_scrap', False):
                time_val = pygame.time.get_ticks() * 0.005
                pulse = math.sin(time_val) * 8
                glow_size = 55 + pulse
                
                glow_surf = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
                
                if scrap.scrap_type == "red_core":
                    color = (255, 40, 40, 90)
                elif scrap.scrap_type == "tine_soul":
                    color = (160, 40, 255, 90)
                else: 
                    color = (255, 255, 100, 110) 
                
                pygame.draw.circle(glow_surf, color, (int(glow_size), int(glow_size)), int(glow_size))
                pygame.draw.circle(glow_surf, (255, 255, 255, 150), (int(glow_size), int(glow_size)), int(glow_size/2.5))
                
                screen.blit(glow_surf, glow_surf.get_rect(center=scrap.rect.center))
        
        self.scrap_group.draw(screen)