import pygame
from ..config import BUILDING_TYPES, TILE_SIZE, RESOURCES, SUPPLY_DEMAND_IMPACT, INTEREST_RATE

class Job:
    def __init__(self, building_type, building, salary):
        self.building_type = building_type
        self.building = building
        self.salary = salary
        self.employee = None
        self.x = building.x
        self.y = building.y

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
        
        # Building state
        self.construction_progress = 0
        self.is_complete = False
        self.current_occupants = 0
        
        # Resource management
        self.inventory = {}
        self.production_timer = 0
        if 'produces' in building_config:
            self.produces = building_config['produces']
            self.production_rate = building_config['production_rate']
            self.inventory[self.produces] = 0
        if 'sells' in building_config:
            self.sells = building_config['sells']
            self.markup = building_config['markup']
            for resource in self.sells:
                self.inventory[resource] = 0
        if 'consumes' in building_config:
            self.consumes = building_config['consumes']
            self.inventory[self.consumes] = 0
        
        # Set building-specific properties
        if building_type == 'house':
            self.capacity = building_config['capacity']
        else:
            self.jobs = []
            self.max_jobs = building_config['jobs']
        
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
            'restaurant': (200, 100, 100),
            'bank': (200, 200, 50),
            'government': (200, 100, 100)
        }

    def get_grid_bounds(self):
        """Get the grid coordinates this building occupies"""
        grid_x, grid_y = self.world.get_grid_position(self.x, self.y)
        return [(grid_x + dx, grid_y + dy) 
                for dx in range(self.size) 
                for dy in range(self.size)]

    def update(self):
        if not self.is_complete:
            self.construction_progress += 1
            if self.construction_progress >= self.build_time:
                self.is_complete = True
                if self.building_type != 'house':
                    self.create_jobs()
        else:
            # Handle production
            if hasattr(self, 'produces'):
                self.production_timer += 1
                if self.production_timer >= 60:  # Produce every 60 ticks
                    self.produce_resources()
                    self.production_timer = 0
            
            # Handle sales
            if hasattr(self, 'sells'):
                self.handle_sales()
            
            # Handle banking
            if self.building_type == 'bank':
                self.handle_banking()
            
            # Track finances
            if len(self.profit_history) >= 30:  # Keep last 30 days
                self.profit_history.pop(0)
            self.profit_history.append(self.daily_revenue - self.daily_expenses)
            self.daily_revenue = 0
            self.daily_expenses = 0

    def produce_resources(self):
        """Handle resource production for production buildings"""
        if not hasattr(self, 'produces'):
            return
            
        # Check if we need to consume resources first
        if hasattr(self, 'consumes'):
            if self.inventory[self.consumes] < self.production_rate:
                return  # Not enough resources to produce
            self.inventory[self.consumes] -= self.production_rate
            
        # Calculate production based on number of workers
        efficiency = len([job for job in self.jobs if job.employee]) / self.max_jobs
        production = self.production_rate * efficiency
        
        self.inventory[self.produces] += production

    def handle_sales(self):
        """Handle resource sales for shops and restaurants"""
        for resource in self.sells:
            # Calculate demand based on nearby colonists
            nearby_colonists = [c for c in self.world.colonists 
                              if ((c.x - self.x)**2 + (c.y - self.y)**2)**0.5 < 100]
            demand = len(nearby_colonists) * 0.1
            
            # Calculate price based on supply and demand
            base_price = RESOURCES[resource]['base_price']
            supply_factor = self.inventory[resource] / 100  # Normalize inventory
            price = base_price * self.markup * (1 + SUPPLY_DEMAND_IMPACT * (demand - supply_factor))
            
            # Process sales
            sales = min(demand, self.inventory[resource])
            self.inventory[resource] -= sales
            self.daily_revenue += sales * price

    def handle_banking(self):
        """Handle banking operations"""
        for colonist in self.world.colonists:
            if colonist.money > 1000:  # Only pay interest on savings above 1000
                interest = (colonist.money - 1000) * INTEREST_RATE / 365  # Daily interest
                colonist.money += interest
                self.daily_expenses += interest

    def render(self, screen, camera_x=0, camera_y=0, zoom=1.0):
        """Render building with camera transformations"""
        # Calculate screen position with offset
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        size = int(self.base_size * zoom)
        
        color = self.colors[self.building_type]
        
        # Draw building centered on its position
        rect = pygame.Rect(screen_x - size//2, screen_y - size//2, 
                          size, size)
        
        if not self.is_complete:
            # Show construction progress
            progress = self.construction_progress / self.build_time
            progress_height = size * progress
            progress_rect = pygame.Rect(screen_x - size//2, 
                                      screen_y + size//2 - progress_height,
                                      size, progress_height)
            pygame.draw.rect(screen, (150, 150, 150), rect)
            pygame.draw.rect(screen, color, progress_rect)
        else:
            pygame.draw.rect(screen, color, rect)
            
            # Draw resource indicators
            if self.inventory:
                bar_width = max(2, int(3 * zoom))
                for i, (resource, amount) in enumerate(self.inventory.items()):
                    indicator_color = (255, 255, 0)  # Yellow for resources
                    indicator_height = min(size, amount / 20 * size)
                    indicator_rect = pygame.Rect(
                        screen_x - size//2 + (i+1)*5*zoom, 
                        screen_y + size//2 - indicator_height,
                        bar_width, indicator_height)
                    pygame.draw.rect(screen, indicator_color, indicator_rect)
        
        # Draw outline
        pygame.draw.rect(screen, (0, 0, 0), rect, max(1, int(2 * zoom)))
        
        # Draw occupancy indicator for houses
        if self.building_type == 'house' and self.is_complete:
            occupancy_color = (0, 255, 0) if self.current_occupants < self.capacity else (255, 0, 0)
            indicator_size = max(2, int(3 * zoom))
            pygame.draw.circle(screen, occupancy_color,
                             (screen_x, screen_y - size//2 - 5*zoom),
                             indicator_size)
        
        # Draw job indicators for businesses
        if self.building_type in ['shop', 'factory', 'farm', 'bank'] and self.is_complete:
            workers = len([job for job in self.jobs if job.employee])
            job_color = (0, 255, 0) if workers == self.max_jobs else (255, 255, 0)
            indicator_size = max(2, int(3 * zoom))
            pygame.draw.circle(screen, job_color,
                             (screen_x, screen_y - size//2 - 5*zoom),
                             indicator_size)

    def create_jobs(self):
        """Create jobs for business and government buildings"""
        if self.building_type in ['business', 'government']:
            base_salary = 50 if self.building_type == 'business' else 70
            jobs = []
            for _ in range(self.max_jobs):
                job = Job(self.building_type, self, base_salary)
                jobs.append(job)
            self.jobs = jobs
            return jobs
        return []

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
