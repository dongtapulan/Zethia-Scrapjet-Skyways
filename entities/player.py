import pygame
import random
import math
from settings import *
from core.physics import FlightPhysics

# --- ENHANCED PARTICLE CLASS ---
class Particle:
    def __init__(self, x, y, p_type="smoke", heat_ratio=0.0):
        self.pos = pygame.Vector2(x, y)
        if p_type == "fire":
            self.vel = pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
            self.color = [255, random.randint(100, 200), 50]
            self.life = random.uniform(0.5, 0.8)
            self.base_size = random.randint(4, 8)
        elif p_type == "shield_spark":
            self.vel = pygame.Vector2(random.uniform(-50, -20), random.uniform(-30, 30))
            self.color = [150, 100, 255] 
            self.life = 0.6
            self.base_size = random.randint(2, 4)
        else: # Smoke
            self.vel = pygame.Vector2(random.uniform(-180, -100), random.uniform(-40, 20))
            grey = random.randint(40, 100) if heat_ratio > 0.7 else random.randint(150, 200)
            self.color = [grey, grey, grey]
            self.life = 1.2
            self.base_size = random.randint(3, 6)
            
        self.decay = random.uniform(1.2, 2.0)
        self.p_type = p_type

    def update(self, dt):
        self.pos += self.vel * dt
        if self.p_type == "smoke":
            self.vel.y -= 10 * dt 
        self.life -= self.decay * dt

    def draw(self, screen):
        if self.life > 0:
            size = int(self.life * self.base_size)
            if self.p_type in ["fire", "shield_spark"]:
                surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                alpha = 150 if self.p_type == "fire" else 200
                pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
                screen.blit(surf, (self.pos.x - size, self.pos.y - size))
            else:
                pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)

