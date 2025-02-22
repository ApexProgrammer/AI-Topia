import pygame
import random
import math
from ..ai.neural_network import ColonistBrain, INPUT_SIZE
from ..config import (COLONIST_SPEED, WORKING_AGE, RETIREMENT_AGE, 
                     REPRODUCTION_AGE_MIN, REPRODUCTION_AGE_MAX, 
                     BUILDING_TYPES, TILE_SIZE, MOVEMENT_SPEED,
                     MARRIAGE_CHANCE, ANIMATION_SPEED, WALK_FRAMES, 
                     RESOURCE_CONSUMPTION_RATE, JOB_SALARIES, MINIMUM_WAGE)
from .building import Building

class Colonist:
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.world = world
        self.brain = ColonistBrain()
        
        # Basic attributes
        self.age = random.randint(18, 50)
        self.gender = random.choice(['M', 'F'])
        self.health = 100
        self.energy = 100
        self.money = 1000
        self.happiness = 100
        
        # Visualization
        self.color = (255, 200, 200) if self.gender == 'F' else (200, 200, 255)
        self.size = 10
        
        # Animation state
        self.animation_frame = 0
        self.direction = 'right'  # right, left, up, down
        self.is_walking = False
        
        # Resources
        self.inventory = {
            'food': 0,
            'goods': 0,
            'money': self.money
        }
        
        # Leadership and skills
        self.leadership = random.randint(0, 100)
        self.construction_skill = random.randint(0, 100)
        self.business_skill = random.randint(0, 100)
        
        # Building projects
        self.current_project = None
        self.project_progress = 0
        
        # Personality traits
        self.traits = {
            'ambition': random.randint(20, 100),
            'sociability': random.randint(20, 100),
            'intelligence': random.randint(20, 100),
            'creativity': random.randint(20, 100),
            'work_ethic': random.randint(20, 100),
            'leadership': random.randint(20, 100)
        }
        
        # Status
        self.job = None
        self.home = None
        self.spouse = None
        self.children = []
        self.role = None  # leader, builder, worker, etc.
        
        # AI state
        self.current_task = None
        self.target_position = None
        self.path = []
        
        # Relationships
        self.relationships = {}
        self.friends = []
        self.enemies = []
        
        # Political views
        self.political_alignment = random.random()  # 0 = conservative, 1 = progressive
        self.voted_for = None

    def update(self, speed_multiplier=1.0):
        # Update relationships
        self.update_relationships()
        
        # Get AI decision focused on gathering and social needs
        state = self.get_state()
        action = self.brain.decide_action(state)
        
        # Execute action with personality influence
        self.execute_action(action)
        
        # Handle movement
        self.move_towards_target()
        
        # Update animation and basic needs
        if self.is_walking:
            self.animation_frame += ANIMATION_SPEED * speed_multiplier
            if self.animation_frame >= WALK_FRAMES:
                self.animation_frame = 0
        
        self.update_basic_needs(speed_multiplier)
        self.update_happiness()
        self.age += 0.0005 * speed_multiplier

    def update_basic_needs(self, speed_multiplier=1.0):
        """Update basic needs like energy, health, and resources"""
        # Energy consumption based on work ethic and activity
        base_energy_loss = RESOURCE_CONSUMPTION_RATE * (2 - self.traits['work_ethic']/100) * speed_multiplier
        if self.is_walking:
            base_energy_loss *= 1.5
        self.energy = max(0, min(100, self.energy - base_energy_loss))
        
        # Health regeneration when resting
        if self.energy > 50:
            self.health = min(100, self.health + (0.05 * speed_multiplier))
        elif self.energy < 20:
            self.health = max(0, self.health - (0.02 * speed_multiplier))
        
        # Food consumption and effects
        if self.inventory['food'] > 0:
            food_consumed = RESOURCE_CONSUMPTION_RATE * speed_multiplier
            self.inventory['food'] = max(0, self.inventory['food'] - food_consumed)
            self.health = min(100, self.health + (0.1 * speed_multiplier))
            self.energy = min(100, self.energy + (0.2 * speed_multiplier))
        else:
            self.health = max(0, self.health - (0.05 * speed_multiplier))
            self.energy = max(0, self.energy - (0.1 * speed_multiplier))
        
        # Work and earn money
        if self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
            # Calculate work efficiency
            efficiency = (1 + (self.traits['work_ethic'] - 50) / 100) * (self.energy / 100)
            
            # Get base salary for job type
            base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
            
            # Calculate daily earnings with bonuses
            earned = (base_salary / 30) * efficiency  # Daily wage
            if self.traits['intelligence'] > 70:
                earned *= 1.2  # Smart worker bonus
            if self.traits['creativity'] > 70:
                earned *= 1.1  # Creative worker bonus
                
            self.money += earned
            self.inventory['money'] = self.money
            
            # Produce resources if applicable
            if hasattr(self.job, 'produces'):
                production = self.job.production_rate * efficiency
                if self.job.produces in self.inventory:
                    self.inventory[self.job.produces] += production
                else:
                    self.inventory[self.job.produces] = production

    def update_happiness(self):
        """Update happiness based on various factors"""
        # Base happiness changes
        if self.health < 50:
            self.happiness -= 0.2
        elif self.health > 80:
            self.happiness += 0.1
            
        if self.energy < 30:
            self.happiness -= 0.2
        elif self.energy > 70:
            self.happiness += 0.1
            
        # Social factors
        if self.spouse:
            self.happiness += 0.2
        if len(self.children) > 0:
            self.happiness += 0.1 * len(self.children)
        if len(self.friends) > 0:
            self.happiness += 0.05 * len(self.friends)
            
        # Economic factors
        if self.job:
            self.happiness += 0.1
        if self.home:
            self.happiness += 0.2
        if self.money > 1000:
            self.happiness += 0.1
        elif self.money < 100:
            self.happiness -= 0.2
            
        # Cap happiness
        self.happiness = max(0, min(100, self.happiness))

    def seek_job(self):
        """Find and move to an available job"""
        if not self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
            available_jobs = self.world.get_available_jobs()
            if available_jobs:
                # Filter jobs by skills and traits
                suitable_jobs = []
                for job in available_jobs:
                    score = 0
                    if job.type == 'farmer':
                        score = self.traits['work_ethic']
                    elif job.type == 'factory_worker':
                        score = (self.traits['work_ethic'] + self.traits['intelligence']) / 2
                    elif job.type == 'shopkeeper':
                        score = (self.traits['sociability'] + self.traits['creativity']) / 2
                    elif job.type == 'banker':
                        score = self.traits['intelligence']
                    elif job.type == 'government_worker':
                        score = (self.traits['intelligence'] + self.traits['leadership']) / 2
                    
                    if score > 50:  # Only consider jobs they're good at
                        suitable_jobs.append((job, score))
                
                if suitable_jobs:
                    # Choose job weighted by suitability score
                    job, _ = max(suitable_jobs, key=lambda x: x[1])
                    self.move_to_job(job)

    def move_to_job(self, job):
        """Move to and take a job"""
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        job_grid_x, job_grid_y = self.world.get_grid_position(job.x, job.y)
        
        # Find walkable position near job
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            target_x = job_grid_x + dx
            target_y = job_grid_y + dy
            
            if (0 <= target_x < self.world.current_size and 
                0 <= target_y < self.world.current_size):
                
                # Remove from current position
                self.world.remove_from_grid(self, current_grid_x, current_grid_y)
                
                # Move to new position
                target_pos = self.world.get_pixel_position(target_x, target_y)
                self.target_position = target_pos
                
                # Add to new position
                self.world.add_to_grid(self, target_x, target_y)
                
                # Assign job
                self.job = job
                job.employee = self
                self.happiness += 10  # Happy to get a job
                break

    def move_towards_target(self):
        """Move towards target position with grid-based movement"""
        if not self.target_position and random.random() < 0.02:  # 2% chance to start random movement
            self.random_movement()
            
        if self.target_position:
            # Get current grid position
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            
            # Calculate target grid position
            target_x, target_y = self.target_position
            target_grid_x, target_grid_y = self.world.get_grid_position(target_x, target_y)
            
            # Calculate grid-based movement
            dx = target_grid_x - current_grid_x
            dy = target_grid_y - current_grid_y
            
            if dx != 0 or dy != 0:
                # Remove from current grid
                self.world.remove_from_grid(self, current_grid_x, current_grid_y)
                
                # Determine movement direction
                if abs(dx) > abs(dy):
                    # Move horizontally
                    move_x = 1 if dx > 0 else -1
                    new_grid_x = current_grid_x + move_x
                    new_grid_y = current_grid_y
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    # Move vertically
                    move_y = 1 if dy > 0 else -1
                    new_grid_x = current_grid_x
                    new_grid_y = current_grid_y + move_y
                    self.direction = 'down' if dy > 0 else 'up'
                
                # Check if new position is valid
                if (0 <= new_grid_x < self.world.current_size and 
                    0 <= new_grid_y < self.world.current_size):
                    
                    # Convert to pixel coordinates
                    new_pos = self.world.get_pixel_position(new_grid_x, new_grid_y)
                    self.x = new_pos[0]
                    self.y = new_pos[1]
                    
                    # Add to new grid position
                    self.world.add_to_grid(self, new_grid_x, new_grid_y)
                    self.is_walking = True
                    
                    # Update animation
                    self.animation_frame += ANIMATION_SPEED
                    if self.animation_frame >= WALK_FRAMES:
                        self.animation_frame = 0
                else:
                    # Invalid position, stop movement
                    self.target_position = None
                    self.is_walking = False
                    self.world.add_to_grid(self, current_grid_x, current_grid_y)
            else:
                # Reached target
                self.target_position = None
                self.is_walking = False

    def random_movement(self):
        """Generate random movement within the grid"""
        if not self.target_position:
            # Get current grid position
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            
            # Choose random direction
            directions = [(0,1), (1,0), (0,-1), (-1,0)]
            dx, dy = random.choice(directions)
            
            new_grid_x = current_grid_x + dx
            new_grid_y = current_grid_y + dy
            
            # Check if new position is valid
            if (0 <= new_grid_x < self.world.current_size and 
                0 <= new_grid_y < self.world.current_size):
                
                # Check if position is occupied by a building
                occupants = self.world.get_grid_occupants(new_grid_x, new_grid_y)
                if not any(isinstance(occupant, Building) for occupant in occupants):
                    # Convert to pixel coordinates
                    target_pos = self.world.get_pixel_position(new_grid_x, new_grid_y)
                    self.target_position = target_pos

    def seek_job(self):
        """Find and move to an available job"""
        available_jobs = self.world.get_available_jobs()
        if available_jobs:
            job = random.choice(available_jobs)
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            job_grid_x, job_grid_y = self.world.get_grid_position(job.x, job.y)
            
            # Find walkable position near job
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                target_x = job_grid_x + dx
                target_y = job_grid_y + dy
                
                if (0 <= target_x < self.world.current_size and 
                    0 <= target_y < self.world.current_size):
                    
                    # Remove from current position
                    self.world.remove_from_grid(self, current_grid_x, current_grid_y)
                    
                    # Move to new position
                    target_pos = self.world.get_pixel_position(target_x, target_y)
                    self.target_position = target_pos
                    
                    # Add to new position
                    self.world.add_to_grid(self, target_x, target_y)
                    
                    # Assign job
                    self.job = job
                    job.employee = self
                    break

    def seek_home(self):
        """Find and move to an available home"""
        available_homes = self.world.get_available_homes()
        if available_homes:
            home = random.choice(available_homes)
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            home_grid_x, home_grid_y = self.world.get_grid_position(home.x, home.y)
            
            # Find walkable position near home
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                target_x = home_grid_x + dx
                target_y = home_grid_y + dy
                
                if (0 <= target_x < self.world.current_size and 
                    0 <= target_y < self.world.current_size):
                    
                    # Remove from current position
                    self.world.remove_from_grid(self, current_grid_x, current_grid_y)
                    
                    # Move to new position
                    target_pos = self.world.get_pixel_position(target_x, target_y)
                    self.target_position = target_pos
                    
                    # Add to new position
                    self.world.add_to_grid(self, target_x, target_y)
                    
                    # Assign home
                    self.home = home
                    home.current_occupants += 1
                    break

    def seek_social_interaction(self):
        """Move towards other colonists"""
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        range_tiles = 5
        
        # Find nearby colonists
        nearby_colonists = []
        for dx in range(-range_tiles, range_tiles + 1):
            for dy in range(-range_tiles, range_tiles + 1):
                check_x = current_grid_x + dx
                check_y = current_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    nearby_colonists.extend([o for o in occupants 
                                          if isinstance(o, Colonist) and o != self])
        
        if nearby_colonists:
            target = random.choice(nearby_colonists)
            target_grid_x, target_grid_y = self.world.get_grid_position(target.x, target.y)
            
            # Find nearby empty tile
            for dx, dy in [(0,0), (0,1), (1,0), (0,-1), (-1,0)]:
                check_x = target_grid_x + dx
                check_y = target_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        self.target_position = self.world.get_pixel_position(check_x, check_y)
                        break

    def seek_partner(self):
        """Find and move towards a potential partner"""
        potential_partners = self.world.get_potential_partners(self)
        if potential_partners:
            target = random.choice(potential_partners)
            target_grid_x, target_grid_y = self.world.get_grid_position(target.x, target.y)
            
            # Find nearby empty tile
            for dx, dy in [(0,0), (0,1), (1,0), (0,-1), (-1,0)]:
                check_x = target_grid_x + dx
                check_y = target_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        self.target_position = self.world.get_pixel_position(check_x, check_y)
                        
                        # Attempt to form partnership with increased chance
                        if random.random() < MARRIAGE_CHANCE:
                            self.spouse = target
                            target.spouse = self
                            # Boost happiness for new couple
                            self.happiness += 20
                            target.happiness += 20
                        break

    def render(self, screen, camera_x=0, camera_y=0, zoom=1.0):
        """Render colonist with walking animation"""
        # Calculate screen position
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        size = int(10 * zoom)  # Base size
        
        # Draw body
        color = (255, 200, 200) if self.gender == 'F' else (200, 200, 255)
        pygame.draw.circle(screen, color, (screen_x, screen_y), size)
        
        # Draw walking animation
        if self.is_walking:
            leg_offset = abs(math.sin(self.animation_frame * math.pi)) * 3 * zoom
            if self.direction in ['left', 'right']:
                # Draw legs
                pygame.draw.line(screen, color,
                               (screen_x, screen_y + size),
                               (screen_x - leg_offset, screen_y + size + 5 * zoom), 
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (screen_x, screen_y + size),
                               (screen_x + leg_offset, screen_y + size + 5 * zoom),
                               max(1, int(2 * zoom)))
            else:
                # Draw legs for up/down movement
                pygame.draw.line(screen, color,
                               (screen_x - 2 * zoom, screen_y + size),
                               (screen_x - 2 * zoom, screen_y + size + leg_offset),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (screen_x + 2 * zoom, screen_y + size),
                               (screen_x + 2 * zoom, screen_y + size - leg_offset),
                               max(1, int(2 * zoom)))
        
        # Draw current activity indicator
        if self.current_task:
            indicator_color = {
                'working': (255, 255, 0),
                'building': (255, 128, 0),
                'shopping': (0, 255, 255),
                'socializing': (255, 192, 203)
            }.get(self.current_task, (255, 255, 255))
            pygame.draw.circle(screen, indicator_color,
                             (screen_x, screen_y - size - 3 * zoom),
                             max(2, int(3 * zoom)))
        
        # Draw relationship indicators
        if self.spouse:
            # Draw heart for married colonists
            pygame.draw.circle(screen, (255, 0, 0),
                             (screen_x, screen_y - size - 8 * zoom),
                             max(2, int(3 * zoom)))

    def get_state(self):
        """Get current state for AI input"""
        # Total 22 features as per INPUT_SIZE configuration
        basic_state = [
            self.x / self.world.width,  # Normalized position
            self.y / self.world.height,
            self.age / 100,  # Normalized age
            self.health / 100,
            self.energy / 100,
            self.money / 10000,  # Normalized money
            self.happiness / 100,
            1 if self.job else 0,
            1 if self.home else 0,
            1 if self.spouse else 0,
        ]
        
        # Add personality traits
        trait_state = [trait_value / 100 for trait_value in self.traits.values()]
        
        # Add social state
        social_state = [
            len(self.friends) / 10,  # Normalized number of friends
            len(self.enemies) / 10,  # Normalized number of enemies
            sum(self.relationships.values()) / (len(self.relationships) * 100) if self.relationships else 0,  # Average relationship strength
        ]
        
        # Add environmental state
        env_state = [
            len(self.world.get_available_jobs()) / 20,  # Normalized available jobs
            len(self.world.get_available_homes()) / 20,  # Normalized available homes
            self.world.treasury / 100000,  # Normalized treasury
        ]
        
        return basic_state + trait_state + social_state + env_state

    def update_relationships(self):
        """Update relationships with other colonists"""
        for other in self.world.colonists:
            if other != self:
                # Initialize relationship if not exists
                if other not in self.relationships:
                    compatibility = self.calculate_compatibility(other)
                    self.relationships[other] = compatibility
                
                # Update relationship based on proximity and interaction
                if ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5 < 50:  # If colonists are close
                    change = random.randint(-2, 2)
                    self.relationships[other] = max(-100, min(100, self.relationships[other] + change))
                    
                    # Update friends and enemies
                    if self.relationships[other] > 50 and other not in self.friends:
                        self.friends.append(other)
                    elif self.relationships[other] < -50 and other not in self.enemies:
                        self.enemies.append(other)

    def calculate_compatibility(self, other):
        """Calculate initial compatibility with another colonist"""
        trait_diff = sum(abs(self.traits[t] - other.traits[t]) for t in self.traits)
        base_compatibility = 100 - trait_diff/len(self.traits)
        return base_compatibility + random.randint(-20, 20)

    def execute_action(self, action):
        """Execute the action chosen by the AI - removed building decisions"""
        if action == 0:  # Find job/gather resources
            if not self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
                self.seek_job()
        elif action == 1:  # Find home
            if not self.home:
                self.seek_home()
        elif action == 2:  # Rest
            if self.home:
                self.target_position = (self.home.x, self.home.y)
                self.energy = min(100, self.energy + 10)
        elif action == 3:  # Work/Gather
            if self.job:
                self.target_position = (self.job.x, self.job.y)
                self.gather_resources()
        elif action == 4:  # Socialize
            self.seek_social_interaction()
        elif action == 5:  # Visit shop
            self.visit_nearest_shop()
        elif action == 6:  # Random movement
            self.random_movement()

    def gather_resources(self):
        """Enhanced resource gathering with efficiency bonuses"""
        if not self.job:
            return
            
        # Calculate base efficiency from traits and energy
        efficiency = (
            (self.traits['work_ethic'] / 100) * 0.4 +  # Work ethic contribution
            (self.energy / 100) * 0.3 +                # Energy level contribution
            (self.happiness / 100) * 0.2 +             # Happiness bonus
            (self.traits['intelligence'] / 100) * 0.1   # Skill bonus
        )
        
        # Job-specific trait bonuses
        if hasattr(self.job, 'type'):
            if self.job.type == 'farm_worker':
                efficiency *= 1 + (self.traits['work_ethic'] / 200)  # Up to 50% bonus
            elif self.job.type == 'mine_worker':
                efficiency *= 1 + (self.traits['intelligence'] / 200)
            elif self.job.type == 'woodcutter_worker':
                efficiency *= 1 + (self.traits['work_ethic'] / 150)
            elif self.job.type == 'workshop_worker':
                efficiency *= 1 + (self.traits['creativity'] / 150)
        
        # Proximity bonus for resource gathering
        if hasattr(self.job, 'building'):
            distance = ((self.x - self.job.building.x)**2 + 
                       (self.y - self.job.building.y)**2)**0.5
            if distance < 50:  # Close to workplace
                efficiency *= 1.2
        
        # Produce resources with calculated efficiency
        if hasattr(self.job, 'produces'):
            production = self.job.production_rate * efficiency
            # Add to world's shared inventory instead of personal inventory
            self.world.add_to_colony_inventory(self.job.produces, production)
            
            # Energy cost of gathering
            self.energy = max(0, self.energy - 0.1)
            
            # Small happiness boost from successful gathering
            if random.random() < 0.1:  # 10% chance per gather
                self.happiness = min(100, self.happiness + 1)
            
            # Earn money for work
            base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
            earned = (base_salary / 30) * efficiency  # Daily wage
            self.money += earned
            self.inventory['money'] = self.money

    def visit_nearest_shop(self):
        """Find and move to the nearest shop"""
        shops = [b for b in self.world.buildings if b.building_type == 'shop']
        if shops:
            # Find nearest shop
            nearest_shop = min(shops, key=lambda b: ((b.x - self.x)**2 + (b.y - self.y)**2)**0.5)
            self.target_position = (nearest_shop.x, nearest_shop.y)
