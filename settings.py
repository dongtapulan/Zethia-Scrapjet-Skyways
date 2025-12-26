# Screen settings
WIDTH = 1000
HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
LUMEN_GOLD = (255, 215, 0)
HEAT_RED = (255, 69, 0)      # For the gauge
SCRAP_GREEN = (50, 205, 50)  # For the Scrap-Meter
GLOOM_VIOLET = (138, 43, 226) # Enemy lasers/corruption

# Player settings
PLAYER_SPEED = 250
PLAYER_VERTICAL_SPEED = 200
PLAYER_HEALTH = 3

# --- Physics & Flight (The "Feel") ---
# settings.py

GRAVITY = 20           # Downward pull
THRUST_FORCE = 70      # Tapping space (Must be > GRAVITY)
EMERGENCY_THRUST = 100 # Holding space
TERMINAL_VELOCITY = 50 # Max falling speed
DRAG = 0.95            # Air resistance (keep it between 0.9 and 0.99)

# --- Heat System ---
HEAT_MAX = 100.0
HEAT_GAIN_TAP = 5.0         # Heat per spacebar tap
HEAT_GAIN_HOLD = 15.0       # Heat per second of holding
HEAT_COOLDOWN_AIR = 2.0     # Natural cooling per second
HEAT_COOLDOWN_SKIM = 8.0    # Cooling while skimming (Landing Gear)
OVERHEAT_STALL_TIME = 3.0   # Seconds engine is dead after overheating

# --- Scrap & Weight ---
SCRAP_TO_OVERCLOCK = 50     # Total scrap needed for powerup
LEECH_WEIGHT_PENALTY = 0.15 # Multiplier that increases GRAVITY per Leech attached

# --- Combat ---
MISSILE_COOLDOWN = 3000     # Milliseconds
BOMB_COOLDOWN = 1500        # Milliseconds

# --- Story Thresholds ---
STORY_GOAL_DISTANCE = 50000 # Meters to reach the end
# settings.py additions
GROUND_HEIGHT = 80  # Adjust this to match the thickness of your ground.png
GROUND_LINE = HEIGHT - GROUND_HEIGHT