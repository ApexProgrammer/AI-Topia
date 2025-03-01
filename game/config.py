# Window Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30
TITLE = "AI Colony Simulation"

# Grid Configuration
TILE_SIZE = 32
INITIAL_MAP_SIZE = 15  # Reduced for smaller starting area
EXPANSION_BUFFER = 2
MIN_MAP_SIZE = 20
MAX_MAP_SIZE = 50
EXPANSION_COST = 500

# Building Spacing
MIN_BUILDING_SPACING = 1
BUILDING_MARGIN = 1

# Production Rates - Rebalanced for better game progression
BASE_PRODUCTION_RATE = 0.15
FOOD_PRODUCTION_RATE = 0.2  # Reduced from 0.3
WOOD_PRODUCTION_RATE = 0.18  # Reduced from 0.25
STONE_PRODUCTION_RATE = 0.25  # Increased from 0.15 to make stone production more noticeable
METAL_PRODUCTION_RATE = 0.12  # Reduced from 0.15
GOODS_PRODUCTION_RATE = 0.15  # Reduced from 0.2

# Colonist Configuration
COLONIST_SPEED = 0.2
MOVEMENT_SPEED = 0.2
DIAGONAL_MOVEMENT = True

# Game Balance
HAPPINESS_RADIUS = 200
WORK_RADIUS = 50
BASE_RESOURCE_COST = 10
INVENTORY_UPDATE_RATE = 60
INITIAL_COLONISTS = 10

# Camera Configuration
CAMERA_ZOOM_SPEED = 0.1

# Social Configuration
WORKING_AGE = 18
RETIREMENT_AGE = 70
LIFE_EXPECTANCY = 90
REPRODUCTION_AGE_MIN = 20
REPRODUCTION_AGE_MAX = 60
REPRODUCTION_BASE_CHANCE = 0.05  # Reduced from 0.5 for slower growth
REPRODUCTION_COOLDOWN = 10
MARRIAGE_CHANCE = 0.2
FAMILY_REPRODUCTION_BONUS = 0.1  # New parameter - bonus for families in family houses

# Add birth rate policy
POLICIES = {
    'birth_rate': {'min': 0.01, 'max': 0.5, 'step': 0.01, 'format': '{:.0%}'}
}

# Building Tiers - New system for building progression
BUILDING_TIERS = {
    'BASIC': 1,
    'INTERMEDIATE': 2,
    'ADVANCED': 3
}

# Building Configuration - Updated with tiers and rebalanced costs/benefits
BUILDING_TYPES = {
    'house': {
        'cost': {'wood': 20, 'stone': 10},
        'description': 'Housing for colonists',
        'max_occupants': 4,
        'happiness_bonus': 10,
        'build_time': 100,
        'size': 1,
        'tier': BUILDING_TIERS['BASIC']
    },
    'farm': {
        'cost': {'wood': 15},
        'description': 'Produces food for the colony',
        'produces': 'food',
        'production_rate': FOOD_PRODUCTION_RATE,
        'max_jobs': 4,
        'build_time': 150,
        'size': 2,
        'storage_multiplier': 2.0,
        'tier': BUILDING_TIERS['BASIC']
    },
    'woodcutter': {
        'cost': {'wood': 10},
        'description': 'Gathers wood from forests',
        'produces': 'wood',
        'production_rate': WOOD_PRODUCTION_RATE,
        'max_jobs': 3,
        'build_time': 100,
        'size': 1,
        'storage_multiplier': 1.5,
        'tier': BUILDING_TIERS['BASIC']
    },
    'quarry': {
        'cost': {'wood': 20},
        'description': 'Extracts stone for construction',
        'produces': 'stone',
        'production_rate': STONE_PRODUCTION_RATE,
        'max_jobs': 3,
        'build_time': 200,
        'size': 2,
        'storage_multiplier': 1.5,
        'tier': BUILDING_TIERS['BASIC']
    },
    'mine': {
        'cost': {'wood': 25, 'stone': 10},
        'description': 'Produces metal for advanced buildings',
        'produces': 'metal',
        'production_rate': METAL_PRODUCTION_RATE,
        'max_jobs': 4,
        'build_time': 300,
        'size': 2,
        'storage_multiplier': 1.5,
        'tier': BUILDING_TIERS['BASIC']
    },
    'workshop': {
        'cost': {'wood': 30, 'stone': 15, 'metal': 5},
        'description': 'Converts raw materials into goods',
        'produces': 'goods',
        'production_rate': GOODS_PRODUCTION_RATE,
        'max_jobs': 5,
        'build_time': 200,
        'size': 2,
        'storage_multiplier': 2.0,
        'tier': BUILDING_TIERS['BASIC']
    },
    'market': {
        'cost': {'wood': 20, 'stone': 10},
        'description': 'Central trading hub for all resources',
        'max_jobs': 3,
        'happiness_bonus': 5,
        'build_time': 150,
        'size': 2,
        'markup': 1.2,
        'sells': ['food', 'wood', 'stone', 'metal', 'goods', 'meals'],
        'storage_multiplier': 3.0,  # Reduced from 5.0
        'base_prices': {
            'food': 8,
            'wood': 10,
            'stone': 12,
            'metal': 20,
            'goods': 15,
            'meals': 12
        },
        'tier': BUILDING_TIERS['BASIC']
    },
    'tavern': {
        'cost': {'wood': 25, 'stone': 15},
        'description': 'Increases colonist happiness and social interactions',
        'max_jobs': 2,
        'happiness_bonus': 15,
        'build_time': 150,
        'size': 2,
        'tier': BUILDING_TIERS['BASIC']
    },
    'government': {
        'cost': {'wood': 50, 'stone': 30, 'metal': 10},
        'description': 'Central government building for colony administration',
        'max_jobs': 5,
        'happiness_bonus': 5,
        'build_time': 300,
        'size': 3,
        'tier': BUILDING_TIERS['INTERMEDIATE']
    },
    'food_processor': {
        'cost': {'wood': 30, 'stone': 15, 'metal': 10},
        'description': 'Processes raw food into meals',
        'produces': 'meals',
        'production_rate': 0.15,  # Reduced from 0.2
        'max_jobs': 4,
        'build_time': 200,
        'size': 2,
        'storage_multiplier': 1.5,
        'inputs': {'food': 0.3},  # New parameter - resource chain dependency
        'tier': BUILDING_TIERS['INTERMEDIATE']
    },
    'advanced_mine': {
        'cost': {'wood': 40, 'stone': 30, 'metal': 20},
        'description': 'Advanced mining facility with higher metal output',
        'produces': 'metal',
        'production_rate': 0.22,  # Reduced from 0.25
        'max_jobs': 6,
        'build_time': 400,
        'size': 3,
        'storage_multiplier': 2.0,
        'tier': BUILDING_TIERS['ADVANCED']
    },
    'lumber_mill': {
        'cost': {'wood': 35, 'stone': 20, 'metal': 5},  # Increased costs
        'description': 'Processes wood more efficiently',
        'produces': 'wood',
        'production_rate': 0.25,  # Reduced from 0.3
        'max_jobs': 5,
        'build_time': 250,
        'size': 2,
        'storage_multiplier': 2.0,
        'tier': BUILDING_TIERS['INTERMEDIATE']
    },
    'storage_warehouse': {
        'cost': {'wood': 50, 'stone': 30, 'metal': 10},
        'description': 'Large storage facility for resources',
        'max_jobs': 3,
        'build_time': 300,
        'size': 3,
        'storage_multiplier': 4.0,  # Reduced from 5.0
        'happiness_bonus': 2,
        'tier': BUILDING_TIERS['INTERMEDIATE']
    },
    'family_house': {
        'cost': {'wood': 30, 'stone': 15},
        'description': 'Specialized housing for families with reproduction bonus',
        'max_occupants': 6,
        'happiness_bonus': 15,
        'reproduction_bonus': 0.1,  # New parameter for family house
        'build_time': 150,
        'size': 2,
        'tier': BUILDING_TIERS['INTERMEDIATE']
    }
}

