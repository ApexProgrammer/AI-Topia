import pygame
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
            self.capacity = building_config['max_occupants']
        elif building_type in ['shop', 'factory', 'farm', 'woodcutter', 'quarry', 'mine', 'workshop']:
            if self.produces:
                self.inventory[self.produces] = 0
                
            if 'sells' in building_config:
                self.sells = building_config['sells']
                self.markup = building_config['markup']
                for resource in self.sells:
                    self.inventory[resource] = 0
                    self.prices[resource] = RESOURCES[resource]['base_price'] * self.markup
        
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
            self.construction_progress += 1
            if self.construction_progress >= self.build_time:
                self.is_complete = True
                if self.building_type != 'house':
                    self.create_jobs()
        else:
            # Handle production
            if hasattr(self, 'produces'):
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
        """Produce resources if this is a production building"""
        if not hasattr(self, 'produces') or not self.is_complete:
            return
            
        workers = len([job for job in self.jobs if job.employee])
        if workers > 0:
            efficiency = workers / self.max_jobs
            production = self.production_rate * efficiency
            self.inventory[self.produces] = self.inventory.get(self.produces, 0) + production

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
        if not self.max_jobs:
            return []
            
        jobs = []
        for _ in range(self.max_jobs):
            job = Job(self)
            if self.produces:
                job.type = f"{self.produces}_gatherer"
            else:
                job.type = f"{self.building_type}_worker"
            self.jobs.append(job)
            jobs.append(job)
        return jobs

    def render(self, screen, camera_x=0, camera_y=0, zoom=1.0):
        """Render building with camera transformations"""
        # Calculate screen position
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        size = int(self.size * TILE_SIZE * zoom)
        
        # Draw building
        rect = pygame.Rect(screen_x - size//2, screen_y - size//2, size, size)
        
        if not self.is_complete:
            # Show construction progress
            progress = self.construction_progress / self.build_time
            progress_height = size * progress
            progress_rect = pygame.Rect(screen_x - size//2, 
                                      screen_y + size//2 - progress_height,
                                      size, progress_height)
            pygame.draw.rect(screen, (150, 150, 150), rect)
            pygame.draw.rect(screen, (100, 200, 100), progress_rect)
        else:
            # Draw completed building
            if self.building_type == 'house':
                color = (100, 200, 100)
            elif self.building_type == 'farm':
                color = (150, 200, 50)
            elif self.building_type == 'factory':
                color = (150, 150, 150)
            elif self.building_type == 'shop':
                color = (200, 150, 100)
            elif self.building_type == 'bank':
                color = (200, 200, 50)
            else:
                color = (200, 100, 100)
                
            pygame.draw.rect(screen, color, rect)
            
            # Draw resource indicators
            if hasattr(self, 'inventory'):
                bar_width = max(2, int(3 * zoom))
                for i, (resource, amount) in enumerate(self.inventory.items()):
                    max_amount = 100
                    height = min(1.0, amount / max_amount) * size
                    indicator_rect = pygame.Rect(
                        screen_x - size//2 + (i+1)*5*zoom,
                        screen_y + size//2 - height,
                        bar_width, height
                    )
                    pygame.draw.rect(screen, (255, 255, 0), indicator_rect)
        
        # Draw outline
        pygame.draw.rect(screen, (0, 0, 0), rect, max(1, int(2 * zoom)))
        
        # Draw status indicators
        if self.is_complete:
            if self.building_type == 'house':
                # Show occupancy
                occupancy_color = (0, 255, 0) if self.current_occupants < self.capacity else (255, 0, 0)
                pygame.draw.circle(screen, occupancy_color,
                                 (screen_x, screen_y - size//2 - 5*zoom),
                                 max(2, int(3 * zoom)))
            elif hasattr(self, 'jobs'):
                # Show employment
                workers = len([job for job in self.jobs if job.employee])
                job_color = (0, 255, 0) if workers == self.max_jobs else (255, 255, 0)
                pygame.draw.circle(screen, job_color,
                                 (screen_x, screen_y - size//2 - 5*zoom),
                                 max(2, int(3 * zoom)))

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
