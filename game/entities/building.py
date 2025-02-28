import pygame
import random
from ..config import (BUILDING_TYPES, TILE_SIZE, RESOURCES,
                     SUPPLY_DEMAND_IMPACT, INTEREST_RATE,
                     PRICE_VOLATILITY, MARKET_UPDATE_RATE, PRICE_MEMORY,
                     JOB_SALARIES, MINIMUM_WAGE, BASE_STORAGE_CAPACITY,
                     INVENTORY_UPDATE_RATE, HAPPINESS_RADIUS, WORK_RADIUS)

class Job:
    def __init__(self, building):
        self.building = building
        self.building_type = building.building_type
        self.employee = None
        self.x = building.x
        self.y = building.y
        
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
        else:
            self.type = 'worker'
            self.salary = MINIMUM_WAGE

class Building:
    def __init__(self, building_type, x, y, world):
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
        
        # Storage capacity
        self.storage_multiplier = building_config.get('storage_multiplier', 1.0)
        self.max_storage = BASE_STORAGE_CAPACITY * self.storage_multiplier
        
        # Building state
        self.construction_progress = 0
        self.is_complete = False
        self.current_occupants = 0
        self.jobs = []
        
        # Initialize inventory and prices
        self.inventory = {}
        self.prices = {}
        self.price_history = []
        self.last_market_update = 0
        
        # Set up based on building type
        if building_type == 'house':
            self.max_occupants = building_config.get('max_occupants', 4)
            self.current_occupants = 0
        elif building_type in ['shop', 'factory', 'farm', 'woodcutter', 'quarry', 'mine', 'workshop']:
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
            'farm': (150, 200, 50),
            'factory': (150, 150, 150),
            'shop': (200, 150, 100),
            'woodcutter': (139, 69, 19),
            'quarry': (169, 169, 169),
            'mine': (105, 105, 105),
            'workshop': (200, 200, 100),
            'market': (200, 150, 100),
            'tavern': (200, 100, 200),
            'government': (150, 150, 200)
        }

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
        else:
            # Operational phase
            if self.building_type in ['farm', 'woodcutter', 'quarry', 'mine', 'workshop']:
                self.produce_resources()
            
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
            
            # Handle production
            if self.produces and self.jobs:
                active_workers = len([job for job in self.jobs if job.employee])
                if active_workers > 0:
                    efficiency = active_workers / self.max_jobs
                    production = self.production_rate * efficiency * speed_multiplier
                    self.world.add_to_colony_inventory(self.produces, production)

            # Apply happiness bonus to nearby colonists
            if self.happiness_bonus > 0:
                for colonist in self.world.colonists:
                    distance = ((colonist.x - self.x)**2 + (colonist.y - self.y)**2)**0.5
                    if distance < 200:  # Happiness bonus radius
                        colonist.happiness = min(100, colonist.happiness + 
                                              (self.happiness_bonus / 100) * speed_multiplier)

    def produce_resources(self):
        """Produce resources if this is a production building with enhanced efficiency"""
        if not self.produces or not self.is_complete:
            return
            
        workers = [job.employee for job in self.jobs if job.employee]
        if not workers:
            # Small passive production even without workers
            passive_production = self.production_rate * 0.1
            
            # Apply storage limit
            current_amount = self.inventory.get(self.produces, 0)
            new_amount = min(current_amount + passive_production, self.max_storage)
            self.inventory[self.produces] = new_amount
            
            # Transfer to colony inventory periodically
            if self.world.day_timer % 100 == 0:  # Every 100 ticks
                transfer_amount = min(current_amount, 5.0)  # Small transfer
                if transfer_amount > 0:
                    self.inventory[self.produces] -= transfer_amount
                    
                    # Ensure colony inventory tracks the resource
                    if self.produces not in self.world.colony_inventory:
                        self.world.colony_inventory[self.produces] = 0
                        
                    self.world.colony_inventory[self.produces] += transfer_amount
            return
        
        # Calculate base efficiency based on worker count
        base_efficiency = len(workers) / max(1, self.max_jobs)
        
        # Calculate bonus based on worker skills and traits
        skill_bonus = 0
        for worker in workers:
            # Different skills matter for different buildings
            if self.building_type == 'farm':
                skill_bonus += worker.traits.get('work_ethic', 50) / 500  # 0-0.2 bonus
            elif self.building_type in ['woodcutter', 'quarry', 'mine']:
                skill_bonus += worker.traits.get('ambition', 50) / 500  # 0-0.2 bonus
            elif self.building_type == 'workshop':
                skill_bonus += worker.traits.get('creativity', 50) / 500  # 0-0.2 bonus
            
            # Give non-farm buildings a bonus to counter farm preference
            if self.building_type != 'farm':
                skill_bonus += 0.1  # Extra 10% bonus for non-farms
        
        # Calculate total production with enhanced bonuses
        efficiency = base_efficiency + skill_bonus
        production = self.production_rate * efficiency
        
        # Apply building-specific production bonuses to counter farm bias
        if self.building_type == 'woodcutter':
            production *= 1.25  # Woodcutter bonus
        elif self.building_type == 'quarry':
            production *= 1.2   # Quarry bonus 
        elif self.building_type == 'mine':
            production *= 1.25  # Mine bonus
        elif self.building_type == 'workshop':
            production *= 1.3   # Workshop gets best bonus
        
        # Apply storage limit
        current_amount = self.inventory.get(self.produces, 0)
        new_amount = min(current_amount + production, self.max_storage)
        self.inventory[self.produces] = new_amount
        
        # Transfer resources to colony inventory if we have workers
        if workers and len(workers) > 0:
            transfer_amount = min(new_amount, production * 2)  # Transfer up to 2x production
            if transfer_amount > 0:
                self.inventory[self.produces] -= transfer_amount
                
                # Make sure the colony inventory has this resource type
                if self.produces not in self.world.colony_inventory:
                    self.world.colony_inventory[self.produces] = 0
                    
                self.world.colony_inventory[self.produces] += transfer_amount
                
                # Show indicator for resource production
                for worker in workers:
                    worker.current_task = f"working at {self.building_type}"

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
                interest = colonist.money * (self.interest_rate / 365)  # Daily interest
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
        if not self.is_complete:
            # Show construction progress
            progress = self.construction_progress / self.build_time
            color = tuple(int(c * (0.5 + 0.5 * progress)) for c in color)
        
        # Draw building
        pygame.draw.rect(screen, color, building_rect)
        
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
            if hasattr(self, 'jobs'):
                # Show employment status for work buildings
                filled_jobs = len([job for job in self.jobs if job.employee])
                if self.jobs and filled_jobs < len(self.jobs):
                    # Draw "Help Wanted" indicator
                    pygame.draw.circle(screen, (255, 200, 0),
                                    (int(screen_x + size - 5), int(screen_y + 5)), 
                                    int(3 * zoom))
            elif self.building_type == 'house':
                # Show occupancy for houses
                if self.current_occupants < self.capacity:
                    # Draw "Vacancy" indicator
                    pygame.draw.circle(screen, (100, 255, 100),
                                    (int(screen_x + size - 5), int(screen_y + 5)),
                                    int(3 * zoom))
        else:
            # Show construction progress bar
            progress_width = (size - 4) * (self.construction_progress / self.build_time)
            pygame.draw.rect(screen, (200, 200, 200),
                            (screen_x + 2, screen_y + size - 4,
                             progress_width, 3 * zoom))

    def add_occupant(self):
        """Add an occupant to a house"""
        if self.building_type == 'house' and self.current_occupants < self.capacity:
            self.current_occupants += 1
            return True
        return False

    def remove_occupant(self):
        """Remove an occupant from a house"""
        if self.building_type == 'house' and self.current_occupants > 0:
            self.current_occupants -= 1
            return True
        return False
