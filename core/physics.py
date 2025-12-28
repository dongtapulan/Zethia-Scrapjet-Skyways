import pygame
from settings import *

class FlightPhysics:
    def __init__(self):
        self.velocity_y = 0
        self.raw_weight = 0  # We'll track the actual scrap weight here
        self.is_stalled = False

    def add_leech_weight(self, weight_value):
        """Updates the raw weight value from the player."""
        self.raw_weight = weight_value

    def apply_forces(self, current_y, thrust_input, is_holding, dt, sprite_height):
        # 1. Calculate Effective Weight (The 'Free Zone' Logic)
        # Only weight above the buffer starts pulling the plane down
        effective_weight = max(0, self.raw_weight - WEIGHT_FREE_ZONE)
        
        # 2. Gravity Calculation
        # Base gravity + (extra weight * how much each unit of weight hurts)
        total_gravity = GRAVITY + (effective_weight * WEIGHT_GRAVITY_SCALER)
        
        # 3. Thrust (Pulling UP)
        thrust = 0
        if not self.is_stalled and thrust_input:
            # Multiplied by a factor to make thrust feel punchy against gravity
            thrust = -EMERGENCY_THRUST if is_holding else -THRUST_FORCE

        # 4. Acceleration
        acceleration_y = total_gravity + thrust
        
        # 5. Update Velocity
        self.velocity_y += acceleration_y * dt
        self.velocity_y *= DRAG 

        # 6. Clamp to Terminal Velocity
        # Prevents the plane from falling at infinite speed
        if self.velocity_y > TERMINAL_VELOCITY:
            self.velocity_y = TERMINAL_VELOCITY

        # 7. Calculate New Position
        # Velocity * dt * 60 converts speed to pixel movement
        new_y = current_y + (self.velocity_y * dt * 60)

        # 8. Collision: Ceiling
        if new_y < 0:
            new_y = 0
            self.velocity_y = 0

        # 9. Collision: Ground
        if new_y + sprite_height > GROUND_LINE:
            new_y = GROUND_LINE - sprite_height
            # Reset velocity on impact so gravity doesn't "accumulate" while landed
            if self.velocity_y > 0:
                self.velocity_y = 0
            
        return new_y

    def reset_momentum(self):
        self.velocity_y = 0