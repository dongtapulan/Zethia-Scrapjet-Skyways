import pygame

class HeatSystem:
    def __init__(self):
        self.heat = 0.0
        self.max_heat = 100.0
        self.is_stalled = False
        self.cough_timer = 0
        # ADD THIS LINE:
        self.base_cool_rate = 35.0 
        
    def add_heat(self, amount):
        if not self.is_stalled:
            self.heat = min(self.max_heat, self.heat + amount)
            if self.heat >= self.max_heat:
                self.is_stalled = True
                return True 
        return False

    def update(self, dt, is_firing):
        # Changed to use self.base_cool_rate so Cici can boost it
        current_cool_speed = 15 if is_firing else self.base_cool_rate
        
        if self.is_stalled:
            current_cool_speed = 25 
            
        self.heat = max(0, self.heat - current_cool_speed * dt)
        
        if self.is_stalled and self.heat <= 0:
            self.is_stalled = False
            
        if self.is_stalled:
            self.cough_timer += dt

    def get_heat_percentage(self):
        return self.heat / self.max_heat