import pygame
from entities.projectiles import ProjectileManager

class CombatSystem:
    def __init__(self, game):
        self.game = game  # Reference to access enemy_manager and player
        self.manager = ProjectileManager()
        self.selected_weapon = "machine_gun" # machine_gun, missile, gravity_bomb
        
    def fire(self, player, enemies, dt):
        """
        Processes firing logic based on selected weapon.
        Now passes 'enemies' to all projectile methods to enable the damage system.
        """
        if self.selected_weapon == "machine_gun":
            # Pass 'enemies' as the second argument before 'dt'
            if self.manager.fire_machine_gun(player, enemies, dt):
                return 5.0 # Return heat amount
                
        elif self.selected_weapon == "missile":
            self.manager.launch_missile(player, enemies)
            return 0.0 # Adjust heat/cooldown if needed
            
        elif self.selected_weapon == "gravity_bomb":
            # Added support for gravity bomb
            self.manager.trigger_gravity_bomb(player, enemies)
            return 0.0
            
        return 0.0

    def update(self, dt):
        self.manager.update(dt)

    def draw(self, screen):
        self.manager.draw(screen)