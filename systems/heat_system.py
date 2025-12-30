import pygame

class HeatSystem:
    def __init__(self):
        self.heat = 0.0
        self.max_heat = 100.0
        self.is_overheating = False
        self.cough_timer = 0
        
    def add_heat(self, amount):
        self.heat = min(self.max_heat, self.heat + amount)
        if self.heat >= self.max_heat:
            self.is_overheating = True

    def update(self, dt, is_firing):
        # Cooling logic: Cools faster if not firing
        cool_rate = 15 if is_firing else 35
        self.heat = max(0, self.heat - cool_rate * dt)
        
        if self.is_overheating and self.heat <= 0:
            self.is_overheating = False

    def get_heat_percentage(self):
        return self.heat / self.max_heat