import pygame
import random
from ..config import (BUILDING_TYPES, TILE_SIZE, RESOURCES,
                     SUPPLY_DEMAND_IMPACT, INTEREST_RATE,
                     PRICE_VOLATILITY, MARKET_UPDATE_RATE, PRICE_MEMORY,
                     JOB_SALARIES, MINIMUM_WAGE, BASE_STORAGE_CAPACITY,
                     INVENTORY_UPDATE_RATE, HAPPINESS_RADIUS, WORK_RADIUS,
                     BUILDING_TIERS, CRITICAL_POSITION_BONUS)

class Job:
    def __init__(self, building):
        self.building = building
        self.building_type = building.building_type
        self.employee = None
        self.x = building.x
        self.y = building.y
        self.is_critical = False  # Flag for critical positions
        
        # Set salary based on job type
        if self.building_type == 'farm':
            self.type = 'farmer'
            self.salary = JOB_SALARIES['farmer']
        elif self.building_type == 'factory':
            self.type = 'factory_worker'
            self.salary = JOB_SALARIES['factory_worker']
        elif self.building_type == 'shop':
            self.type = 'shopkeeper'
            self.salary = JOB_SALARIES['shopkeeper']
        elif self.building_type == 'bank':
            self.type = 'banker'
            self.salary = JOB_SALARIES['banker']
        elif self.building_type == 'government':
            self.type = 'government_worker'
            self.salary = JOB_SALARIES['government_worker']
        elif self.building_type == 'woodcutter':
            self.type = 'wood_gatherer'
            self.salary = JOB_SALARIES['wood_gatherer']
        elif self.building_type == 'quarry':
            self.type = 'stone_gatherer'
            self.salary = JOB_SALARIES['stone_gatherer']
        elif self.building_type == 'mine':
            self.type = 'metal_gatherer'
            self.salary = JOB_SALARIES['metal_gatherer']
        elif self.building_type == 'workshop':
            self.type = 'goods_worker'
            self.salary = JOB_SALARIES['goods_worker']
        else:
            self.type = 'worker'
            self.salary = MINIMUM_WAGE

