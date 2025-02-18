import pygame
import random
from .entities.colonist import Colonist
from .entities.building import Building
from .config import (TILE_SIZE, INITIAL_MAP_SIZE, EXPANSION_BUFFER, MIN_MAP_SIZE,
                    MAX_MAP_SIZE, EXPANSION_COST, BUILDING_TYPES,
                    REPRODUCTION_AGE_MIN, REPRODUCTION_AGE_MAX,
                    COLONISTS_PER_TILE, BUILDINGS_PER_TILE,
                    MIN_BUILDING_SPACING, BUILDING_MARGIN,
                    INITIAL_COLONISTS, CONSTRUCTION_SKILL_THRESHOLD,
                    MIN_MONEY_FOR_BUILDING, BUILDING_CHANCE, TAX_RATE, INTEREST_RATE,
                    INITIAL_TREASURY)

class World:
    def __init__(self, screen_width=None, screen_height=None):
        self.current_size = INITIAL_MAP_SIZE
        self.width = self.current_size * TILE_SIZE
        self.height = self.current_size * TILE_SIZE
        self.ui = None
        
        # Store screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate center offset
        if screen_width and screen_height:
            self.offset_x = (screen_width - self.width) // 2
            self.offset_y = (screen_height - self.height) // 2
        else:
            self.offset_x = 0
            self.offset_y = 0
        
        # Initialize lists
        self.colonists = []
        self.buildings = []
        self.jobs = []
        self.homes = []
        
        # Initialize state
        self.treasury = INITIAL_TREASURY
        self.gdp = 0
        self.leader = None
        self.election_timer = 0
        self.election_candidates = []
        self.term_length = 1000
        
        # History tracking
        self.expansion_history = []
        self.birth_history = []
        self.death_history = []
        self.election_history = []
        self.economic_history = []  # Track economic metrics
        
        # Grid tracking
        self.grid_occupation = {}
        
        # Generate initial colony
        self.generate_initial_colony()

    def world_to_screen(self, pos):
        """Convert world coordinates to screen coordinates"""
        if isinstance(pos, tuple):
            x, y = pos
        else:
            x, y = pos[0], pos[1]
        return (x + self.offset_x, y + self.offset_y)

    def screen_to_world(self, pos):
        """Convert screen coordinates to world coordinates"""
        if isinstance(pos, tuple):
            x, y = pos
        else:
            x, y = pos[0], pos[1]
        return (x - self.offset_x, y - self.offset_y)

    def get_grid_position(self, x, y=None):
        """Convert world coordinates to grid coordinates"""
        if y is None and isinstance(x, (tuple, list)):
            x, y = x[0], x[1]
        # Remove offset for grid calculation
        x = x - self.offset_x
        y = y - self.offset_y
        return (int(x / TILE_SIZE), int(y / TILE_SIZE))

    def get_pixel_position(self, x, y=None):
        """Convert grid coordinates to world coordinates (center of tile)"""
        if y is None and isinstance(x, (tuple, list)):
            x, y = x[0], x[1]
        # Convert to pixel coordinates and add offset
        world_x = x * TILE_SIZE + TILE_SIZE // 2 + self.offset_x
        world_y = y * TILE_SIZE + TILE_SIZE // 2 + self.offset_y
        return (world_x, world_y)

    def find_building_location(self, building_type):
        """Find a suitable grid location for a new building"""
        building_size = BUILDING_TYPES[building_type]['size']
        spacing = MIN_BUILDING_SPACING
        margin = BUILDING_MARGIN
        
        # Calculate valid grid range considering margins
        min_x = margin
        min_y = margin
        max_x = self.current_size - building_size - margin
        max_y = self.current_size - building_size - margin
        
        # Try random positions until we find a suitable one
        attempts = 50  # Limit attempts to avoid infinite loop
        for _ in range(attempts):
            # Choose random position within valid range
            grid_x = random.randint(min_x, max_x)
            grid_y = random.randint(min_y, max_y)
            
            # Check if area is clear including spacing
            area_clear = True
            for dx in range(-spacing, building_size + spacing):
                for dy in range(-spacing, building_size + spacing):
                    check_x = grid_x + dx
                    check_y = grid_y + dy
                    
                    # Check if position is within world bounds
                    if (0 <= check_x < self.current_size and 
                        0 <= check_y < self.current_size):
                        if self.is_grid_occupied(check_x, check_y):
                            area_clear = False
                            break
                    else:
                        area_clear = False
                        break
                        
                if not area_clear:
                    break
            
            if area_clear:
                return (grid_x, grid_y)
        
        return None

    def create_building(self, building_type, x, y):
        """Create a new building at the specified location"""
        # Convert to grid coordinates
        grid_x, grid_y = self.get_grid_position(x, y)
        building_size = BUILDING_TYPES[building_type]['size']
        
        # Validate position
        if (grid_x < 0 or grid_x + building_size > self.current_size or
            grid_y < 0 or grid_y + building_size > self.current_size):
            return False
        
        # Check if area is clear
        for dx in range(building_size):
            for dy in range(building_size):
                if self.is_grid_occupied(grid_x + dx, grid_y + dy):
                    return False
        
        # Create building
        building = Building(building_type, x, y, self)
        self.buildings.append(building)
        
        # Occupy grid positions
        for dx in range(building_size):
            for dy in range(building_size):
                self.add_to_grid(building, grid_x + dx, grid_y + dy)
        
        # Add to appropriate lists
        if building_type == 'house':
            self.homes.append(building)
        elif building_type in ['shop', 'factory', 'farm', 'bank', 'government']:
            self.jobs.extend(building.create_jobs())
        
        return True

    def generate_initial_colony(self):
        """Generate initial colony"""
        # Calculate center of grid
        center_x = self.current_size // 2
        center_y = self.current_size // 2
        
        # Create central government building
        gov_pos = self.get_pixel_position(center_x, center_y)
        gov_building = Building('government', gov_pos[0], gov_pos[1], self)
        self.buildings.append(gov_building)
        self.add_to_grid(gov_building, center_x, center_y)
        self.jobs.extend(gov_building.create_jobs())
        
        # Create houses in a ring around center
        house_offsets = [
            (-2, -2), (0, -2), (2, -2),  # Top row
            (-2, 0),           (2, 0),    # Middle row
            (-2, 2),  (0, 2),  (2, 2)     # Bottom row
        ]
        
        for offset_x, offset_y in house_offsets:
            grid_x = center_x + offset_x
            grid_y = center_y + offset_y
            if 0 <= grid_x < self.current_size and 0 <= grid_y < self.current_size:
                pos = self.get_pixel_position(grid_x, grid_y)
                house = Building('house', pos[0], pos[1], self)
                self.buildings.append(house)
                self.homes.append(house)
                self.add_to_grid(house, grid_x, grid_y)
        
        # Create shop and farm
        shop_pos = self.get_pixel_position(center_x + 3, center_y + 3)
        farm_pos = self.get_pixel_position(center_x - 3, center_y + 3)
        
        shop = Building('shop', shop_pos[0], shop_pos[1], self)
        farm = Building('farm', farm_pos[0], farm_pos[1], self)
        
        self.buildings.extend([shop, farm])
        self.add_to_grid(shop, center_x + 3, center_y + 3)
        self.add_to_grid(farm, center_x - 3, center_y + 3)
        
        self.jobs.extend(shop.create_jobs())
        self.jobs.extend(farm.create_jobs())
        
        # Create initial colonists near buildings
        for _ in range(INITIAL_COLONISTS):
            building = random.choice(self.buildings)
            building_grid_x, building_grid_y = self.get_grid_position(building.x, building.y)
            
            # Find empty adjacent tile
            placed = False
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                colonist_grid_x = building_grid_x + dx
                colonist_grid_y = building_grid_y + dy
                
                if (0 <= colonist_grid_x < self.current_size and 
                    0 <= colonist_grid_y < self.current_size):
                    
                    if not self.is_grid_occupied(colonist_grid_x, colonist_grid_y):
                        colonist_pos = self.get_pixel_position(colonist_grid_x, colonist_grid_y)
                        colonist = Colonist(colonist_pos[0], colonist_pos[1], self)
                        self.colonists.append(colonist)
                        self.add_to_grid(colonist, colonist_grid_x, colonist_grid_y)
                        placed = True
                        break
            
            if not placed:
                # If no empty adjacent tile, place randomly near building
                for _ in range(10):  # Try 10 times to find a spot
                    offset_x = random.randint(-2, 2)
                    offset_y = random.randint(-2, 2)
                    colonist_grid_x = max(0, min(self.current_size - 1, building_grid_x + offset_x))
                    colonist_grid_y = max(0, min(self.current_size - 1, building_grid_y + offset_y))
                    
                    if not self.is_grid_occupied(colonist_grid_x, colonist_grid_y):
                        colonist_pos = self.get_pixel_position(colonist_grid_x, colonist_grid_y)
                        colonist = Colonist(colonist_pos[0], colonist_pos[1], self)
                        self.colonists.append(colonist)
                        self.add_to_grid(colonist, colonist_grid_x, colonist_grid_y)
                        break

    def render(self, screen):
        # Get camera offset
        camera_x = self.ui.camera_x if self.ui else 0
        camera_y = self.ui.camera_y if self.ui else 0
        zoom = self.ui.zoom if self.ui else 1.0
        
        # Draw background
        background = (20, 20, 20)
        pygame.draw.rect(screen, background,
                        (self.offset_x + camera_x,
                         self.offset_y + camera_y,
                         self.width, self.height))
        
        # Draw grid
        grid_color = (40, 40, 40)
        for x in range(self.current_size + 1):
            screen_x = self.offset_x + x * TILE_SIZE + camera_x
            pygame.draw.line(screen, grid_color,
                           (screen_x, self.offset_y + camera_y),
                           (screen_x, self.offset_y + self.height + camera_y))
            
        for y in range(self.current_size + 1):
            screen_y = self.offset_y + y * TILE_SIZE + camera_y
            pygame.draw.line(screen, grid_color,
                           (self.offset_x + camera_x, screen_y),
                           (self.offset_x + self.width + camera_x, screen_y))
        
        # Draw entities
        for building in self.buildings:
            building.render(screen, camera_x, camera_y, zoom)
        
        for colonist in self.colonists:
            colonist.render(screen, camera_x, camera_y, zoom)

    def update(self):
        # Update colonists
        for colonist in self.colonists:
            colonist.update()
        
        # Update buildings
        for building in self.buildings:
            building.update()
        
        # Update systems
        self.update_economy()
        self.update_government()
        self.handle_reproduction()
        self.handle_deaths()

    def update_economy(self):
        """Update the colony's economy"""
        current_time = pygame.time.get_ticks()
        
        # Calculate GDP
        self.gdp = sum(c.money for c in self.colonists)
        
        # Calculate tax revenue
        tax_revenue = 0
        for colonist in self.colonists:
            if colonist.job and colonist.money > 0:
                tax = colonist.money * TAX_RATE
                colonist.money -= tax
                colonist.inventory['money'] = colonist.money
                tax_revenue += tax
        
        # Calculate government expenses
        gov_expenses = sum(job.salary / 30 for job in self.jobs 
                         if job.building_type == 'government' and job.employee)
        
        # Update treasury with minimum safeguard
        self.treasury = max(1000, self.treasury + tax_revenue - gov_expenses)
        
        # Pay workers based on available funds
        available_funds = self.treasury - 1000  # Keep minimum reserve
        if available_funds > 0:
            total_salaries = sum(job.salary / 30 for job in self.jobs if job.employee)
            if total_salaries > 0:
                payment_ratio = min(1.0, available_funds / total_salaries)
                
                for job in self.jobs:
                    if job.employee:
                        salary = (job.salary / 30) * payment_ratio  # Adjusted daily wage
                        self.treasury -= salary
                        job.employee.money += salary
                        job.employee.inventory['money'] = job.employee.money
        
        # Handle building operations
        for building in self.buildings:
            if building.is_complete:
                # Process production
                if hasattr(building, 'produces'):
                    workers = len([job for job in building.jobs if job.employee])
                    if workers > 0:
                        efficiency = workers / building.max_jobs
                        production = building.production_rate * efficiency
                        building.inventory[building.produces] = (
                            building.inventory.get(building.produces, 0) + production
                        )
                
                # Process sales
                if hasattr(building, 'sells'):
                    for resource in building.sells:
                        if resource in building.inventory and building.inventory[resource] > 0:
                            # Calculate demand
                            nearby_colonists = [c for c in self.colonists 
                                              if ((c.x - building.x)**2 + 
                                                  (c.y - building.y)**2)**0.5 < 200]
                            potential_buyers = len(nearby_colonists)
                            
                            # Process sales
                            price = building.prices[resource]
                            max_sales = min(building.inventory[resource], potential_buyers)
                            actual_sales = 0
                            
                            for colonist in nearby_colonists:
                                if colonist.money >= price and building.inventory[resource] > 0:
                                    # Make purchase
                                    colonist.money -= price
                                    colonist.inventory['money'] = colonist.money
                                    colonist.inventory[resource] = (
                                        colonist.inventory.get(resource, 0) + 1
                                    )
                                    building.inventory[resource] -= 1
                                    building.daily_revenue += price
                                    actual_sales += 1
                                    
                                    if actual_sales >= max_sales:
                                        break
        
        # Record economic metrics
        self.economic_history.append({
            'time': current_time,
            'gdp': self.gdp,
            'treasury': self.treasury,
            'tax_revenue': tax_revenue,
            'expenses': gov_expenses
        })
        
        # Keep history manageable
        if len(self.economic_history) > 100:
            self.economic_history = self.economic_history[-100:]
    
    def update_government(self):
        self.election_timer += 1
        
        # Hold election every 1000 ticks
        if self.election_timer >= 1000:
            self.force_election()
            self.election_timer = 0
        
        # Government policies affect colony
        if self.leader:
            # Leader's political alignment affects policies
            tax_modifier = 0.5 + self.leader.political_alignment  # Higher for progressive
            minimum_wage_modifier = 0.8 + self.leader.political_alignment * 0.4
            
            # Update economic policies
            for job in self.jobs:
                if job.salary < 10 * minimum_wage_modifier:
                    job.salary = 10 * minimum_wage_modifier
            
            # Collect taxes based on leader's policy
            tax_revenue = sum(c.money * 0.1 * tax_modifier for c in self.colonists)
            self.treasury += tax_revenue

    def force_election(self):
        """Force an immediate election"""
        candidates = [c for c in self.colonists 
                     if c.age >= 35 and c.leadership >= 60]
        
        if not candidates:
            return
        
        # Each colonist votes based on their political alignment
        votes = {}
        for voter in self.colonists:
            if voter.age >= 18:  # Voting age
                # Find candidate with closest political alignment
                best_candidate = min(candidates,
                    key=lambda c: abs(c.political_alignment - voter.political_alignment))
                votes[best_candidate] = votes.get(best_candidate, 0) + 1
                voter.voted_for = best_candidate
        
        # Determine winner
        if votes:
            self.leader = max(votes.keys(), key=lambda c: votes[c])
            # Give leader bonus
            self.leader.money += 1000
            self.leader.happiness += 20

    def handle_reproduction(self):
        """Handle colonist reproduction with more factors"""
        current_time = pygame.time.get_ticks()
        
        for colonist in self.colonists:
            if (colonist.spouse and 
                colonist.gender == 'F' and 
                REPRODUCTION_AGE_MIN <= colonist.age <= REPRODUCTION_AGE_MAX):
                
                # Check reproduction cooldown
                last_birth_time = 0
                for birth in self.birth_history:
                    if birth['parents'][0] == colonist or birth['parents'][1] == colonist:
                        last_birth_time = max(last_birth_time, birth['time'])
                
                if current_time - last_birth_time < 10000:
                    continue
                
                # Calculate birth probability based on:
                # 1. Base chance
                # 2. Health and happiness
                # 3. Economic situation
                # 4. Government policies
                
                health_factor = (colonist.health + colonist.spouse.health) / 200
                happiness_factor = (colonist.happiness + colonist.spouse.happiness) / 200
                economic_factor = min(1.0, (colonist.money + colonist.spouse.money) / 5000)
                
                # Policy effects
                policy_factor = 1.0
                if self.ui and self.ui.policies['birth_incentive'] > 0:
                    policy_factor += self.ui.policies['birth_incentive'] / 1000
                
                birth_chance = (0.01 * 
                              health_factor * 
                              happiness_factor * 
                              economic_factor * 
                              policy_factor)
                
                if random.random() < birth_chance:
                    # Create new colonist
                    x, y = colonist.x, colonist.y
                    child = Colonist(x, y, self)
                    child.age = 0
                    
                    # Inherit traits from parents
                    for trait in child.traits:
                        child.traits[trait] = (
                            colonist.traits[trait] * 0.5 +
                            colonist.spouse.traits[trait] * 0.5 +
                            random.randint(-10, 10)
                        )
                        child.traits[trait] = max(0, min(100, child.traits[trait]))
                    
                    # Political alignment influenced by parents
                    child.political_alignment = (
                        colonist.political_alignment * 0.4 +
                        colonist.spouse.political_alignment * 0.4 +
                        random.random() * 0.2
                    )
                    
                    # Add to world
                    self.colonists.append(child)
                    colonist.children.append(child)
                    colonist.spouse.children.append(child)
                    
                    # Record birth
                    self.birth_history.append({
                        'time': current_time,
                        'child': child,
                        'parents': (colonist, colonist.spouse)
                    })
                    
                    # Apply birth incentive
                    if self.ui and self.ui.policies['birth_incentive'] > 0:
                        colonist.money += self.ui.policies['birth_incentive']
                        colonist.inventory['money'] = colonist.money
                    
                    # Update grid position
                    grid_x, grid_y = self.get_grid_position(x, y)
                    self.add_to_grid(child, grid_x, grid_y)

    def handle_deaths(self):
        """Handle colonist deaths"""
        current_time = pygame.time.get_ticks()
        
        for colonist in self.colonists[:]:  # Copy list to allow removal
            # Death conditions:
            # 1. Old age (increased chance after 70)
            # 2. Poor health
            # 3. Accidents (very small chance)
            
            death_chance = 0
            
            if colonist.age > 70:
                death_chance += (colonist.age - 70) * 0.0001
            
            if colonist.health < 20:
                death_chance += (20 - colonist.health) * 0.001
            
            death_chance += 0.0001  # Base accident chance
            
            # Policy effects
            if self.ui and self.ui.policies['healthcare']:
                death_chance *= 0.5
            
            if random.random() < death_chance:
                # Record death
                self.death_history.append({
                    'time': current_time,
                    'colonist': colonist,
                    'age': colonist.age,
                    'cause': 'natural' if colonist.age > 70 else 'health' if colonist.health < 20 else 'accident'
                })
                
                # Remove from lists
                self.colonists.remove(colonist)
                if colonist.job:
                    colonist.job.employee = None
                if colonist.home:
                    colonist.home.current_occupants -= 1
                if colonist == self.leader:
                    self.leader = None
                    self.election_timer = self.term_length  # Trigger immediate election

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle colonist selection for information display
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self.screen_to_world(mouse_pos)
            
            for colonist in self.colonists:
                dx = colonist.x - world_pos[0]
                dy = colonist.y - world_pos[1]
                if (dx*dx + dy*dy) < 100:  # Click radius
                    self.ui.selected_colonist = colonist
                    self.ui.show_colonist_info = True
                    break

    def add_to_grid(self, entity, grid_x, grid_y):
        """Add an entity to a grid position"""
        if (grid_x, grid_y) not in self.grid_occupation:
            self.grid_occupation[(grid_x, grid_y)] = []
        self.grid_occupation[(grid_x, grid_y)].append(entity)

    def remove_from_grid(self, entity, grid_x, grid_y):
        """Remove an entity from a grid position"""
        if (grid_x, grid_y) in self.grid_occupation:
            if entity in self.grid_occupation[(grid_x, grid_y)]:
                self.grid_occupation[(grid_x, grid_y)].remove(entity)

    def get_grid_occupants(self, grid_x, grid_y):
        """Get all entities in a grid position"""
        return self.grid_occupation.get((grid_x, grid_y), [])

    def is_grid_occupied(self, grid_x, grid_y):
        """Check if a grid position is occupied"""
        return (grid_x, grid_y) in self.grid_occupation

    def check_expansion_needed(self):
        """Check if map needs to expand based on population density"""
        total_tiles = self.current_size * self.current_size
        colonist_density = len(self.colonists) / total_tiles
        building_density = len(self.buildings) / total_tiles
        
        return (colonist_density > COLONISTS_PER_TILE or 
                building_density > BUILDINGS_PER_TILE)

    def expand_map(self):
        """Expand the map size"""
        if self.current_size >= MAX_MAP_SIZE:
            return False
            
        if self.treasury < EXPANSION_COST:
            return False
            
        old_size = self.current_size
        self.current_size += EXPANSION_BUFFER
        self.width = self.current_size * TILE_SIZE
        self.height = self.current_size * TILE_SIZE
        
        # Record expansion
        self.expansion_history.append({
            'time': pygame.time.get_ticks(),
            'old_size': old_size,
            'new_size': self.current_size,
            'cost': EXPANSION_COST
        })
        
        self.treasury -= EXPANSION_COST
        return True

    def set_ui(self, ui):
        """Set the UI reference after initialization"""
        self.ui = ui

    def get_available_jobs(self):
        return [job for job in self.jobs if not job.employee]

    def get_available_homes(self):
        return [home for home in self.homes if home.current_occupants < home.capacity]

    def get_potential_partners(self, colonist):
        return [c for c in self.colonists 
                 if c != colonist and 
                 not c.spouse and 
                 c.gender != colonist.gender and 
                 abs(c.age - colonist.age) < 10]

    def update_election(self):
        """Handle election process"""
        self.election_timer += 1
        
        # Start election process when timer is close to term length
        if self.election_timer >= self.term_length - 200 and not self.election_candidates:
            self.start_election()
        
        # Hold election when timer expires
        if self.election_timer >= self.term_length:
            self.hold_election()
            self.election_timer = 0
            self.election_candidates = []

    def start_election(self):
        """Begin election process by selecting candidates"""
        # Find potential candidates
        potential_candidates = [c for c in self.colonists 
                              if c.age >= 35 and c.leadership >= 60 and c.job]
        
        # Select top candidates based on leadership and experience
        self.election_candidates = sorted(
            potential_candidates,
            key=lambda c: (c.leadership + c.business_skill + c.construction_skill) / 3,
            reverse=True
        )[:5]  # Top 5 candidates

    def hold_election(self):
        """Hold election with current candidates"""
        if not self.election_candidates:
            return
            
        # Each colonist votes based on political alignment and candidate qualities
        votes = {candidate: 0 for candidate in self.election_candidates}
        
        for voter in self.colonists:
            if voter.age >= 18:  # Voting age
                # Calculate vote preference based on:
                # 1. Political alignment (40% weight)
                # 2. Leadership skill (30% weight)
                # 3. Economic success (30% weight)
                
                best_candidate = max(
                    self.election_candidates,
                    key=lambda c: (
                        (1 - abs(c.political_alignment - voter.political_alignment)) * 0.4 +
                        (c.leadership / 100) * 0.3 +
                        (c.money / 10000) * 0.3
                    )
                )
                
                votes[best_candidate] += 1
                voter.voted_for = best_candidate
        
        # Determine winner
        self.leader = max(votes.keys(), key=lambda c: votes[c])
        
        # Record election results
        self.election_history.append({
            'time': pygame.time.get_ticks(),
            'winner': self.leader,
            'candidates': self.election_candidates.copy(),
            'votes': votes.copy()
        })
        
        # Apply election effects
        self.leader.money += 1000  # Election bonus
        self.leader.happiness += 20

    def consider_autonomous_building(self, colonist):
        """Colonist decides what to build based on colony needs"""
        # Check if colonist meets building requirements
        if (colonist.construction_skill < CONSTRUCTION_SKILL_THRESHOLD or
            colonist.money < MIN_MONEY_FOR_BUILDING or
            random.random() > BUILDING_CHANCE):
            return
            
        # Analyze colony needs
        housing_ratio = len([c for c in self.colonists if not c.home]) / max(1, len(self.colonists))
        job_ratio = len([c for c in self.colonists if not c.job]) / max(1, len(self.colonists))
        
        # Calculate food per colonist
        total_food = sum(c.inventory.get('food', 0) for c in self.colonists)
        food_per_colonist = total_food / max(1, len(self.colonists))
        
        # Calculate priorities based on needs
        priorities = []
        
        # Critical needs (high priority)
        if housing_ratio > 0.2:  # More than 20% homeless
            priorities.append(('house', 5 * (1 + housing_ratio)))
        if food_per_colonist < 5:  # Less than 5 food per colonist
            priorities.append(('farm', 4 * (1 + (5 - food_per_colonist)/5)))
        if job_ratio > 0.3:  # More than 30% unemployed
            priorities.append(('factory', 3 * (1 + job_ratio)))
            priorities.append(('shop', 3 * (1 + job_ratio)))
        
        # Development needs (medium priority)
        if len(self.buildings) > 5:
            bank_count = len([b for b in self.buildings if b.building_type == 'bank'])
            if bank_count < len(self.colonists) / 20:  # 1 bank per 20 colonists
                priorities.append(('bank', 2))
        
        # Government needs (lower priority)
        if len(self.colonists) > 20:
            gov_count = len([b for b in self.buildings if b.building_type == 'government'])
            if gov_count < len(self.colonists) / 30:  # 1 government per 30 colonists
                priorities.append(('government', 1))
        
        if priorities:
            # Choose building type based on weighted priorities
            building_type, priority = max(priorities, key=lambda x: x[1] * (0.8 + random.random() * 0.4))
            building_cost = BUILDING_TYPES[building_type]['cost']
            
            if colonist.money >= building_cost:
                # Find suitable location
                location = self.find_building_location(building_type)
                if location:
                    grid_x, grid_y = location
                    pos = self.get_pixel_position(grid_x, grid_y)
                    
                    # Create building
                    if self.create_building(building_type, pos[0], pos[1]):
                        colonist.money -= building_cost
                        colonist.inventory['money'] = colonist.money
                        colonist.happiness += 10  # Happiness boost for successful building
                        
                        # Set colonist's task
                        colonist.current_task = 'building'
                        colonist.target_position = pos
