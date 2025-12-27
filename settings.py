# Screen settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
LUMEN_GOLD = (255, 215, 0)
HEAT_RED = (255, 69, 0)
SCRAP_GREEN = (50, 205, 50)
GLOOM_VIOLET = (138, 43, 226)

# Player settings
PLAYER_SPEED = 250
PLAYER_VERTICAL_SPEED = 200
PLAYER_HEALTH = 3

# --- Physics & Flight ---
GRAVITY = 30
THRUST_FORCE = 70
EMERGENCY_THRUST = 100
TERMINAL_VELOCITY = 50
DRAG = 0.95

# --- Heat System (REBALANCED) ---
HEAT_MAX = 150.0             # Increased from 100 (Bigger tank)
HEAT_GAIN_TAP = 3.0          # Lowered from 5.0
HEAT_GAIN_HOLD = 10.0        # Lowered from 15.0
HEAT_COOLDOWN_AIR = 10.0     # Buffed from 2.0 (Cool down faster while gliding)
HEAT_COOLDOWN_SKIM = 40.0    # Buffed from 8.0 (Rapid cooling on ground)
OVERHEAT_STALL_TIME = 2.0    # Shortened from 3.0 (Less punishment)

# --- Scrap & Weight ---
SCRAP_TO_OVERCLOCK = 50
LEECH_WEIGHT_PENALTY = 0.15

# --- Combat ---
MISSILE_COOLDOWN = 3000
BOMB_COOLDOWN = 1500

# --- World ---
STORY_GOAL_DISTANCE = 50000
GROUND_HEIGHT = 80
GROUND_LINE = HEIGHT - GROUND_HEIGHT