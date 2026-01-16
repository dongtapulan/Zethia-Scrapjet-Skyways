import pygame
import json
import os

class UpgradeManager:
    def __init__(self):
        self.save_file = "save_data.json"
        self.total_bolts = 0
        
        # KEY NAMES NOW MATCH main.py FOR PERFECT SYNC
        self.stats = {
            "Engine Cooling": {"level": 0, "max": 5, "cost": 150},
            "Magnetic Hull":  {"level": 0, "max": 5, "cost": 100},
            "Hull Integrity": {"level": 0, "max": 5, "cost": 200},
            "Ammo Feed":      {"level": 0, "max": 5, "cost": 250},
            
            # ORDINANCE: These are consumables bought for the next run
            "missiles":          {"level": 0, "max": 20, "cost": 75, "per_buy": 5},   
            "lightning_charges": {"level": 0, "max": 9, "cost": 150, "per_buy": 3},  
            "laser_fuel":        {"level": 0, "max": 500, "cost": 200, "per_buy": 100},
            "bombs":             {"level": 0, "max": 5, "cost": 300, "per_buy": 1}
        }

        self.unlocked_overclocks = []
        self.load_game()

    def save_game(self):
        data = {
            "bolts": self.total_bolts,
            "stats": {k: v["level"] for k, v in self.stats.items()},
            "overclocks": self.unlocked_overclocks
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_game(self):
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
            except:
                print("Save file corrupted, starting fresh.")

    def convert_score_to_bolts(self, score):
        """Converts game score to permanent currency after death."""
        earned = score // 100
        self.total_bolts += earned
        self.save_game()

    def get_upgrade_cost(self, stat_name):
        stat = self.stats[stat_name]
        # Consumables stay at a flat price
        if stat_name in ["missiles", "lightning_charges", "laser_fuel", "bombs"]:
            return stat["cost"]
        # Permanent upgrades get more expensive
        return int(stat["cost"] * (1.5 ** stat["level"]))

    def attempt_upgrade(self, stat_name, player=None):
        if stat_name not in self.stats: return False
        stat = self.stats[stat_name]
        cost = self.get_upgrade_cost(stat_name)

        if stat["level"] < stat["max"] and self.total_bolts >= cost:
            self.total_bolts -= cost
            
            if "per_buy" in stat: # It's a consumable
                stat["level"] += stat["per_buy"]
            else: # It's a permanent stat
                stat["level"] += 1
            
            self.save_game()
            if player: self._apply_stat_boost(stat_name, player)
            return True
        return False

    def _apply_stat_boost(self, stat_name, player):
        level = self.stats[stat_name]["level"]
        
        # Permanent Stats
        if stat_name == "Engine Cooling":
            player.heat_system.max_heat = 100 + (level * 15)
        elif stat_name == "Magnetic Hull":
            player.collection_range = 60 + (level * 25)
        elif stat_name == "Hull Integrity":
            player.max_health = 100 + (level * 25)
            player.health = player.max_health
        elif stat_name == "Ammo Feed":
            player.combat_system.manager.fire_rate = max(0.04, 0.08 - (level * 0.008))

        # Transfer Stock to Player Active Inventory
        elif stat_name == "missiles":
            player.missiles = level
        elif stat_name == "lightning_charges":
            player.lightning_charges = level
        elif stat_name == "laser_fuel":
            player.laser_fuel = level
        elif stat_name == "bombs":
            player.bombs = level

    def apply_all_upgrades(self, player):
        """Called in reset_game to move Workshop purchases into Huey's inventory."""
        if player is None: return
        for stat_name in self.stats:
            self._apply_stat_boost(stat_name, player)
        
        # CLEAR CONSUMABLE STOCK AFTER STARTING RUN
        # This ensures you have to buy ammo again for the next life!
        self.stats["missiles"]["level"] = 0
        self.stats["lightning_charges"]["level"] = 0
        self.stats["laser_fuel"]["level"] = 0
        self.stats["bombs"]["level"] = 0
        self.save_game()