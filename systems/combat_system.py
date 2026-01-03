import pygame
from entities.projectiles import ProjectileManager

class CombatSystem:
    def __init__(self, game):
        self.game = game  # Reference to access enemy_manager and player
        self.manager = ProjectileManager()
        self.selected_weapon = "machine_gun" # machine_gun, missile, gravity_bomb
        
    def fire(self, player, enemies, dt):
        if self.selected_weapon == "machine_gun":
            # Add heat only for machine gun
            if self.manager.fire_machine_gun(player, dt):
                return 5.0 # Return heat amount
        elif self.selected_weapon == "missile":
            self.manager.launch_missile(player, enemies)
        return 0.0

    def update(self, dt):
        self.manager.update(dt)
        # Collision logic is handled in main.py _handle_collisions for now
        # but having the game reference here allows for future expansion.

    def draw(self, screen):
        self.manager.draw(screen)