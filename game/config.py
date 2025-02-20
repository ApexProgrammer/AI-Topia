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
EXPANSION_COST = 500

# Building Spacing
MIN_BUILDING_SPACING = 1
BUILDING_MARGIN = 1

# Colonist Configuration
COLONIST_SPEED = 0.05
MOVEMENT_SPEED = 0.05
DIAGONAL_MOVEMENT = False
WORKING_AGE = 18
RETIREMENT_AGE = 70
LIFE_EXPECTANCY = 90
REPRODUCTION_AGE_MIN = 20
REPRODUCTION_AGE_MAX = 60
INITIAL_COLONISTS = 200  # Target initial number of colonists; actual count depends on valid grid placement
REPRODUCTION_BASE_CHANCE = 0.2
REPRODUCTION_COOLDOWN = 10
MARRIAGE_CHANCE = 0.2

# Building Configuration
BUILDING_CHANCE = 0.05
MIN_MONEY_FOR_BUILDING = 800
CONSTRUCTION_SKILL_THRESHOLD = 40
BUILD_TIME_MULTIPLIER = 3

# Resource Generation
FOOD_PRODUCTION_RATE = 15
GOODS_PRODUCTION_RATE = 8
RESOURCE_CONSUMPTION_RATE = 0.005

# Economic Configuration
INITIAL_CURRENCY = 2000
INITIAL_TREASURY = 20000
MINIMUM_WAGE = 12
TAX_RATE = 0.20
INTEREST_RATE = 0.05
SALARY_MULTIPLIER = 1.5

# Building Types and Costs
BUILDING_TYPES = {
    'house': {
        'cost': 300,
        'build_time': 150,
        'capacity': 4,
        'size': 1,
        'priority': 5
    },
    'farm': {
        'cost': 500,
        'build_time': 200,
        'jobs': 4,
        'produces': 'food',
        'production_rate': 15,
        'size': 2,
        'priority': 4
    },
    'factory': {
        'cost': 1000,
        'build_time': 300,
        'jobs': 8,
        'produces': 'goods',
        'production_rate': 8,
        'size': 2,
        'priority': 3
    },
    'shop': {
        'cost': 600,
        'build_time': 200,
        'jobs': 4,
        'sells': ['food', 'goods'],
        'markup': 1.3,
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
        'cost': 1200,
        'build_time': 250,
        'jobs': 5,
        'interest_rate': 0.05,
        'size': 1,
        'priority': 2
    },
    'government': {
        'cost': 1200,
        'build_time': 400,
        'jobs': 10,
        'size': 2,
        'priority': 1
    }
}

# Resource Configuration
RESOURCES = {
    'food': {'base_price': 5},
    'goods': {'base_price': 10},
    'meals': {'base_price': 15}
}

# Job Salaries
JOB_SALARIES = {
    'farmer': 15,
    'factory_worker': 18,
    'shopkeeper': 16,
    'banker': 22,
    'government_worker': 20
}

# Market Configuration
SUPPLY_DEMAND_IMPACT = 0.2
PRICE_MEMORY = 10
PRICE_VOLATILITY = 0.1
MARKET_UPDATE_RATE = 100

# Animation Configuration
ANIMATION_SPEED = 0.05
WALK_FRAMES = 8

# Population Thresholds for Expansion
COLONISTS_PER_TILE = 2
BUILDINGS_PER_TILE = 0.5

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
