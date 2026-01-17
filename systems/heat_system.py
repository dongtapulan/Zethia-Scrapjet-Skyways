import pygame

class HeatSystem:
    def __init__(self):
        self.heat = 0.0
        self.max_heat = 100.0
        self.is_stalled = False
        self.cough_timer = 0
        
        # Base cooling speed (higher = faster recovery)
        self.base_cool_rate = 45.0 
        # Extra multiplier for when Cici/Companions are active
        self.cooling_multiplier = 1.0 
        
    def add_heat(self, amount):
        if not self.is_stalled:
            self.heat = min(self.max_heat, self.heat + amount)
            if self.heat >= self.max_heat:
                self.is_stalled = True
                return True 
        return False

    def update(self, dt, is_firing):
        # Calculate final cooling speed with potential buffs
        eff_cool_rate = self.base_cool_rate * self.cooling_multiplier
        
        # If firing, you cool down slower; if not, you use full effective rate
        current_cool_speed = 15.0 if is_firing else eff_cool_rate
        
        # If stalled (overheated), we force a steady recovery rate
        if self.is_stalled:
            current_cool_speed = 35.0 # Faster than before to get you back in the fight
            
        self.heat = max(0, self.heat - current_cool_speed * dt)
        
        # Reset stall once heat reaches zero
        if self.is_stalled and self.heat <= 0:
            self.is_stalled = False
            
        if self.is_stalled:
            self.cough_timer += dt

    def apply_cici_boost(self, active):
        """Called by CompanionManager. If Cici is active, boost cooling by 50%."""
        if active:
            self.cooling_multiplier = 1.5
        else:
            self.cooling_multiplier = 1.0

    def get_heat_percentage(self):
        return self.heat / self.max_heat