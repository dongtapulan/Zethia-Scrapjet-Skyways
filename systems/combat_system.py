import pygame
import random
from entities.projectiles import ProjectileManager

class CombatSystem:
    def __init__(self, game):
        self.game = game 
        self.manager = ProjectileManager()
        self.selected_weapon = "machine_gun"
        
        # --- NEW STATE FOR SPECIALS ---
        self.laser_active = False 

    def fire(self, player, enemies, dt):
        if self.selected_weapon == "machine_gun":
            if self.manager.fire_machine_gun(player, enemies, dt):
                return 5.0 
                
        elif self.selected_weapon == "missile":
            self.manager.launch_missile(player, enemies)
            return 0.0 
            
        elif self.selected_weapon == "gravity_bomb":
            self.manager.trigger_gravity_bomb(player, enemies)
            return 0.0
            
        return 0.0

    # --- NEW: TINE'S LIGHTNING (Triggered once per press) ---
    def trigger_lightning(self, player, enemies):
        """Finds targets and tells the manager to draw/damage with lightning."""
        # Find all enemies on screen
        targets = [e for e in enemies if e.rect.right > 0 and e.rect.left < 1280]
        if targets:
            # Sort by distance to player to hit the closest ones
            targets.sort(key=lambda e: pygame.math.Vector2(e.rect.center).distance_to(player.rect.center))
            # Pick up to 3 targets for a 'chain' effect
            chain_targets = targets[:3]
            self.manager.spawn_lightning(player.rect.center, chain_targets)

    # --- NEW: RED'S LASER (Continuous while holding) ---
    def fire_laser(self, player, enemies, dt):
        """Continuously drains fuel and damages enemies in a line."""
        if player.laser_fuel > 0:
            player.laser_fuel -= 50 * dt # Drains 50 fuel per second
            self.laser_active = True
            # Tell manager to process the beam collision and visuals
            self.manager.process_laser_beam(player, enemies)
            return True
        else:
            self.laser_active = False
            return False

    def update(self, dt):
        self.manager.update(dt)
        # Reset laser state every frame; if F is held, fire_laser will turn it back on
        self.laser_active = False 

    def draw(self, screen):
        self.manager.draw(screen)