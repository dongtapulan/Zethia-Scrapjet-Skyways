import pygame
import random
import json
import os

class UpgradeManager:
    def __init__(self):
        self.save_file = "save_data.json"
        
        # Currency (Permanent)
        self.total_bolts = 0
        
        # --- PERMANENT STAT LEVELS ---
        # Current Level, Max Level, Base Cost
        self.stats = {
            "Engine Cooling": {"level": 0, "max": 5, "cost": 150},
            "Magnetic Hull":  {"level": 0, "max": 5, "cost": 100},
            "Hull Integrity": {"level": 0, "max": 5, "cost": 200},
            "Ammo Feed":      {"level": 0, "max": 5, "cost": 250}
        }

        self.unlocked_overclocks = []
        self.available_overclocks = [
            {"name": "Splitter Rounds", "desc": "Bullets have a 10% chance to pierce.", "cost": 1000},
            {"name": "Gravity Well", "desc": "Gravity Bomb pulls enemies inward.", "cost": 1500},
            {"name": "Afterburners", "desc": "Reduced speed penalty when heavy.", "cost": 1200}
        ]
        
        # Load any existing save data on initialization
        self.load_game()

    # --- SAVE / LOAD LOGIC ---

    def save_game(self):
        """Writes current progress to a JSON file."""
        data = {
            "bolts": self.total_bolts,
            "stats": {k: v["level"] for k, v in self.stats.items()},
            "overclocks": self.unlocked_overclocks
        }
        try:
            with open(self.save_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self):
        """Reads progress from JSON file if it exists."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    self.total_bolts = data.get("bolts", 0)
                    saved_stats = data.get("stats", {})
                    for name, level in saved_stats.items():
                        if name in self.stats:
                            self.stats[name]["level"] = level
                    self.unlocked_overclocks = data.get("overclocks", [])
            except Exception as e:
                print(f"Error loading game: {e}")

    # --- CURRENCY LOGIC ---

    def convert_score_to_bolts(self, score):
        """Converts Arcade score to permanent currency at the end of a run."""
        earned = int(score * 0.10)
        self.total_bolts += earned
        self.save_game() 
        return earned

    # --- UPGRADE LOGIC ---

    def get_upgrade_cost(self, stat_name):
        stat = self.stats[stat_name]
        return int(stat["cost"] * (1.5 ** stat["level"]))

    def attempt_upgrade(self, stat_name, player=None):
        """Handles the logic of spending bolts. Player is optional for menu-use."""
        if stat_name not in self.stats:
            return False

        stat = self.stats[stat_name]
        cost = self.get_upgrade_cost(stat_name)

        if stat["level"] < stat["max"] and self.total_bolts >= cost:
            self.total_bolts -= cost
            stat["level"] += 1
            
            # Save the new level to disk immediately
            self.save_game()
            
            # Only try to modify a player if one is actually provided (not in menus)
            if player:
                self._apply_stat_boost(stat_name, player)
            return True
        return False

    def _apply_stat_boost(self, stat_name, player):
        """Safely modifies player variables based on current levels."""
        if player is None:
            return

        level = self.stats[stat_name]["level"]
        
        if stat_name == "Engine Cooling":
            # Update the max heat capacity
            if hasattr(player, 'heat_system'):
                player.heat_system.max_heat = 100 + (level * 15)
                
        elif stat_name == "Magnetic Hull":
            # Increase collection range
            player.collection_range = 60 + (level * 25)
            
        elif stat_name == "Hull Integrity":
            # Increase Max HP and heal
            player.max_health = 100 + (level * 25)
            player.health = player.max_health
            
        elif stat_name == "Ammo Feed":
            # Access the manager inside the combat system to change fire rate
            if hasattr(player, 'combat_system') and player.combat_system.manager:
                player.combat_system.manager.fire_rate = max(0.04, 0.08 - (level * 0.008))

    def apply_all_upgrades(self, player):
        """Called by main.py during reset_game() to sync ship with workshop levels."""
        if player is None:
            return
            
        for stat_name in self.stats:
            self._apply_stat_boost(stat_name, player)