# Initial Resource Configuration - Adjusted for better early game balance
INITIAL_RESOURCES = {
    'food': 150,  # Increased from 100
    'wood': 100,  # Increased from 75
    'stone': 60,  # Increased from 50
    'metal': 30,  # Increased from 25
    'goods': 20   # Reduced from 25
}

# Resource Generation
RESOURCE_CONSUMPTION_RATE = 0.08
RESOURCE_STORAGE_CAPACITY = 1500
LOW_RESOURCE_THRESHOLD = 10

# Economic Configuration
INITIAL_CURRENCY = 2000
INITIAL_TREASURY = 5000  # Reduced from 20000
MINIMUM_WAGE = 12
TAX_RATE = 0.15    # Reduced from 0.20
INTEREST_RATE = 0.05

# Critical Positions System - New!
CRITICAL_POSITION_BONUS = 0.25  # Productivity bonus for critical positions
CRITICAL_POSITION_WAGE_BONUS = 1.5  # Wage bonus for critical positions

# Skill Development
SKILL_GAIN_RATE = 0.001  # Rate at which colonists gain skills while working
EDUCATION_SKILL_BONUS = 0.005  # Additional skill gain from education

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
MARKET_STORAGE_MULTIPLIER = 3.0  # Reduced from 5.0
BASE_MARKET_PRICES = {
    'food': 8,
    'wood': 10,
    'stone': 12,
    'metal': 20,
    'goods': 15,
    'meals': 12
}

# Population density parameters for colony expansion
POPULATION_DENSITY_THRESHOLD = 0.7  # Trigger expansion when 70% of tiles are used
COLONISTS_PER_TILE = 2
BUILDINGS_PER_TILE = 0.5

SUPPLY_DEMAND_IMPACT = 0.2
PRICE_MEMORY = 10
PRICE_VOLATILITY = 0.1
MARKET_UPDATE_RATE = 100
BASE_STORAGE_CAPACITY = 100
STORAGE_MULTIPLIER = 2.0

# Animation Configuration
ANIMATION_SPEED = 0.2
WALK_FRAMES = 16

# Camera Configuration
CAMERA_ACCELERATION = 2.0
CAMERA_FRICTION = 0.9
CAMERA_MAX_SPEED = 20.0
CAMERA_ZOOM_SPEED = 0.1

# Building Decision Thresholds
CONSTRUCTION_SKILL_THRESHOLD = 50
MIN_MONEY_FOR_BUILDING = 1000
BUILDING_CHANCE = 0.1

# AI Configuration
NEURAL_NET_LAYERS = [64, 128, 64]
LEARNING_RATE = 0.001
BATCH_SIZE = 32
INPUT_SIZE = 22
OUTPUT_SIZE = 10
