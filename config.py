"""
Game configuration constants for Breakout.
"""

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Brick Breaker"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 40)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 128)

# Paddle settings
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 40
PADDLE_Y = SCREEN_HEIGHT - 80
PADDLE_SPEED = 10

# Ball settings
BALL_SIZE = 32
BALL_SPEED_INITIAL = 6
BALL_SPEED_MIN = 4
BALL_SPEED_MAX = 12

# Brick settings
BRICK_WIDTH = 96
BRICK_HEIGHT = 32
BRICK_ROWS = 5
BRICK_COLS = 9
BRICK_PADDING = 4
BRICK_TOP_OFFSET = 80
BRICK_LEFT_OFFSET = (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

# Brick health
BRICK_HEALTH_NORMAL = 2  # Two hits: complete -> cracked -> destroyed

# Score values by brick type (indices 0-9 correspond to brick types)
SCORE_VALUES = [50, 50, 100, 100, 100, 150, 150, 250, 250, 500]

# Lives
INITIAL_LIVES = 3
HEART_SIZE = 40
HEART_SPACING = 50
HEART_Y = 20

# Power-up settings
POWERUP_DROP_CHANCE = 0.20  # 20% chance to drop power-up
POWERUP_SPEED = 3
POWERUP_SIZE = 40
POWERUP_DURATION = 8000  # 8 seconds in milliseconds

# Power-up types
POWERUP_SLOW = "slow"
POWERUP_FAST = "fast"
POWERUP_BULLET = "bullet"

# Bullet settings
BULLET_SPEED = 12
BULLET_COOLDOWN = 300  # milliseconds between shots

# Particle settings
PARTICLE_COUNT = 8
PARTICLE_SIZE = 16
PARTICLE_SPEED = 5
PARTICLE_LIFETIME = 1000  # milliseconds
PARTICLE_GRAVITY = 0.3

# Speed modifiers
SLOW_MULTIPLIER = 0.6
FAST_MULTIPLIER = 1.5

# Paddle display durations (milliseconds)
PADDLE_SCORE_DISPLAY_TIME = 1500

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_WIN = "win"

# Number of levels
NUM_LEVELS = 5
