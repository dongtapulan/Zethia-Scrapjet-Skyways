import pygame
import random
import math
from settings import *
from core.physics import FlightPhysics

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. Load Animation Frames
        self.frame_open = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
        self.frame_blink = pygame.image.load("assets/sprites/huey_plane2.png").convert_alpha()
        
        # Base image for rotation to prevent pixel degradation
        self.base_image = self.frame_open
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(200, HEIGHT // 2))
        
        # 2. Animation & Tilt State
        self.blink_timer = 0
        self.is_blinking = False
        self.next_blink_time = random.randint(3000, 6000)
        self.rotation = 0  
        
        # 3. Systems
        self.physics = FlightPhysics()
        
        # 4. Stats & State
        self.health = PLAYER_HEALTH
        self.heat = 0.0
        self.is_stalled = False
        self.is_skimming = False
        self.leeches = 0
        self.stall_timer = 0

    def apply_heat(self, dt, is_holding):
        """Calculates heat gain and triggers stall if limit is reached."""
        rate = HEAT_GAIN_HOLD if is_holding else HEAT_GAIN_TAP
        self.heat += rate * dt
        
        if self.heat >= HEAT_MAX:
            self.heat = HEAT_MAX
            self.is_stalled = True
            self.stall_timer = pygame.time.get_ticks()

    def animate(self):
        """Handles blinking logic."""
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
        """Tilts the plane based on vertical velocity."""
        # Use velocity to determine tilt (-25 to 15 degrees)
        target_rotation = self.physics.velocity_y * -2.5
        target_rotation = max(-25, min(15, target_rotation))
        
        # Smooth interpolation (Lerp)
        self.rotation += (target_rotation - self.rotation) * 0.1
        
        # Rotate the current base image
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        
        # Re-center the rect to prevent 'vibration' during rotation
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt):
        self.animate()
        self.apply_tilt()
        
        # --- Cooling Logic ---
        # Note: We check if the bottom of the plane is touching the GROUND_LINE
        if self.rect.bottom >= GROUND_LINE - 2: 
            self.is_skimming = True
            self.heat = max(0, self.heat - (HEAT_COOLDOWN_SKIM * dt))
        else:
            self.is_skimming = False
            self.heat = max(0, self.heat - (HEAT_COOLDOWN_AIR * dt))

        # --- Stall Recovery ---
        if self.is_stalled:
            now = pygame.time.get_ticks()
            if now - self.stall_timer > OVERHEAT_STALL_TIME * 1000:
                self.is_stalled = False

    def handle_input(self, keys, dt):
        thrust_active = False
        is_holding = False

        if not self.is_stalled:
            if keys[pygame.K_SPACE]:
                thrust_active = True
                is_holding = True 
                self.apply_heat(dt, is_holding)

        # Update physics state
        self.physics.is_stalled = self.is_stalled
        self.physics.add_leech_weight(self.leeches)
        
        # IMPORTANT: We update rect.y with the result of physics
        # If this isn't changing, Huey won't move!
        self.rect.y = self.physics.apply_forces(
            self.rect.y, 
            thrust_active, 
            is_holding, 
            dt, 
            self.rect.height
        )

    def draw_hud_elements(self, screen):
        """Draws the mini heat-bar above the player."""
        bar_width, bar_height = 64, 8
        heat_ratio = min(self.heat / HEAT_MAX, 1.0)
        
        bar_x = self.rect.x
        bar_y = self.rect.y - 20
        
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        color = WHITE if self.is_stalled else (HEAT_RED if self.heat < 80 else (255, 150, 0))
        pygame.draw.rect(screen, color, (bar_x, bar_y, heat_ratio * bar_width, bar_height))