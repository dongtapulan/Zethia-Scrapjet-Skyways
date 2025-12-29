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
PLAYER_HEALTH = 100

# --- Physics & Flight ---
GRAVITY = 18            # Slightly reduced from 20 for floatier feel
THRUST_FORCE = 75       # Slightly buffed from 70 to counter weight better
EMERGENCY_THRUST = 110  # Stronger "save me" force
TERMINAL_VELOCITY = 45  # Lowered so you don't fall too fast to react
DRAG = 0.96             # More "air resistance" helps stabilize the plane

# --- Heat System (REBALANCED) ---
HEAT_MAX = 150.0             # Increased from 100 (Bigger tank)
HEAT_GAIN_TAP = 3.0          # Lowered from 5.0
HEAT_GAIN_HOLD = 10.0        # Lowered from 15.0
HEAT_COOLDOWN_AIR = 10.0     # Buffed from 2.0 (Cool down faster while gliding)
HEAT_COOLDOWN_SKIM = 40.0    # Buffed from 8.0 (Rapid cooling on ground)
OVERHEAT_STALL_TIME = 2.0    # Shortened from 3.0 (Less punishment)

# --- Scrap & Weight (REBALANCED) ---
MAX_WEIGHT_CAPACITY = 1000
WEIGHT_FREE_ZONE = 150       # New! First 150 scrap units don't affect physics
WEIGHT_GRAVITY_SCALER = 0.02 # New! Controls how much each unit of weight pulls you down
BULLET_SHED_AMOUNT = 2.0     # Buffed! Each shot now removes 2.0 weight (was 0.5)

# --- Combat ---
MISSILE_COOLDOWN = 3000
BOMB_COOLDOWN = 1500

# --- World ---
STORY_GOAL_DISTANCE = 50000
GROUND_HEIGHT = 80
GROUND_LINE = HEIGHT - GROUND_HEIGHT

# --- Assets & UI ---
FONT_MAIN = "assets/fonts/8-bitanco.ttf"
SFX_MACHINE_GUN = "assets/sfx/machine_gun.mp3"

# --- HUD & Stats ---
HEALTH_BAR_COLOR = (255, 50, 50)
DISTANCE_GOAL = 50000  # How far Huey needs to go