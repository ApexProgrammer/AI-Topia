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

# Production Rates
BASE_PRODUCTION_RATE = 0.1
FOOD_PRODUCTION_RATE = 0.15
WOOD_PRODUCTION_RATE = 0.12
STONE_PRODUCTION_RATE = 0.08
METAL_PRODUCTION_RATE = 0.05
GOODS_PRODUCTION_RATE = 0.10

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
BUILDING_TYPES = {
    'house': {
        'cost': {'wood': 20, 'stone': 10},
        'description': 'Housing for colonists',
        'max_occupants': 4,
        'happiness_bonus': 10,
        'build_time': 100,
        'size': 1
    },
    'farm': {
        'cost': {'wood': 15},
        'description': 'Produces food',
        'produces': 'food',
        'production_rate': FOOD_PRODUCTION_RATE,
        'max_jobs': 4,
        'build_time': 150,
        'size': 2
    },
    'woodcutter': {
        'cost': {'wood': 10},
        'description': 'Gathers wood from nearby forests',
        'produces': 'wood',
        'production_rate': WOOD_PRODUCTION_RATE,
        'max_jobs': 3,
        'build_time': 100,
        'size': 1
    },
    'quarry': {
        'cost': {'wood': 20},
        'description': 'Extracts stone',
        'produces': 'stone',
        'production_rate': STONE_PRODUCTION_RATE,
        'max_jobs': 3,
        'build_time': 200,
        'size': 2
    },
    'mine': {
        'cost': {'wood': 25, 'stone': 10},
        'description': 'Produces metal',
        'produces': 'metal',
        'production_rate': METAL_PRODUCTION_RATE,
        'max_jobs': 4,
        'build_time': 300,
        'size': 2
    },
    'workshop': {
        'cost': {'wood': 30, 'stone': 15, 'metal': 5},
        'description': 'Converts raw materials into goods',
        'produces': 'goods',
        'production_rate': GOODS_PRODUCTION_RATE,
        'max_jobs': 5,
        'build_time': 200,
        'size': 2,
        'storage_multiplier': 2.0
    },
    'market': {
        'cost': {'wood': 20, 'stone': 10},
        'description': 'Allows colonists to buy goods',
        'max_jobs': 3,
        'happiness_bonus': 5,
        'build_time': 150,
        'size': 2,
        'markup': 1.2,
        'sells': ['food', 'goods'],
        'storage_multiplier': 3.0
    },
    'tavern': {
        'cost': {'wood': 25, 'stone': 15},
        'description': 'Increases colonist happiness and social interactions',
        'max_jobs': 2,
        'happiness_bonus': 15,
        'build_time': 150,
        'size': 2
    },
    'government': {
        'cost': {'wood': 50, 'stone': 30, 'metal': 10},
        'description': 'Central government building for colony administration',
        'max_jobs': 5,
        'happiness_bonus': 5,
        'build_time': 300,
        'size': 3
    }
}

# Resource Generation
FOOD_PRODUCTION_RATE = 15
GOODS_PRODUCTION_RATE = 8
RESOURCE_CONSUMPTION_RATE = 0.1
RESOURCE_STORAGE_CAPACITY = 1000
LOW_RESOURCE_THRESHOLD = 5  # Per capita

# Economic Configuration
INITIAL_CURRENCY = 2000
INITIAL_TREASURY = 20000
MINIMUM_WAGE = 12
TAX_RATE = 0.20    # 20% tax rate
INTEREST_RATE = 0.05  # 5% interest rate per year
SALARY_MULTIPLIER = 1.5

# Resource Configuration
RESOURCES = {
    'food': {'base_price': 5},
    'wood': {'base_price': 8},
    'stone': {'base_price': 12},
    'metal': {'base_price': 20},
    'goods': {'base_price': 10},
    'meals': {'base_price': 15}
}

# Job Salaries
JOB_SALARIES = {
    'farmer': 15,
    'factory_worker': 18,
    'shopkeeper': 16,
    'banker': 22,
    'government_worker': 20,
    'wood_gatherer': 15,
    'stone_gatherer': 16,
    'metal_gatherer': 18,
    'goods_worker': 17
}

# Market Configuration
SUPPLY_DEMAND_IMPACT = 0.2
PRICE_MEMORY = 10
PRICE_VOLATILITY = 0.1
MARKET_UPDATE_RATE = 100  # Ticks between price updates
BASE_STORAGE_CAPACITY = 100
STORAGE_MULTIPLIER = 2.0  # Storage capacity multiplier for specialized buildings

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

# Building Decision Thresholds
CONSTRUCTION_SKILL_THRESHOLD = 50  # Minimum skill needed to construct buildings
MIN_MONEY_FOR_BUILDING = 1000      # Minimum money needed to start construction
BUILDING_CHANCE = 0.1              # Base chance for colonists to attempt building

# AI Configuration
NEURAL_NET_LAYERS = [64, 128, 64]
LEARNING_RATE = 0.001
BATCH_SIZE = 32
INPUT_SIZE = 22
OUTPUT_SIZE = 10

# Game Balance
HAPPINESS_RADIUS = 200  # Radius for building happiness effects
WORK_RADIUS = 50      # Radius for work efficiency bonus
BASE_RESOURCE_COST = 10
INVENTORY_UPDATE_RATE = 60
