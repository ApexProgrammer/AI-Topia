# Window Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30
TITLE = "AI Colony Simulation"

# Grid Configuration
TILE_SIZE = 32
INITIAL_MAP_SIZE = 20
EXPANSION_BUFFER = 2
MIN_MAP_SIZE = 20
MAX_MAP_SIZE = 50
EXPANSION_COST = 1000

# Building Spacing
MIN_BUILDING_SPACING = 2  # Minimum tiles between buildings
BUILDING_MARGIN = 1      # Margin from grid edges

# Colonist Configuration
COLONIST_SPEED = 0.05
MOVEMENT_SPEED = 0.05
DIAGONAL_MOVEMENT = False
WORKING_AGE = 18
RETIREMENT_AGE = 65
LIFE_EXPECTANCY = 80
REPRODUCTION_AGE_MIN = 20
REPRODUCTION_AGE_MAX = 40
INITIAL_COLONISTS = 10
REPRODUCTION_BASE_CHANCE = 0.002
REPRODUCTION_COOLDOWN = 2000
MARRIAGE_CHANCE = 0.05

# Building Configuration
BUILDING_CHANCE = 0.02
MIN_MONEY_FOR_BUILDING = 1000
CONSTRUCTION_SKILL_THRESHOLD = 50
BUILD_TIME_MULTIPLIER = 5

# Animation Configuration
ANIMATION_SPEED = 0.05
WALK_FRAMES = 20

# Population Thresholds for Expansion
COLONISTS_PER_TILE = 2
BUILDINGS_PER_TILE = 0.5

# Building Types and Costs
BUILDING_TYPES = {
    'house': {
        'cost': 500,
        'build_time': 200 * BUILD_TIME_MULTIPLIER,
        'capacity': 4,
        'size': 1,
        'priority': 5
    },
    'farm': {
        'cost': 800,
        'build_time': 300 * BUILD_TIME_MULTIPLIER,
        'jobs': 4,
        'produces': 'food',
        'production_rate': 10,
        'size': 2,
        'priority': 4
    },
    'factory': {
        'cost': 1500,
        'build_time': 400 * BUILD_TIME_MULTIPLIER,
        'jobs': 8,
        'produces': 'goods',
        'production_rate': 5,
        'size': 2,
        'priority': 3
    },
    'shop': {
        'cost': 1000,
        'build_time': 250 * BUILD_TIME_MULTIPLIER,
        'jobs': 4,
        'sells': ['food', 'goods'],
        'markup': 1.5,
        'size': 1,
        'priority': 3
    },
    'restaurant': {
        'cost': 1200,
        'build_time': 180,
        'jobs': 6,
        'consumes': 'food',
        'produces': 'meals',
        'production_rate': 15,
        'size': 1
    },
    'bank': {
        'cost': 2000,
        'build_time': 350 * BUILD_TIME_MULTIPLIER,
        'jobs': 5,
        'interest_rate': 0.05,
        'size': 1,
        'priority': 2
    },
    'government': {
        'cost': 2000,
        'build_time': 500 * BUILD_TIME_MULTIPLIER,
        'jobs': 10,
        'size': 2,
        'priority': 1
    }
}

# Resource Configuration
RESOURCES = {
    'food': {'base_price': 10},
    'goods': {'base_price': 20},
    'meals': {'base_price': 25}
}

# Economic Configuration
INITIAL_CURRENCY = 1000
MINIMUM_WAGE = 10
TAX_RATE = 0.15
INTEREST_RATE = 0.05
PRICE_VOLATILITY = 0.1

# Market Configuration
SUPPLY_DEMAND_IMPACT = 0.2
PRICE_MEMORY = 10

# Camera Configuration
CAMERA_ACCELERATION = 2.0
CAMERA_FRICTION = 0.9
CAMERA_MAX_SPEED = 20.0
CAMERA_ZOOM_SPEED = 0.1

# AI Configuration
NEURAL_NET_LAYERS = [64, 128, 64]
LEARNING_RATE = 0.001
BATCH_SIZE = 32
INPUT_SIZE = 22
OUTPUT_SIZE = 10