# --- PLAYER CLASS ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Assets
        try:
            self.frame_open = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
            self.frame_blink = pygame.image.load("assets/sprites/huey_plane2.png").convert_alpha()
            self.image_crash = pygame.image.load("assets/sprites/huey_planecrash.png").convert_alpha()
        except:
            self.frame_open = pygame.Surface((50, 30)); self.frame_open.fill((200, 200, 200))
            self.frame_blink = self.frame_open.copy()
            self.image_crash = self.frame_open.copy(); self.image_crash.fill((100, 100, 100))
    
        # --- AUDIO SYSTEM ---
        try:
            self.sfx_explosion = pygame.mixer.Sound("assets/sfx/explosion.wav")
            self.sfx_engine = pygame.mixer.Sound("assets/sfx/engine_loop.mp3")
            self.sfx_stall = pygame.mixer.Sound("assets/sfx/engine_stall.mp3") 
            
            # New Weapon SFX
            self.sfx_lightning = pygame.mixer.Sound("assets/sfx/tine_lightning.mp3")
            self.sfx_laser_loop = pygame.mixer.Sound("assets/sfx/Red_Laser.mp3")
            
            # Volume adjustments
            self.sfx_lightning.set_volume(0.6)
            self.sfx_laser_loop.set_volume(0.4)

            # Dedicated Channels
            self.engine_channel = pygame.mixer.find_channel()
            self.laser_channel = pygame.mixer.find_channel() # Continuous channel for Red's Laser

            if self.engine_channel:
                self.engine_channel.play(self.sfx_engine, loops=-1)
                self.engine_channel.set_volume(0.1)
        except:
            self.sfx_explosion = self.sfx_engine = self.sfx_stall = None
            self.sfx_lightning = self.sfx_laser_loop = None
            self.engine_channel = self.laser_channel = None

        self.base_image = self.frame_open
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(200, HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.image)
        
        # 2. Systems
        self.physics = FlightPhysics()
        self.combat_system = None
        self.heat_system = None
        self.particles = [] 
        self.smoke_timer = 0
        self.magnet_pulse = 0 
        
        # 3. Stats & State
        self.health = PLAYER_HEALTH
        self.is_alive = True
        self.scrap = 0
        self.distance = 0
        self.heat = 0.0
        self.weight = 0
        self.max_weight = MAX_WEIGHT_CAPACITY 
        self.is_stalled = False
        self.is_skimming = False
        self.leeches = 0
        
        # Weapons
        self.missiles = 0
        self.max_missiles = 15
        self.bombs = 0
        self.max_bombs = 5
        self.lightning_charges = 0
        self.max_lightning_charges = 3
        self.laser_fuel = 0.0
        self.max_laser_fuel = 100.0
        
        # 4. State Management
        self.death_timer = 0
        self.has_exploded = False
        self.invincible = False
        self.is_invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1.5 

        # 5. Animation
        self.blink_timer = 0
        self.is_blinking = False
        self.next_blink_time = random.randint(3000, 6000)
        self.rotation = 0
        self.stall_timer = 0

    def play_lightning_sfx(self):
        """Called by main.py when Q is pressed."""
        if self.sfx_lightning:
            self.sfx_lightning.play()

    def update_laser_audio(self, is_firing):
        """Manages the looping laser sound."""
        if not self.laser_channel or not self.sfx_laser_loop:
            return
            
        if is_firing and self.is_alive and self.laser_fuel > 0:
            if not self.laser_channel.get_busy():
                self.laser_channel.play(self.sfx_laser_loop, loops=-1)
        else:
            self.laser_channel.stop()

    def take_damage(self, amount, play_sound=True):
        if not self.is_alive or self.invincible or self.is_invincible:
            return False

        self.health -= amount
        if play_sound and self.sfx_explosion:
            self.sfx_explosion.play()
            
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.death_timer = pygame.time.get_ticks()
            if self.engine_channel: self.engine_channel.stop()
            if self.laser_channel: self.laser_channel.stop()
        else:
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
        return True 

    def update(self, dt):
        if self.heat_system:
            self.heat = self.heat_system.heat
            if self.heat_system.is_stalled and not self.is_stalled:
                if self.sfx_stall: self.sfx_stall.play()
            self.is_stalled = self.heat_system.is_stalled

        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration * 1000:
                self.invincible = False
            
        self.animate()
        self.apply_tilt()
        self.update_engine_audio()
        
        # Laser audio logic is checked every frame
        keys = pygame.key.get_pressed()
        self.update_laser_audio(keys[pygame.K_e])

        self.is_skimming = self.rect.bottom >= GROUND_LINE - 5
        self.magnet_pulse += 5 * dt
        
        if not self.is_alive:
            self.rect.y += (GRAVITY * 0.8) * dt
            self.rect.x += math.sin(pygame.time.get_ticks() * 0.01) * 2
            
            time_since_death = (pygame.time.get_ticks() - self.death_timer) / 1000
            if (time_since_death > 2.0 or self.rect.bottom >= HEIGHT) and not self.has_exploded:
                self.trigger_final_explosion()

        if self.is_alive:
            self.handle_recovery(dt)
        
        self.emit_detailed_particles(dt)
        
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)

    def update_engine_audio(self):
        if not self.is_alive or not self.engine_channel:
            return
        vol = 0.1
        strain = abs(self.physics.velocity_y) / 500
        vol += strain * 0.1
        heat_ratio = self.heat / HEAT_MAX
        if heat_ratio > 0.7:
            vol += 0.1 + (math.sin(pygame.time.get_ticks() * 0.05) * 0.05)
        self.engine_channel.set_volume(min(0.4, vol))

    def trigger_final_explosion(self):
        self.has_exploded = True
        if self.sfx_explosion:
            self.sfx_explosion.play()
        for _ in range(30):
            ex_x, ex_y = self.rect.center
            self.particles.append(Particle(ex_x, ex_y, "fire"))
            self.particles.append(Particle(ex_x, ex_y, "smoke", 1.0))

    def emit_detailed_particles(self, dt):
        self.smoke_timer += dt
        current_heat = self.heat_system.heat if self.heat_system else self.heat
        heat_ratio = current_heat / HEAT_MAX
        spawn_rate = 0.04
        if not self.is_alive: spawn_rate = 0.01 
        
        if self.smoke_timer > spawn_rate:
            ex_x, ex_y = self.rect.center
            self.particles.append(Particle(ex_x, ex_y, "smoke", heat_ratio))
            if heat_ratio > 0.8 or not self.is_alive:
                self.particles.append(Particle(ex_x, ex_y, "fire"))
            self.smoke_timer = 0

    def handle_recovery(self, dt):
        if not self.heat_system and self.is_stalled:
            if pygame.time.get_ticks() - self.stall_timer > OVERHEAT_STALL_TIME * 1000:
                self.is_stalled = False

    def handle_input(self, flight_input, dt):
        if not self.is_alive: return
        thrust_active = False
        is_holding = False
        if not self.is_stalled:
            if flight_input["thrust"]:
                thrust_active = True
                is_holding = flight_input["is_holding"]
                if not self.heat_system:
                    self.apply_heat(dt, is_holding)
        
        if not self.heat_system and not thrust_active:
            cooldown_rate = HEAT_COOLDOWN_SKIM if self.is_skimming else HEAT_COOLDOWN_AIR
            self.heat = max(0, self.heat - (cooldown_rate * dt))
        
        self.physics.is_stalled = self.is_stalled
        self.physics.add_leech_weight(self.leeches + self.weight) 
        self.rect.y = self.physics.apply_forces(
            self.rect.y, thrust_active, is_holding, dt, self.rect.height
        )

    def apply_heat(self, dt, is_holding):
        rate = HEAT_GAIN_HOLD if is_holding else HEAT_GAIN_TAP
        self.heat += rate * dt
        if self.heat >= HEAT_MAX:
            self.heat = HEAT_MAX
            self.is_stalled = True
            if self.sfx_stall: self.sfx_stall.play()
            self.stall_timer = pygame.time.get_ticks()

    def animate(self):
        now = pygame.time.get_ticks()
        if not self.is_alive:
            self.base_image = self.image_crash
            return
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
        if not self.is_alive:
            target_rotation = -30 
        else:
            target_rotation = self.physics.velocity_y * -2.5
            target_rotation = max(-25, min(15, target_rotation))
        self.rotation += (target_rotation - self.rotation) * 0.1
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        if self.is_alive:
            pulse_val = (math.sin(self.magnet_pulse) + 1) * 5
            pygame.draw.circle(screen, (0, 200, 255, 30), self.rect.center, 150 + int(pulse_val), 1)
        for p in self.particles:
            p.draw(screen)
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            return
        if not self.has_exploded:
            screen.blit(self.image, self.rect)