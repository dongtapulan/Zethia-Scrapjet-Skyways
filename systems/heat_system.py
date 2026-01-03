import pygame

class HeatSystem:
    def __init__(self):
        self.heat = 0.0
        self.max_heat = 100.0
        self.is_stalled = False  # Changed from is_overheating to match Player.py
        self.cough_timer = 0
        
    def add_heat(self, amount):
        if not self.is_stalled:
            self.heat = min(self.max_heat, self.heat + amount)
            if self.heat >= self.max_heat:
                self.is_stalled = True
                return True # Signal that we just hit max heat
        return False

    def update(self, dt, is_firing):
        # Cooling logic: Cools faster if not firing
        # Skimming cooling (optional) could be added here if passed from game
        cool_rate = 15 if is_firing else 35
        
        if self.is_stalled:
            # While stalled, we might want a different cooling rate 
            # or wait until it hits 0 to recover
            cool_rate = 25 
            
        self.heat = max(0, self.heat - cool_rate * dt)
        
        # Recovery logic
        if self.is_stalled and self.heat <= 0:
            self.is_stalled = False
            
        # Update cough/quip timer
        if self.is_stalled:
            self.cough_timer += dt

    def get_heat_percentage(self):
        return self.heat / self.max_heat