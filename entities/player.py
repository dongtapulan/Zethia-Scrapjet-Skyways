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
            if self.p_type == "fire":
                surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*self.color, 150), (size, size), size)
                screen.blit(surf, (self.pos.x - size, self.pos.y - size))
            else:
                pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)

# --- PLAYER CLASS ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Assets & SFX
        try:
            self.frame_open = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
            self.frame_blink = pygame.image.load("assets/sprites/huey_plane2.png").convert_alpha()
            self.image_crash = pygame.image.load("assets/sprites/huey_planecrash.png").convert_alpha()
        except:
            # Fallback if images are missing
            self.frame_open = pygame.Surface((50, 30))
            self.frame_open.fill((200, 200, 200))
            self.frame_blink = self.frame_open.copy()
            self.image_crash = self.frame_open.copy()
            self.image_crash.fill((100, 100, 100))
    
        try:
            self.sfx_explosion = pygame.mixer.Sound("assets/sfx/explosion.wav")
            self.sfx_explosion.set_volume(0.3)
        except:
            self.sfx_explosion = None

        self.base_image = self.frame_open
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(200, HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.image)
        
        # 2. Systems (References assigned by Game.reset_game)
        self.physics = FlightPhysics()
        self.combat_system = None
        self.heat_system = None
        self.particles = [] 
        self.smoke_timer = 0
        
        # 3. Stats & State
        self.health = PLAYER_HEALTH
        self.is_alive = True
        self.scrap = 0        # FIXED: Added scrap attribute
        self.distance = 0     # FIXED: Initialized distance
        self.heat = 0.0
        self.weight = 0
        self.max_weight = MAX_WEIGHT_CAPACITY 
        self.is_stalled = False
        self.is_skimming = False
        self.leeches = 0
        
        # Secondary Weapons
        self.missiles = 0
        self.max_missiles = 15
        self.bombs = 0
        self.max_bombs = 5
        
        # 4. Death & Crash Sequence
        self.death_timer = 0
        self.has_exploded = False
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1.5 

        # 5. Animation State
        self.blink_timer = 0
        self.is_blinking = False
        self.next_blink_time = random.randint(3000, 6000)
        self.rotation = 0
        self.stall_timer = 0

    def take_damage(self, amount, play_sound=True):
        if self.is_alive and not self.invincible:
            self.health -= amount
            if play_sound and self.sfx_explosion:
                self.sfx_explosion.play()
                
            if self.health <= 0:
                self.health = 0
                self.is_alive = False
                self.death_timer = pygame.time.get_ticks()
            else:
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
            return True 
        return False

    def emit_detailed_particles(self, dt):
        self.smoke_timer += dt
        # Use heat_system if available, otherwise fallback to self.heat
        current_heat = self.heat_system.heat if self.heat_system else self.heat
        heat_ratio = current_heat / HEAT_MAX
        
        spawn_rate = 0.04
        if not self.is_alive:
            spawn_rate = 0.01 
        
        if self.smoke_timer > spawn_rate:
            ex_x, ex_y = self.rect.center
            self.particles.append(Particle(ex_x, ex_y, "smoke", heat_ratio))
            
            if heat_ratio > 0.8 or not self.is_alive:
                self.particles.append(Particle(ex_x, ex_y, "fire"))
                
            self.smoke_timer = 0

    def update(self, dt):
        # Sync with heat system if it exists
        if self.heat_system:
            self.heat = self.heat_system.heat
            self.is_stalled = self.heat_system.is_stalled

        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration * 1000:
                self.invincible = False
            
        self.animate()
        self.apply_tilt()
        self.is_skimming = self.rect.bottom >= GROUND_LINE - 5
        
        # Death Sequence Logic
        if not self.is_alive:
            self.rect.y += (GRAVITY * 0.8) * dt
            self.rect.x += math.sin(pygame.time.get_ticks() * 0.01) * 2
            self.weight = max(0, self.weight - 10 * dt)
            
            time_since_death = (pygame.time.get_ticks() - self.death_timer) / 1000
            if (time_since_death > 2.0 or self.rect.bottom >= HEIGHT) and not self.has_exploded:
                self.trigger_final_explosion()

        # Movement recovery handled by heat system now, but keeping for safety
        if self.is_alive:
            self.handle_recovery(dt)
        
        self.emit_detailed_particles(dt)
        
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)

    def trigger_final_explosion(self):
        self.has_exploded = True
        if self.sfx_explosion:
            self.sfx_explosion.play()
        for _ in range(30):
            ex_x, ex_y = self.rect.center
            self.particles.append(Particle(ex_x, ex_y, "fire"))
            self.particles.append(Particle(ex_x, ex_y, "smoke", 1.0))

    def handle_recovery(self, dt):
        # If no external heat system, handle stall timer locally
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
                # Only apply heat locally if HeatSystem isn't handling it via main.py
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
        
        # Maintain center point during rotation
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
            
        # Flicker effect when invincible
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        if not self.has_exploded:
            screen.blit(self.image, self.rect)