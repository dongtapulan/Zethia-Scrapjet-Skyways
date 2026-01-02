from settings import *

class ModeManager:
    """
    Decides the 'rules of engagement' for the current session.
    Keeps Arcade logic intact while preparing the stage for Story Mode.
    """
    def __init__(self, upgrade_manager):
        self.upgrade_manager = upgrade_manager
        self.current_mode = "ARCADE"  # Options: "ARCADE", "STORY"
        
        # Story specific tracking
        self.current_level_id = 1
        self.story_goal_distance = 5000 # 5km to finish a level
        self.is_boss_active = False

    def set_mode(self, mode, level_id=1):
        """Switches the game mode and resets mode-specific goals."""
        self.current_mode = mode
        self.current_level_id = level_id
        self.is_boss_active = False
        
        if mode == "STORY":
            # Scale distance goal based on level
            self.story_goal_distance = 3000 + (level_id * 2000)
        else:
            self.story_goal_distance = float('inf') # Infinite for Arcade

    def check_victory_condition(self, distance):
        """Determines if the current run/mission is successful."""
        if self.current_mode == "STORY":
            return distance >= self.story_goal_distance
        return False # Arcade only ends in death (Game Over)

    def get_spawn_difficulty(self, distance):
        """
        Returns a multiplier to scale enemy HP or spawn rates.
        Keeps your existing difficulty curve but allows story spikes.
        """
        if self.current_mode == "ARCADE":
            # Endless scaling: Difficulty increases 10% every 1km
            return 1.0 + (distance / 10000)
        else:
            # Story scaling: Locked to level difficulty
            return 1.0 + (self.current_level_id * 0.2)

    def handle_run_completion(self, score, distance, was_victory):
        """
        Processes rewards. 
        In Arcade: Always convert score to bolts.
        In Story: Only give bonus bolts on Victory.
        """
        summary = {
            "bolts_earned": 0,
            "story_unlocked": False,
            "message": ""
        }

        if self.current_mode == "ARCADE":
            summary["bolts_earned"] = self.upgrade_manager.convert_score_to_bolts(score)
            summary["message"] = f"RUN ENDED: {distance:.0f}m TRAVELLED"
        
        elif self.current_mode == "STORY":
            if was_victory:
                # Big bonus for completing a story mission
                bonus = 500 * self.current_level_id
                self.upgrade_manager.total_bolts += bonus
                self.upgrade_manager.save_game()
                summary["bolts_earned"] = bonus
                summary["story_unlocked"] = True
                summary["message"] = "MISSION ACCOMPLISHED"
            else:
                summary["message"] = "MISSION FAILED"

        return summary