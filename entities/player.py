import pygame
import random
from settings import *
from core.physics import FlightPhysics

# --- PARTICLE CLASS (No changes needed, but kept for completeness) ---
class Particle:
    def __init__(self, x, y, heat_ratio, weight_ratio):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-150, -80), random.uniform(-30, 30))
        self.life = 1.0  
        self.decay = random.uniform(1.0, 2.5) 
        
        if heat_ratio > 0.8:
            self.color = [random.randint(200, 255), random.randint(50, 100), 50] 
        elif weight_ratio > 0.6:
            grey = random.randint(50, 80) 
            self.color = [grey, grey, grey]
        else:
            grey = random.randint(180, 230) 
            self.color = [grey, grey, grey]

        self.base_size = 4 + (weight_ratio * 10)

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= self.decay * dt

    def draw(self, screen):
        size = int(self.life * self.base_size)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)

# --- PLAYER CLASS ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Animation Frames
        self.frame_open = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
        self.frame_blink = pygame.image.load("assets/sprites/huey_plane2.png").convert_alpha()
        
        self.base_image = self.frame_open
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(200, HEIGHT // 2))
        
        # 2. Systems
        self.physics = FlightPhysics()
        self.particles = [] 
        self.smoke_timer = 0
        
        # 3. Stats & State
        self.health = PLAYER_HEALTH
        self.heat = 0.0
        self.weight = 0
        self.max_weight = MAX_WEIGHT_CAPACITY # Updated to use your new setting
        self.is_stalled = False
        self.is_skimming = False
        self.leeches = 0
        self.stall_timer = 0
        
        # 4. Animation State
        self.blink_timer = 0
        self.is_blinking = False
        self.next_blink_time = random.randint(3000, 6000)
        self.rotation = 0  

    def shed_weight(self):
        """Called by ProjectileManager when Huey fires his gun."""
        if self.weight > 0:
            self.weight = max(0, self.weight - BULLET_SHED_AMOUNT)

    def emit_smoke(self, dt):
        self.smoke_timer += dt
        heat_ratio = self.heat / HEAT_MAX
        # Smoke gets bigger only after passing the Free Zone
        effective_weight_ratio = max(0, self.weight - WEIGHT_FREE_ZONE) / self.max_weight
        
        spawn_rate = max(0.01, 0.05 - (effective_weight_ratio * 0.03) - (heat_ratio * 0.01))
        
        if self.smoke_timer > spawn_rate:
            exhaust_x = self.rect.left + 5
            exhaust_y = self.rect.centery + 5
            self.particles.append(Particle(exhaust_x, exhaust_y, heat_ratio, effective_weight_ratio))
            self.smoke_timer = 0

    def handle_cooling(self, dt, thrust_active):
        if self.is_stalled:
            self.heat = max(0, self.heat - (HEAT_MAX / OVERHEAT_STALL_TIME) * dt)
        elif not thrust_active:
            cooldown_rate = HEAT_COOLDOWN_SKIM if self.is_skimming else HEAT_COOLDOWN_AIR
            self.heat = max(0, self.heat - (cooldown_rate * dt))

    def handle_stall(self, dt):
        if self.is_stalled:
            now = pygame.time.get_ticks()
            if now - self.stall_timer > OVERHEAT_STALL_TIME * 1000:
                self.is_stalled = False

    def handle_input(self, flight_input, dt):
        thrust_active = False
        is_holding = False

        if not self.is_stalled:
            if flight_input["thrust"]:
                thrust_active = True
                is_holding = flight_input["is_holding"]
                self.apply_heat(dt, is_holding)
        
        self.handle_cooling(dt, thrust_active)

        # Update physics with total weight
        self.physics.is_stalled = self.is_stalled
        total_extra_weight = self.leeches + self.weight
        self.physics.add_leech_weight(total_extra_weight) 
        
        self.rect.y = self.physics.apply_forces(
            self.rect.y, thrust_active, is_holding, dt, self.rect.height
        )

    def apply_heat(self, dt, is_holding):
        rate = HEAT_GAIN_HOLD if is_holding else HEAT_GAIN_TAP
        self.heat += rate * dt
        if self.heat >= HEAT_MAX:
            self.heat = HEAT_MAX
            self.is_stalled = True
            self.stall_timer = pygame.time.get_ticks()

    def update(self, dt):
        self.animate()
        self.apply_tilt()
        self.is_skimming = self.rect.bottom >= GROUND_LINE - 5
        self.handle_stall(dt)
        self.emit_smoke(dt)
        
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)

    def animate(self):
        now = pygame.time.get_ticks()
        if self.is_stalled:
            self.base_image = self.frame_blink
        elif not self.is_blinking:
            if now - self.blink_timer > self.next_blink_time:
                self.is_blinking = True
                self.base_image = self.frame_blink
                self.blink_timer = now
        else:
            if now - self.blink_timer > 150:
                self.is_blinking = False
                self.base_image = self.frame_open
                self.blink_timer = now
                self.next_blink_time = random.randint(3000, 6000)

    def apply_tilt(self):
        target_rotation = self.physics.velocity_y * -2.5
        target_rotation = max(-25, min(15, target_rotation))
        self.rotation += (target_rotation - self.rotation) * 0.1
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen):
        # 1. Particles (Back layer)
        for p in self.particles:
            p.draw(screen)
            
        # 2. Plane
        screen.blit(self.image, self.rect)
        # Note: HUD Bars removed from here as they are now in HUD class