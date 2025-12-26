import pygame
from settings import *

class FlightPhysics:
    def __init__(self):
        self.velocity_y = 0
        self.weight_multiplier = 1.0
        self.is_stalled = False

    def apply_forces(self, current_y, thrust_input, is_holding, dt, sprite_height):
        # 1. Gravity (Always pulling down)
        total_gravity = GRAVITY * self.weight_multiplier
        
        # 2. Thrust (Pulling UP)
        thrust = 0
        if not self.is_stalled and thrust_input:
            # Multiplied by a factor to make thrust feel punchy against gravity
            thrust = -EMERGENCY_THRUST if is_holding else -THRUST_FORCE

        # 3. Acceleration
        acceleration_y = total_gravity + thrust
        
        # 4. Update Velocity
        # We apply acceleration over time
        self.velocity_y += acceleration_y * dt
        self.velocity_y *= DRAG 

        # 5. Clamp to Terminal Velocity
        if self.velocity_y > TERMINAL_VELOCITY:
            self.velocity_y = TERMINAL_VELOCITY

        # 6. Calculate New Position (THE FIX IS HERE)
        # We multiply by dt * 60 to translate velocity into actual pixel movement
        new_y = current_y + (self.velocity_y * dt * 60)

        # 7. Collision: Ceiling
        if new_y < 0:
            new_y = 0
            self.velocity_y = 0

        # 8. Collision: Ground
        if new_y + sprite_height > GROUND_LINE:
            new_y = GROUND_LINE - sprite_height
            # If we hit the ground while falling, reset velocity so we don't 'store' gravity
            if self.velocity_y > 0:
                self.velocity_y = 0
            
        return new_y

    def reset_momentum(self):
        self.velocity_y = 0

    def add_leech_weight(self, count):
        self.weight_multiplier = 1.0 + (count * LEECH_WEIGHT_PENALTY)