class Building:
    _next_id = 1  # Class variable for generating unique IDs
    
    def __init__(self, building_type, x, y, world):
        self.id = Building._next_id  # Assign unique ID
        Building._next_id += 1  # Increment for next building
        
        self.building_type = building_type
        self.x = x
        self.y = y
        self.world = world
        
        # Get building properties from config
        building_config = BUILDING_TYPES[building_type]
        self.cost = building_config['cost']
        self.build_time = building_config['build_time']
        self.size = building_config['size']  # Size in tiles
        self.max_jobs = building_config.get('max_jobs', 0)
        self.happiness_bonus = building_config.get('happiness_bonus', 0)
        self.produces = building_config.get('produces', None)
        self.production_rate = building_config.get('production_rate', 0)
        self.tier = building_config.get('tier', 1)  # Building tier level
        
        # Initialize inventory only once
        self.inventory = {}
        if self.produces:
            self.inventory[self.produces] = 0
            # Initialize in colony inventory if not exists
            if self.produces not in self.world.colony_inventory:
                self.world.colony_inventory[self.produces] = 0
                
            # Start passive production immediately for all resource production buildings
            if building_type in ['quarry', 'woodcutter', 'mine', 'workshop', 'farm']:
                self.construction_progress = 0.2  # Start with some progress
                # Add small initial amount for basic resources
                if self.produces in ['stone', 'metal', 'wood']:
                    world.colony_inventory[self.produces] = max(10, world.colony_inventory.get(self.produces, 0))

        # Storage capacity
        self.storage_multiplier = building_config.get('storage_multiplier', 1.0)
        self.max_storage = BASE_STORAGE_CAPACITY * self.storage_multiplier
        
        # Resource chain dependencies - new!
        self.inputs = building_config.get('inputs', {})
        
        # Family housing reproduction bonus - new!
        self.reproduction_bonus = building_config.get('reproduction_bonus', 0)
        
        # Critical position tracking
        self.has_critical_positions = False
        
        # Building state
        self.construction_progress = 0
        self.is_complete = False
        self.current_occupants = 0
        self.jobs = []
        self.efficiency = 1.0  # Building efficiency tracker
        
        # Initialize inventory and prices
        self.inventory = {}
        self.prices = {}
        self.price_history = []
        self.last_market_update = 0
        
        # Set up based on building type
        if building_type == 'house':
            self.max_occupants = building_config.get('max_occupants', 4)
            self.current_occupants = 0
            self.capacity = self.max_occupants  # Add capacity attribute for houses
        elif building_type == 'family_house':
            self.max_occupants = building_config.get('max_occupants', 6)
            self.current_occupants = 0
            self.capacity = self.max_occupants
        elif building_type in ['shop', 'factory', 'farm', 'woodcutter', 'quarry', 'mine', 'workshop', 'food_processor', 'advanced_mine', 'lumber_mill']:
            # Initialize resource inventory for production buildings
            if self.produces:
                self.inventory[self.produces] = 0
            # Create jobs
            self.create_jobs()
        
        # Financial tracking
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.profit_history = []
        
        # Visualization
        self.base_size = TILE_SIZE * self.size
        self.colors = {
            'house': (100, 200, 100),
            'family_house': (120, 220, 120),  # Slightly brighter green for family house
            'farm': (150, 200, 50),
            'woodcutter': (139, 69, 19),
            'quarry': (169, 169, 169),
            'mine': (105, 105, 105),
            'advanced_mine': (85, 85, 125),  # Darker color for advanced buildings
            'workshop': (200, 200, 100),
            'market': (200, 150, 100),
            'tavern': (200, 100, 200),
            'government': (150, 150, 200),
            'food_processor': (200, 150, 50),
            'lumber_mill': (160, 82, 45),
            'storage_warehouse': (180, 180, 180),
            'school': (100, 100, 220),
            'university': (80, 80, 240),
            'library': (120, 120, 240)
        }

        # Initialize inventory and resources immediately
        self.inventory = {}
        if self.produces:
            self.inventory[self.produces] = 0
            # Ensure resource exists in colony inventory
            if self.produces not in world.colony_inventory:
                world.colony_inventory[self.produces] = 0
                
            # Start passive production immediately for all resource buildings
            if building_type in ['quarry', 'woodcutter', 'mine', 'farm']:
                self.construction_progress = 0.2  # Increased initial progress
                # Add small initial amount for all basic resources
                if self.produces in ['stone', 'metal', 'wood']:
                    world.colony_inventory[self.produces] = max(10, world.colony_inventory.get(self.produces, 0))

    def get_grid_bounds(self):
        """Get the grid coordinates this building occupies"""
        grid_x, grid_y = self.world.get_grid_position(self.x, self.y)
        return [(grid_x + dx, grid_y + dy) 
                for dx in range(self.size) 
                for dy in range(self.size)]

    def update(self, speed_multiplier=1.0):
        if not self.is_complete:
            # Construction phase
            self.construction_progress += speed_multiplier * 0.01
            if self.construction_progress >= self.build_time:
                self.is_complete = True
                # Now that building is complete, assign critical positions if needed
                self.assign_critical_positions()
        
        # Always call produce_resources for resource buildings, even during construction
        if self.produces and self.building_type in ['quarry', 'woodcutter', 'mine', 'farm']:
            self.produce_resources(speed_multiplier)
        elif self.is_complete and self.produces:
            # Other buildings only produce when complete
            self.produce_resources(speed_multiplier)
            
            # Handle sales
            if hasattr(self, 'sells'):
                self.update_prices()
            
            # Handle banking
            if self.building_type == 'bank':
                self.process_banking()
            
            # Track finances
            if len(self.profit_history) >= 30:  # Keep last 30 days
                self.profit_history.pop(0)
            self.profit_history.append(self.daily_revenue - self.daily_expenses)
            self.daily_revenue = 0
            self.daily_expenses = 0
            
            # Apply happiness bonus to nearby colonists
            if self.happiness_bonus > 0:
                for colonist in self.world.colonists:
                    distance = ((colonist.x - self.x)**2 + (colonist.y - self.y)**2)**0.5
                    if distance < HAPPINESS_RADIUS:
                        colonist.happiness = min(100, colonist.happiness + 
                                              (self.happiness_bonus / 100) * speed_multiplier)

    def produce_resources(self, speed_multiplier=1.0):
        """Produce resources if this is a production building with enhanced efficiency"""
        if not self.produces:
            return
            
        # Allow all resource buildings to produce during construction
        if not self.is_complete and self.building_type not in ['quarry', 'woodcutter', 'mine', 'farm']:
            return
            
        workers = [job.employee for job in self.jobs if job.employee]
        
        # Always produce at least a small amount, even without workers
        # Increased base production rate for basic resource buildings
        base_rate = self.production_rate * speed_multiplier
        if self.building_type in ['quarry', 'mine', 'woodcutter']:
            base_rate *= 1.5  # Increased passive production for basic resources
        
        # Base production with improved passive generation
        base_production = base_rate * (0.3 if not workers else 1.5)  # Increased passive production from 0.2 to 0.3
        
        # Calculate efficiency based on workers
        efficiency = 1.0
        if workers:
            # Worker skill bonuses
            skill_bonus = 0
            for worker in workers:
                if self.building_type == 'farm':
                    skill_bonus += worker.skills.get('farming', 50) / 500
                elif self.building_type in ['woodcutter', 'quarry', 'mine']:
                    skill_bonus += worker.skills.get('mining', 50) / 400
                elif self.building_type == 'workshop':
                    skill_bonus += worker.skills.get('crafting', 50) / 500
                
                if hasattr(worker, 'is_critical_position') and worker.is_critical_position:
                    skill_bonus += CRITICAL_POSITION_BONUS
            
            efficiency = (len(workers) / self.max_jobs) + skill_bonus
        
        # Building type bonuses
        type_multiplier = {
            'woodcutter': 1.35,
            'quarry': 1.6,   # Higher multiplier for stone
            'mine': 1.35,
            'workshop': 1.4,
            'farm': 1.0
        }.get(self.building_type, 1.0)
        
        # Calculate final production amount
        production = base_production * efficiency * type_multiplier
        
        # Initialize resource in colony inventory if needed
        if self.produces not in self.world.colony_inventory:
            self.world.colony_inventory[self.produces] = 0
        
        # Add production to colony inventory
        production_amount = production
        self.world.colony_inventory[self.produces] += production_amount
        
        # Debug logging
        if hasattr(self.world, 'debug_log'):
            self.world.debug_log(f"Building {self.building_type} produced {production_amount:.1f} {self.produces}")

        # Update efficiency tracker for UI
        self.efficiency = efficiency
        
        # Update worker tasks
        for worker in workers:
            worker.current_task = f"working at {self.building_type}"

    def has_input_resources(self):
        """Check if required input resources are available"""
        if not self.inputs:
            return True
            
        for resource, amount in self.inputs.items():
            if self.world.colony_inventory.get(resource, 0) < amount:
                return False
        return True
    
    def consume_input_resources(self, production_amount):
        """Consume input resources for production chain and return success"""
        if not self.inputs:
            return True
            
        # Calculate how much input is needed based on production
        input_needed = {}
        for resource, base_amount in self.inputs.items():
            # Scale input needs with production 
            input_needed[resource] = base_amount * (production_amount / self.production_rate)
        
        # Check if we have enough of all inputs
        for resource, amount in input_needed.items():
            if self.world.colony_inventory.get(resource, 0) < amount:
                return False
        
        # Consume the resources
        for resource, amount in input_needed.items():
            self.world.colony_inventory[resource] -= amount
            
            # Log consumption
            if hasattr(self.world, 'debug_log'):
                self.world.debug_log(f"Resource chain: consumed {amount:.2f} {resource} for {self.building_type}")
                
        return True

    def update_prices(self):
        """Update prices based on supply and demand"""
        if not hasattr(self, 'sells') or not self.is_complete:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_market_update < MARKET_UPDATE_RATE:
            return
            
        self.last_market_update = current_time
        
        for resource in self.sells:
            base_price = RESOURCES[resource]['base_price']
            current_price = self.prices[resource]
            
            # Calculate supply factor
            inventory_level = self.inventory.get(resource, 0)
            supply_factor = 1.0
            if inventory_level > 100:
                supply_factor = 0.9  # Price decrease when oversupplied
            elif inventory_level < 20:
                supply_factor = 1.1  # Price increase when undersupplied
                
            # Calculate new price
            target_price = base_price * self.markup * supply_factor
            price_change = (target_price - current_price) * SUPPLY_DEMAND_IMPACT
            
            # Limit price volatility
            price_change = max(-PRICE_VOLATILITY, min(PRICE_VOLATILITY, price_change))
            new_price = current_price + price_change
            
            # Keep price within reasonable bounds
            min_price = base_price * 0.5
            max_price = base_price * 2.0
            self.prices[resource] = max(min_price, min(max_price, new_price))
            
            # Update price history
            self.price_history.append({
                'time': current_time,
                'resource': resource,
                'price': self.prices[resource]
            })
            
            # Keep history manageable
            if len(self.price_history) > PRICE_MEMORY:
                self.price_history = self.price_history[-PRICE_MEMORY:]

    def process_banking(self):
        """Process banking operations"""
        if self.building_type != 'bank' or not self.is_complete:
            return
            
        # Process interest for all colonists
        for colonist in self.world.colonists:
            if colonist.money > 0:
                interest = colonist.money * (INTEREST_RATE / 365)  # Daily interest
                colonist.money += interest
                colonist.inventory['money'] = colonist.money
                self.daily_expenses += interest

    def create_jobs(self):
        """Create job positions for this building"""
        if self.max_jobs <= 0:
            return []
            
        # Clear existing jobs
        self.jobs = []
        
        # Create job objects
        for _ in range(self.max_jobs):
            job = Job(self)
            job.building = self
            job.x = self.x
            job.y = self.y
            job.type = self.building_type
            job.employee = None
            self.jobs.append(job)
            
        # Return the created jobs list so it can be added to the world.jobs list
        return self.jobs
    
    def assign_critical_positions(self):
        """Assign critical position status to specific jobs based on building type and tier"""
        if not self.jobs or len(self.jobs) == 0:
            return
            
        # Advanced buildings (tier 3) always have at least one critical position
        if self.tier == BUILDING_TIERS['ADVANCED']:
            self.jobs[0].is_critical = True
            self.has_critical_positions = True
            
            # For larger advanced buildings, make more positions critical
            if len(self.jobs) >= 4:
                self.jobs[1].is_critical = True
        
        # Intermediate buildings (tier 2) have critical positions for leadership roles
        elif self.tier == BUILDING_TIERS['INTERMEDIATE']:
            # Buildings that require specialized skills
            if self.building_type in ['lumber_mill', 'food_processor', 'government']:
                self.jobs[0].is_critical = True
                self.has_critical_positions = True
        
        # Special case for specialized resource production
        if self.building_type in ['advanced_mine', 'lumber_mill'] or self.produces == 'meals':
            # Make at least one position critical
            self.jobs[0].is_critical = True
            self.has_critical_positions = True

    def render(self, screen, camera_x=0, camera_y=0, zoom=1.0):
        """Render building with improved visual feedback"""
        # Calculate screen position with camera offset and zoom
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        
        # Calculate size based on building configuration and zoom
        size = int(self.size * TILE_SIZE * zoom)
        
        # Draw building base - no centering adjustment needed since position is already grid-aligned
        building_rect = pygame.Rect(screen_x, screen_y, size, size)
        color = self.colors.get(self.building_type, (200, 200, 200))
        
        # Adjust color based on building tier
        if self.tier == BUILDING_TIERS['INTERMEDIATE']:
            # Slightly richer colors for intermediate tier
            color = tuple(min(255, c * 1.1) for c in color)
        elif self.tier == BUILDING_TIERS['ADVANCED']:
            # More saturated colors for advanced tier
            color = tuple(min(255, int(c * 0.9 + 40)) for c in color)
        
        if not self.is_complete:
            # Show construction progress
            progress = self.construction_progress / self.build_time
            color = tuple(int(c * (0.5 + 0.5 * progress)) for c in color)
        
        # Draw building
        pygame.draw.rect(screen, color, building_rect)
        
        # Draw border for buildings with critical positions
        if self.has_critical_positions and self.is_complete:
            # Gold border for buildings with critical positions
            pygame.draw.rect(screen, (255, 215, 0), building_rect, 2)
        
        # Draw grid lines for multi-tile buildings
        if self.size > 1:
            for i in range(self.size + 1):
                # Vertical lines
                pygame.draw.line(screen, (100, 100, 100),
                               (screen_x + i * TILE_SIZE * zoom, screen_y),
                               (screen_x + i * TILE_SIZE * zoom, screen_y + size))
                # Horizontal lines
                pygame.draw.line(screen, (100, 100, 100),
                               (screen_x, screen_y + i * TILE_SIZE * zoom),
                               (screen_x + size, screen_y + i * TILE_SIZE * zoom))
        
        # Show building status indicators
        if self.is_complete:
            if hasattr(self, 'jobs') and self.jobs:
                # Show employment status for work buildings
                filled_jobs = len([job for job in self.jobs if job.employee])
                if filled_jobs < len(self.jobs):
                    # Draw "Help Wanted" indicator
                    pygame.draw.circle(screen, (255, 200, 0),
                                    (int(screen_x + size - 5), int(screen_y + 5)), 
                                    int(3 * zoom))
                
                # Show efficiency indicator if producing
                if self.produces and filled_jobs > 0:
                    # Draw efficiency bar (green to red based on efficiency)
                    eff_width = int((size - 6) * min(1.0, self.efficiency))
                    # Color ranges from red (0%) to yellow (50%) to green (100%)
                    if self.efficiency < 0.5:
                        # Red to yellow
                        eff_color = (255, int(255 * (self.efficiency * 2)), 0)
                    else:
                        # Yellow to green
                        eff_color = (int(255 * (2 - self.efficiency * 2)), 255, 0)
                    
                    pygame.draw.rect(screen, eff_color,
                                  (screen_x + 3, screen_y + size - 6,
                                   eff_width, 3))
            
            elif self.building_type in ['house', 'family_house']:
                # Show occupancy for houses
                if self.current_occupants < self.max_occupants:
                    # Draw "Vacancy" indicator
                    pygame.draw.circle(screen, (100, 255, 100),
                                    (int(screen_x + size - 5), int(screen_y + 5)),
                                    int(3 * zoom))
                
                # Special indicator for family houses
                if self.building_type == 'family_house':
                    # Heart icon for family houses
                    heart_size = int(4 * zoom)
                    pygame.draw.circle(screen, (255, 100, 100),
                                     (int(screen_x + size/2), int(screen_y + 5)),
                                     heart_size)
        else:
            # Show construction progress bar
            progress_width = (size - 4) * (self.construction_progress / self.build_time)
            pygame.draw.rect(screen, (200, 200, 200),
                            (screen_x + 2, screen_y + size - 4,
                             progress_width, 3 * zoom))

    def add_occupant(self):
        """Add an occupant to a house"""
        if self.building_type in ['house', 'family_house'] and self.current_occupants < self.capacity:
            self.current_occupants += 1
            return True
        return False

    def remove_occupant(self):
        """Remove an occupant from a house"""
        if self.building_type in ['house', 'family_house'] and self.current_occupants > 0:
            self.current_occupants -= 1
            return True
        return False
