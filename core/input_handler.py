import pygame

class InputHandler:
    def __init__(self):
        self.hold_threshold = 150  # milliseconds to distinguish tap vs hold
        self.space_pressed_time = 0
        self.is_holding_space = False

    def get_flight_input(self):
        """
        Returns a dictionary containing the state of the flight controls.
        """
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        # Check for sustained thrust
        if keys[pygame.K_SPACE]:
            if not self.is_holding_space:
                self.space_pressed_time = now
                self.is_holding_space = True
            
            hold_duration = now - self.space_pressed_time
            is_sustained = hold_duration > self.hold_threshold
            return {"thrust": True, "is_holding": is_sustained}
        else:
            self.is_holding_space = False
            return {"thrust": False, "is_holding": False}

    def get_combat_input(self):
        keys = pygame.key.get_pressed()
        return {
            "firing": keys[pygame.K_f] or keys[pygame.K_z],
            "special": keys[pygame.K_x]
        }