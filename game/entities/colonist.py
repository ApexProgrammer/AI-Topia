import pygame
import random
import math
from ..ai.neural_network import ColonistBrain, INPUT_SIZE
from ..config import (COLONIST_SPEED, WORKING_AGE, RETIREMENT_AGE, 
                     REPRODUCTION_AGE_MIN, REPRODUCTION_AGE_MAX, 
                     BUILDING_TYPES, TILE_SIZE, MOVEMENT_SPEED,
                     MARRIAGE_CHANCE, ANIMATION_SPEED, WALK_FRAMES, 
                     RESOURCE_CONSUMPTION_RATE, JOB_SALARIES, MINIMUM_WAGE,
                     REPRODUCTION_BASE_CHANCE, FAMILY_REPRODUCTION_BONUS,
                     REPRODUCTION_COOLDOWN, CRITICAL_POSITION_BONUS,
                     CRITICAL_POSITION_WAGE_BONUS, SKILL_GAIN_RATE,
                     EDUCATION_SKILL_BONUS)
from .building import Building

class Colonist:
    # Demographic tracking - keep track of age groups for population visualization
    AGE_GROUPS = {
        "child": (0, 18),
        "young_adult": (18, 30),
        "adult": (30, 50),
        "middle_aged": (50, 65),
        "senior": (65, 100)
    }
    
    # Satisfaction thresholds for visual indicators
    SATISFACTION_LEVELS = {
        "very_low": 0.2,
        "low": 0.4,
        "medium": 0.6,
        "high": 0.8,
        "very_high": 1.0
    }
    
    # Optimization - cached property to avoid recalculating
    PERFORMANCE_UPDATE_INTERVAL = 5  # Only update non-critical attributes every X frames
    
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
        self.job_satisfaction = 1.0  # Added job satisfaction tracking
        
        # Family and reproduction tracking
        self.reproduction_cooldown = 0
        self.is_critical_position = False  # Flag for critical position
        self.education_level = random.randint(1, 5)  # Education level (1-5)
        self.skills = {
            'farming': random.randint(20, 50),
            'mining': random.randint(20, 50),
            'crafting': random.randint(20, 50),
            'construction': random.randint(20, 50),
            'education': random.randint(20, 50),
            'leadership': random.randint(20, 50),
        }
        
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
        
        # Leadership and skills - removed construction_skill
        self.leadership = random.randint(0, 100)
        self.business_skill = random.randint(0, 100)
        
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
        self.role = None  # leader, worker, etc.
        
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

        # Movement and pathfinding attributes
        self.target_position = None
        self.current_grid_x = x // TILE_SIZE
        self.current_grid_y = y // TILE_SIZE
        self.interpolation_progress = 1.0
        self.start_pos = (x, y)
        self.prev_pos = (x, y)
        self.next_pos = (x, y)
        self.animation_timer = 0
        self.direction = 'right'
        self.is_walking = False
        self.movement_cooldown = 0
        self.last_move_time = 0
        self.current_path = []  # Store path to target
        self.path_index = 0     # Current position in path
        self.last_target = None # Remember last valid target
        
        # Performance optimization
        self.update_counter = 0  # Counter for less frequent updates
        self.cached_age_group = self.get_age_group()  # Cache age group
        
        # Enhanced worker satisfaction tracking
        self.satisfaction_history = [1.0] * 10  # Track satisfaction over time
        self.satisfaction_factors = {  # Detailed breakdown of satisfaction factors
            'pay': 1.0,
            'environment': 1.0,
            'job_match': 1.0,
            'social': 1.0,
            'workload': 1.0
        }
        
        # Accessibility options
        self.high_contrast_enabled = False  # Default to standard mode
        self.text_scale = 1.0  # Default text scale

    def update(self, speed_multiplier=1.0):
        # Store previous position for interpolation
        self.prev_pos = (self.x, self.y)
        
        # Performance optimization - count frames for less frequent updates
        self.update_counter = (self.update_counter + 1) % self.PERFORMANCE_UPDATE_INTERVAL
        
        # Critical updates every frame
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 0.01 * speed_multiplier
        
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
        
        # Update animation timer for smoother transitions
        if self.is_walking:
            self.animation_timer += ANIMATION_SPEED * speed_multiplier
            if self.animation_timer >= 1.0:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % WALK_FRAMES
        
        # Less frequent updates for performance optimization
        if self.update_counter == 0:
            # Update relationships and check age group changes
            self.update_relationships()
            
            # Check for reproduction with family house bonus
            if self.check_reproduction_conditions():
                self.attempt_reproduction()
            
            # Update skills through work experience
            if self.job:
                self.improve_skills()
            
            # Update demographic data when age group changes
            old_age_group = self.cached_age_group
            new_age_group = self.get_age_group()
            if old_age_group != new_age_group:
                self.cached_age_group = new_age_group
                if hasattr(self.world, 'update_demographics'):
                    self.world.update_demographics(old_age_group, new_age_group)
                    
            # Update detailed satisfaction metrics
            self.update_detailed_satisfaction()
        
        # Always update basic needs and happiness each frame
        self.update_basic_needs(speed_multiplier)
        self.update_happiness()
        self.age += 0.0005 * speed_multiplier
        
    def get_age_group(self):
        """Get the demographic age group for this colonist"""
        for group, (min_age, max_age) in self.AGE_GROUPS.items():
            if min_age <= self.age < max_age:
                return group
        return "senior"  # Default to senior for anyone over the top age

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
            self.update_job_satisfaction()  # Update job satisfaction
            self.happiness += 0.1 * self.job_satisfaction  # Job satisfaction affects happiness
        if self.home:
            self.happiness += 0.2
        if self.money > 1000:
            self.happiness += 0.1
        elif self.money < 100:
            self.happiness -= 0.2
            
        # Cap happiness
        self.happiness = max(0, min(100, self.happiness))
        
        # Update satisfaction history
        self.satisfaction_history.append(self.job_satisfaction)
        if len(self.satisfaction_history) > 10:  # Keep last 10 values
            self.satisfaction_history.pop(0)

    def update_detailed_satisfaction(self):
        """Update detailed satisfaction factors for visualization"""
        if not self.job:
            # Reset all factors for unemployed colonists
            for factor in self.satisfaction_factors:
                self.satisfaction_factors[factor] = 0.0
            return
            
        # Pay satisfaction
        base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
        actual_salary = getattr(self.job, 'salary', base_salary)
        self.satisfaction_factors['pay'] = min(1.0, actual_salary / (base_salary * 1.5))
        
        # Environment satisfaction - workspace efficiency and conditions
        if hasattr(self.job, 'building'):
            building = self.job.building
            # Calculate worker density and facility quality
            total_workers = len([j for j in building.jobs if j.employee])
            ideal_workers = building.max_jobs
            
            if ideal_workers > 0:
                # Balance between understaffed/overstaffed
                worker_ratio = total_workers / ideal_workers
                if worker_ratio <= 1.0:
                    # Understaffed - more work per person
                    self.satisfaction_factors['workload'] = min(1.0, 0.5 + worker_ratio * 0.5)
                else:
                    # Overstaffed - less work per person
                    self.satisfaction_factors['workload'] = max(0.2, 1.5 - worker_ratio * 0.5)
                    
            # Environmental factors based on building type
            if building.happiness_bonus > 0:
                self.satisfaction_factors['environment'] = min(1.0, 0.5 + (building.happiness_bonus / 20))
            else:
                self.satisfaction_factors['environment'] = 0.5
        else:
            self.satisfaction_factors['environment'] = 0.5
            self.satisfaction_factors['workload'] = 0.5
            
        # Job match based on skills and traits
        if hasattr(self.job, 'building'):
            building_type = self.job.building.building_type
            match_skill = None
            match_trait = None
            
            if building_type == 'farm':
                match_skill = 'farming'
                match_trait = 'work_ethic'
            elif building_type in ['woodcutter', 'quarry', 'mine']:
                match_skill = 'mining'
                match_trait = 'ambition'
            elif building_type == 'workshop':
                match_skill = 'crafting'
                match_trait = 'creativity'
            elif building_type in ['teacher', 'university']:
                match_skill = 'education'
                match_trait = 'intelligence'
            elif building_type in ['government']:
                match_skill = 'leadership'
                match_trait = 'leadership'
                
            if match_skill and match_trait:
                skill_level = self.skills.get(match_skill, 0) / 100
                trait_level = self.traits.get(match_trait, 0) / 100
                self.satisfaction_factors['job_match'] = (skill_level * 0.6) + (trait_level * 0.4)
            else:
                self.satisfaction_factors['job_match'] = 0.5
        else:
            self.satisfaction_factors['job_match'] = 0.5
            
        # Social satisfaction based on coworkers
        if hasattr(self.job, 'building') and hasattr(self.job.building, 'jobs'):
            coworkers = [j.employee for j in self.job.building.jobs if j.employee and j.employee != self]
            
            # Check relationships with coworkers
            if coworkers:
                relationship_sum = 0
                for coworker in coworkers:
                    if coworker in self.relationships:
                        relationship_sum += max(-1, min(1, self.relationships[coworker] / 100))
                    else:
                        relationship_sum += 0  # Neutral relationship
                
                avg_relationship = relationship_sum / len(coworkers) if coworkers else 0
                self.satisfaction_factors['social'] = (avg_relationship + 1) / 2  # Convert -1,1 to 0,1
            else:
                self.satisfaction_factors['social'] = 0.5  # Neutral if no coworkers
        else:
            self.satisfaction_factors['social'] = 0.5

    def update_job_satisfaction(self):
        """Calculate job satisfaction based on various factors"""
        if not self.job:
            self.job_satisfaction = 0.0
            return

        # Base satisfaction from pay
        base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
        pay_satisfaction = min(1.0, self.job.salary / base_salary)

        # Trait match satisfaction
        trait_match = 1.0
        if hasattr(self.job, 'building'):
            building_type = self.job.building.building_type
            if building_type == 'farm':
                trait_match = 0.5 + (self.traits['work_ethic'] / 200)
            elif building_type in ['woodcutter', 'quarry', 'mine']:
                trait_match = 0.5 + (self.traits['ambition'] / 200)
            elif building_type == 'workshop':
                trait_match = 0.5 + (self.traits['creativity'] / 200)
            elif building_type in ['teacher', 'government']:
                trait_match = 0.5 + (self.traits['intelligence'] / 200)

        # Workplace conditions
        workplace_satisfaction = 1.0
        if hasattr(self.job, 'building'):
            # Check building efficiency
            building = self.job.building
            workers = len([j for j in building.jobs if j.employee])
            if building.max_jobs > 0:
                workplace_satisfaction = 0.5 + (workers / building.max_jobs) * 0.5

        # Calculate final satisfaction
        self.job_satisfaction = (pay_satisfaction * 0.4 + 
                               trait_match * 0.4 + 
                               workplace_satisfaction * 0.2)
        
        # Cap satisfaction
        self.job_satisfaction = max(0.0, min(1.0, self.job_satisfaction))
        
    def get_satisfaction_level(self):
        """Return the satisfaction level category for visualization"""
        for level, threshold in sorted(self.SATISFACTION_LEVELS.items(), key=lambda x: x[1]):
            if self.job_satisfaction <= threshold:
                return level
        return "very_high"  # Default if all thresholds passed

    def get_satisfaction_color(self):
        """Get color for satisfaction visualization"""
        level = self.get_satisfaction_level()
        if level == "very_low":
            return (255, 0, 0)  # Red
        elif level == "low":
            return (255, 128, 0)  # Orange
        elif level == "medium":
            return (255, 255, 0)  # Yellow
        elif level == "high":
            return (128, 255, 0)  # Light green
        else:  # very_high
            return (0, 255, 0)  # Green

    def seek_job(self):
        """Find and move to an available job with balanced distribution"""
        if not self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
            # Get all buildings that can have jobs
            work_buildings = [b for b in self.world.buildings 
                            if b.max_jobs > 0 and len([j for j in b.jobs if not j.employee]) > 0]
            
            if work_buildings:
                # Group buildings by type
                building_types = {}
                for building in work_buildings:
                    if building.building_type not in building_types:
                        building_types[building.building_type] = []
                    building_types[building.building_type].append(building)
                
                # Calculate worker distribution for each building type
                type_distribution = {}
                for building_type in building_types:
                    total_jobs = sum(b.max_jobs for b in self.world.buildings if b.building_type == building_type)
                    filled_jobs = sum(len([j for j in b.jobs if j.employee]) for b in self.world.buildings if b.building_type == building_type)
                    if total_jobs > 0:
                        type_distribution[building_type] = filled_jobs / total_jobs
                
                # Find building type with lowest worker percentage
                target_type = min(type_distribution.items(), key=lambda x: x[1])[0]
                
                # Find closest building of target type
                closest_building = None
                min_distance = float('inf')
                
                for building in building_types.get(target_type, []):
                    dist = ((self.x - building.x)**2 + (self.y - building.y)**2)**0.5
                    if dist < min_distance:
                        min_distance = dist
                        closest_building = building
                
                if closest_building:
                    # Take the first available job
                    for job in closest_building.jobs:
                        if not job.employee:
                            self.job = job
                            job.employee = self
                            self.current_task = f"working at {closest_building.building_type}"
                            self.target_position = (closest_building.x, closest_building.y)
                            return True
        
        return False

    def move_to_job(self, job):
        """Move to and take a job with improved pathfinding"""
        if not job:
            return False
            
        job_grid_x, job_grid_y = self.world.get_grid_position(job.x, job.y)
        
        # Find best adjacent position to job
        best_pos = None
        shortest_path = None
        
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            check_x = job_grid_x + dx
            check_y = job_grid_y + dy
            
            if (0 <= check_x < self.world.current_size and 
                0 <= check_y < self.world.current_size):
                
                # Check if position is walkable
                occupants = self.world.get_grid_occupants(check_x, check_y)
                if not any(isinstance(occupant, Building) for occupant in occupants):
                    test_pos = self.world.get_pixel_position(check_x, check_y)
                    if self.set_target_position(test_pos):
                        path_len = len(self.current_path)
                        if shortest_path is None or path_len < shortest_path:
                            shortest_path = path_len
                            best_pos = test_pos
                            
        if best_pos:
            self.target_position = best_pos
            self.job = job
            job.employee = self
            
            # Check if this is a critical position job
            if hasattr(job, 'is_critical') and job.is_critical:
                self.is_critical_position = True
            
            self.happiness += 10
            return True
            
        return False

    def move_towards_target(self):
        """Move towards target position with improved pathfinding"""
        if not self.target_position:
            if random.random() < 0.005:
                self.random_movement()
            return

        # Handle interpolation between grid positions
        if self.interpolation_progress < 1.0:
            # Simple linear interpolation at constant speed
            self.interpolation_progress = min(1.0, self.interpolation_progress + MOVEMENT_SPEED)
            
            # Update position with linear interpolation
            self.x = self.start_pos[0] + (self.next_pos[0] - self.start_pos[0]) * self.interpolation_progress
            self.y = self.start_pos[1] + (self.next_pos[1] - self.start_pos[1]) * self.interpolation_progress
            
            # Update animation state continuously
            self.is_walking = True
            self.animation_timer = (self.animation_timer + ANIMATION_SPEED) % 1.0
            return

        # Check if we need a new path
        if not self.current_path:
            # Try to set target again or clear it if invalid
            if not self.set_target_position(self.target_position):
                self.target_position = None
                self.is_walking = False
                return

        # Get next path position
        if self.path_index < len(self.current_path):
            next_grid_x, next_grid_y = self.current_path[self.path_index]
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)

            # Update direction based on movement
            dx = next_grid_x - current_grid_x
            dy = next_grid_y - current_grid_y
            
            if dx != 0 or dy != 0:
                # Remove from current grid
                self.world.remove_from_grid(self, current_grid_x, current_grid_y)

                # Update direction based on primary movement axis
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'

                # Store positions for interpolation
                self.start_pos = (self.x, self.y)
                new_pos = self.world.get_pixel_position(next_grid_x, next_grid_y)
                self.next_pos = new_pos
                self.interpolation_progress = 0.0
                
                # Add to new grid position
                self.world.add_to_grid(self, next_grid_x, next_grid_y)
                self.is_walking = True
                self.path_index += 1
            else:
                # Reached target grid position
                self.path_index += 1
        else:
            # Reached end of path
            self.target_position = None
            self.current_path = []
            self.path_index = 0
            self.is_walking = False

    def random_movement(self):
        """Generate random movement within the grid"""
        if not self.target_position:
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            
            # Try each direction in random order
            directions = [(0,1), (1,0), (0,-1), (-1,0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_grid_x = current_grid_x + dx
                new_grid_y = current_grid_y + dy
                
                if (0 <= new_grid_x < self.world.current_size and 
                    0 <= new_grid_y < self.world.current_size):
                    
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(new_grid_x, new_grid_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        target_pos = self.world.get_pixel_position(new_grid_x, new_grid_y)
                        if self.set_target_position(target_pos):
                            break

    def seek_home(self):
        """Find and move to an available home with improved pathfinding"""
        available_homes = self.world.get_available_homes()
        if not available_homes:
            return False
            
        # Find closest available home with valid path
        best_home = None
        shortest_path = None
        best_pos = None
        
        for home in available_homes:
            home_grid_x, home_grid_y = self.world.get_grid_position(home.x, home.y)
            
            # Check adjacent positions
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                check_x = home_grid_x + dx
                check_y = home_grid_y + dy
                
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        test_pos = self.world.get_pixel_position(check_x, check_y)
                        if self.set_target_position(test_pos):
                            path_len = len(self.current_path)
                            if shortest_path is None or path_len < shortest_path:
                                shortest_path = path_len
                                best_pos = test_pos
                                best_home = home
                                
        if best_pos and best_home:
            self.target_position = best_pos
            self.home = best_home
            best_home.current_occupants += 1
            return True
            
        return False

    def seek_social_interaction(self):
        """Move towards other colonists with improved pathfinding"""
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        range_tiles = 5
        
        # Find nearby colonists and sort by distance
        nearby_colonists = []
        for dx in range(-range_tiles, range_tiles + 1):
            for dy in range(-range_tiles, range_tiles + 1):
                check_x = current_grid_x + dx
                check_y = current_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    colonists = [o for o in occupants 
                               if isinstance(o, Colonist) and o != self]
                    for colonist in colonists:
                        dist = abs(dx) + abs(dy)  # Manhattan distance
                        nearby_colonists.append((dist, colonist))
        
        # Sort by distance and try each colonist until we find a valid path
        if nearby_colonists:
            nearby_colonists.sort(key=lambda x: x[0])
            for _, target in nearby_colonists:
                target_grid_x, target_grid_y = self.world.get_grid_position(target.x, target.y)
                
                # Try positions near target in order of proximity
                for dx, dy in [(0,0), (0,1), (1,0), (0,-1), (-1,0)]:
                    check_x = target_grid_x + dx
                    check_y = target_grid_y + dy
                    if (0 <= check_x < self.world.current_size and 
                        0 <= check_y < self.world.current_size):
                        # Check if position is walkable
                        occupants = self.world.get_grid_occupants(check_x, check_y)
                        if not any(isinstance(occupant, Building) for occupant in occupants):
                            test_pos = self.world.get_pixel_position(check_x, check_y)
                            if self.set_target_position(test_pos):
                                return True
            
        return False

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
        """Render colonist with walking animation and status indicators"""
        # Calculate screen position
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        size = int(10 * zoom)  # Base size
        
        # Use high contrast colors if accessibility option is enabled
        if self.high_contrast_enabled:
            body_color = (255, 255, 100) if self.gender == 'F' else (100, 100, 255)
        else:
            body_color = (255, 200, 200) if self.gender == 'F' else (200, 200, 255)
        
        # Critical position highlights
        if self.is_critical_position:
            # Draw halo for critical position workers
            pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y), size + 2)
        
        # Draw job satisfaction indicator under colonist if employed
        if self.job:
            satisfaction_color = self.get_satisfaction_color()
            indicator_size = max(2, int(3 * zoom))
            pygame.draw.circle(screen, satisfaction_color, 
                             (screen_x, screen_y + size + indicator_size), 
                             indicator_size)
        
        # Draw age group indicators for demographic visualization
        age_group = self.get_age_group()
        age_indicator_y = screen_y - size - 5 * zoom
        
        if age_group == "child":
            age_color = (102, 255, 255)  # Light blue for children
        elif age_group == "young_adult":
            age_color = (0, 204, 102)    # Green for young adults
        elif age_group == "adult":
            age_color = (51, 102, 255)   # Blue for adults
        elif age_group == "middle_aged":
            age_color = (153, 153, 255)  # Purple for middle-aged
        else:  # senior
            age_color = (204, 204, 204)  # Gray for seniors
            
        # Draw small age indicator above colonist
        pygame.draw.circle(screen, age_color, 
                         (screen_x, int(age_indicator_y)), 
                         max(1, int(2 * zoom)))
        
        # Draw main body
        pygame.draw.circle(screen, body_color, (screen_x, screen_y), size)
        
        # Enhanced walking animation with consistent leg length across all directions
        if self.is_walking:
            # Calculate leg movement using sine wave
            leg_phase = self.animation_timer * math.pi * 2
            leg_length = 6 * zoom  # Standard leg length
            step_offset = abs(math.sin(leg_phase)) * 3 * zoom  # Reduced offset for more natural look
            
            # Base positions for legs
            base_left = screen_x - 3 * zoom
            base_right = screen_x + 3 * zoom
            base_y = screen_y + size
            
            # Draw legs based on direction
            if self.direction == 'right':
                # Right movement - legs swing forward/back
                leg_y = base_y + leg_length
                pygame.draw.line(screen, body_color,
                               (base_left, base_y),
                               (base_left - step_offset, leg_y),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, body_color,
                               (base_right, base_y),
                               (base_right + step_offset, leg_y),
                               max(1, int(2 * zoom)))
            elif self.direction == 'left':
                # Left movement - legs swing forward/back (mirrored)
                leg_y = base_y + leg_length
                pygame.draw.line(screen, body_color,
                               (base_left, base_y),
                               (base_left + step_offset, leg_y),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, body_color,
                               (base_right, base_y),
                               (base_right - step_offset, leg_y),
                               max(1, int(2 * zoom)))
            elif self.direction == 'up':
                # Up movement - legs move side to side
                pygame.draw.line(screen, body_color,
                               (base_left - step_offset, base_y),
                               (base_left - step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, body_color,
                               (base_right + step_offset, base_y),
                               (base_right + step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
            else:  # down
                # Down movement - legs move side to side
                pygame.draw.line(screen, body_color,
                               (base_left + step_offset, base_y),
                               (base_left + step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, body_color,
                               (base_right - step_offset, base_y),
                               (base_right - step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
        
        # Draw current activity indicator
        if self.current_task:
            # Use high contrast colors for accessibility if enabled
            if self.high_contrast_enabled:
                indicator_colors = {
                    'working': (255, 255, 0),      # Bright yellow
                    'building': (255, 100, 0),     # Bright orange
                    'shopping': (0, 255, 255),     # Bright cyan
                    'socializing': (255, 100, 255), # Bright pink
                    'studying': (100, 100, 255),    # Bright blue
                }
            else:
                indicator_colors = {
                    'working': (255, 255, 0),
                    'building': (255, 128, 0),
                    'shopping': (0, 255, 255),
                    'socializing': (255, 192, 203),
                    'studying': (100, 100, 255),
                }
            
            indicator_color = indicator_colors.get(self.current_task, (255, 255, 255))
            pygame.draw.circle(screen, indicator_color,
                             (screen_x, screen_y - size - 3 * zoom),
                             max(2, int(3 * zoom)))
        
        # Draw relationship indicators
        if self.spouse:
            # Draw heart for married colonists
            pygame.draw.circle(screen, (255, 0, 0),
                             (screen_x, screen_y - size - 8 * zoom),
                             max(2, int(3 * zoom)))
            
        # Draw education level indicator (small dots)
        if self.education_level > 1:
            for i in range(int(self.education_level)):
                pygame.draw.circle(screen, (100, 100, 255),
                                 (screen_x - size + i*4*zoom, screen_y - size - 12*zoom),
                                 max(1, int(1.5 * zoom)))

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
        """Execute the action chosen by the AI - with new education action"""
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
        elif action == 7:  # Education - new action
            self.current_task = "studying"
            self.attend_education()

    def gather_resources(self):
        """Enhanced resource gathering with building integration"""
        if not self.job:
            return
            
        # Calculate base efficiency from traits and energy with improved weights
        efficiency = (
            (self.traits['work_ethic'] / 100) * 0.5 +    # Increased work ethic importance
            (self.energy / 100) * 0.2 +                  # Energy level contribution
            (self.happiness / 100) * 0.2 +               # Happiness bonus
            (self.traits['intelligence'] / 100) * 0.1    # Skill bonus
        )
        
        # Apply skill bonus based on job type
        if hasattr(self.job, 'building'):
            building_type = self.job.building.building_type
            if building_type == 'farm':
                efficiency *= (1 + self.skills['farming'] / 200)  # Up to 50% boost
            elif building_type in ['woodcutter', 'quarry', 'mine']:
                efficiency *= (1 + self.skills['mining'] / 200)
            elif building_type == 'workshop':
                efficiency *= (1 + self.skills['crafting'] / 200)
        
        # Critical position bonus
        if self.is_critical_position:
            efficiency *= (1 + CRITICAL_POSITION_BONUS)
        
        # Building-type specific bonuses to encourage variety
        if hasattr(self.job, 'building'):
            building_type = self.job.building.building_type
            # Enhanced bonuses for non-farm buildings to counter farm bias
            if building_type == 'woodcutter':
                efficiency *= 1.25  # Significant boost for woodcutters
            elif building_type == 'quarry':
                efficiency *= 1.2   # Good boost for quarry
            elif building_type == 'mine':
                efficiency *= 1.25  # Significant boost for mines
            elif building_type == 'workshop':
                efficiency *= 1.3   # Best boost for workshops
            elif building_type == 'farm':
                efficiency *= 1.0   # No additional boost for farms
        
        # Enhanced proximity bonus for resource gathering
        if hasattr(self.job, 'building'):
            distance = ((self.x - self.job.building.x)**2 + 
                       (self.y - self.job.building.y)**2)**0.5
            if distance < 50:  # Close to workplace
                efficiency *= 1.3  # Increased proximity bonus
                self.current_task = 'working'  # Set current task for visual indicator
            elif distance < 100:  # Medium distance
                efficiency *= 1.1
                self.current_task = 'working'
        
        # Earn money for work with efficiency bonus
        building_type = self.job.building.building_type if hasattr(self.job, 'building') else "unknown"
        base_salary = JOB_SALARIES.get(building_type, MINIMUM_WAGE) 
        
        # Apply critical position wage bonus
        wage_multiplier = CRITICAL_POSITION_WAGE_BONUS if self.is_critical_position else 1.0
        
        earned = (base_salary / 30) * efficiency * wage_multiplier
        self.money += earned
        self.inventory['money'] = self.money
        
        # Small happiness boost from successful gathering
        if random.random() < 0.15:  # 15% chance for happiness boost
            self.happiness = min(100, self.happiness + 1)

        # Directly trigger building production if close to workplace
        if hasattr(self.job, 'building') and distance < 100:
            # Boost building production when colonist is at work
            building = self.job.building
            if building.is_complete and hasattr(building, 'produces'):
                # Process resource chain dependencies if applicable
                if hasattr(building, 'inputs') and building.inputs:
                    self.process_resource_chain(building)
                
                # Transfer building resources to colonist's personal inventory (small amount)
                if building.produces and building.inventory.get(building.produces, 0) > 0:
                    if building.produces not in self.inventory:
                        self.inventory[building.produces] = 0
                    
                    harvest_amount = efficiency * 0.2  # Small personal harvest
                    if building.inventory.get(building.produces, 0) >= harvest_amount:
                        building.inventory[building.produces] -= harvest_amount
                        self.inventory[building.produces] += harvest_amount
                    
                    # Bonus production chance
                    bonus_chance = 0.05
                    if building.building_type != 'farm':
                        bonus_chance = 0.08
                    
                    if random.random() < bonus_chance * efficiency:
                        produced = building.production_rate * 0.5
                        if building.produces in self.world.colony_inventory:
                            self.world.colony_inventory[building.produces] += produced

    # New methods for family, skills, and resource chains
    def check_reproduction_conditions(self):
        """Check if reproduction is possible"""
        if not self.spouse:
            return False
            
        if self.reproduction_cooldown > 0:
            return False
            
        # Check age requirements
        if (REPRODUCTION_AGE_MIN <= self.age <= REPRODUCTION_AGE_MAX and
            REPRODUCTION_AGE_MIN <= self.spouse.age <= REPRODUCTION_AGE_MAX):
                
            # Calculate base chance
            chance = REPRODUCTION_BASE_CHANCE
            
            # Apply family house bonus if applicable
            if self.home and self.home.building_type == 'family_house':
                if hasattr(self.home, 'reproduction_bonus'):
                    chance += self.home.reproduction_bonus
                else:
                    chance += FAMILY_REPRODUCTION_BONUS  # Default bonus
            
            # Adjust based on colony health
            if len(self.world.colonists) > 50:  # Large colony
                chance *= 0.8  # Reduce chance in large colonies
                
            # Roll for reproduction
            return random.random() < chance
        
        return False

    def attempt_reproduction(self):
        """Create a new colonist through reproduction"""
        if not self.spouse or not self.world:
            return
            
        # Create new colonist near the parents
        x, y = self.x, self.y
        child = Colonist(x, y, self.world)
        
        # Genetics - inherit traits from parents
        for trait in child.traits:
            # 50% chance to inherit from each parent
            parent = self if random.random() < 0.5 else self.spouse
            
            # Add some genetic variation
            variation = random.randint(-10, 10)
            child.traits[trait] = max(20, min(100, parent.traits[trait] + variation))
        
        # Set child's age to 0
        child.age = 0
        
        # Add to parents' children lists
        self.children.append(child)
        self.spouse.children.append(child)
        
        # Add to world
        self.world.colonists.append(child)
        
        # Set reproduction cooldown
        self.reproduction_cooldown = REPRODUCTION_COOLDOWN
        self.spouse.reproduction_cooldown = REPRODUCTION_COOLDOWN
        
        # Happiness boost for new parents
        self.happiness = min(100, self.happiness + 15)
        self.spouse.happiness = min(100, self.spouse.happiness + 15)

    def improve_skills(self):
        """Improve skills through work experience"""
        if not self.job or not hasattr(self.job, 'building'):
            return
            
        building_type = self.job.building.building_type
        
        # Determine which skill to improve
        skill_to_improve = None
        if building_type == 'farm':
            skill_to_improve = 'farming'
        elif building_type in ['woodcutter', 'quarry', 'mine']:
            skill_to_improve = 'mining'
        elif building_type == 'workshop':
            skill_to_improve = 'crafting'
        elif building_type == 'government':
            skill_to_improve = 'leadership'
        
        # Improve the relevant skill
        if skill_to_improve and skill_to_improve in self.skills:
            # Base skill improvement
            improvement = SKILL_GAIN_RATE
            
            # Education bonus
            improvement *= (1 + (self.education_level - 1) * 0.2)  # 0-80% bonus based on education
            
            # Intelligence bonus
            improvement *= (1 + (self.traits['intelligence'] - 50) / 100)
            
            # Apply improvement
            self.skills[skill_to_improve] = min(100, self.skills[skill_to_improve] + improvement)

    def process_resource_chain(self, building):
        """Process resource chain dependencies for production"""
        if not hasattr(building, 'inputs') or not building.inputs:
            return
            
        # Check if required input resources are available
        can_produce = True
        consumption_amount = {}
        
        for input_resource, amount_needed in building.inputs.items():
            # Check colony inventory
            available = self.world.colony_inventory.get(input_resource, 0)
            if available < amount_needed:
                can_produce = False
                break
                
            consumption_amount[input_resource] = min(amount_needed, available)
        
        if can_produce:
            # Consume input resources
            for resource, amount in consumption_amount.items():
                self.world.colony_inventory[resource] -= amount
            
            # Apply production bonus for resource chains
            bonus_production = building.production_rate * 0.5
            
            # Add to building inventory
            if building.produces not in building.inventory:
                building.inventory[building.produces] = 0
            building.inventory[building.produces] += bonus_production
            
            # Log processing
            if hasattr(self.world, 'debug_log'):
                self.world.debug_log(f"Resource chain processed: {consumption_amount} → {bonus_production} {building.produces}")

    def attend_education(self):
        """Attend education to improve skills and education level"""
        # Find education building
        education_buildings = [b for b in self.world.buildings 
                             if b.building_type in ['school', 'university', 'library']]
        
        if not education_buildings:
            return False
        
        # Find closest education building
        closest = None
        min_dist = float('inf')
        
        for building in education_buildings:
            dist = ((self.x - building.x)**2 + (self.y - building.y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest = building
        
        if not closest:
            return False
        
        # Move towards education building
        self.target_position = (closest.x, closest.y)
        
        # If close enough, gain education benefits
        if min_dist < 50:
            # Improve education level slowly
            if random.random() < 0.05:  # 5% chance per update
                self.education_level = min(5, self.education_level + 0.1)
            
            # Improve a random skill
            skill_keys = list(self.skills.keys())
            skill_to_improve = random.choice(skill_keys)
            self.skills[skill_to_improve] = min(100, 
                                              self.skills[skill_to_improve] + EDUCATION_SKILL_BONUS)
            
            # Happiness boost from learning
            self.happiness = min(100, self.happiness + 0.2)
            
            return True
        
        return False

    def visit_nearest_shop(self):
        """Find and move to the nearest shop with pathfinding"""
        shops = [b for b in self.world.buildings if b.building_type == 'shop']
        if not shops:
            return False
        
        # Sort shops by distance and try each until we find a valid path
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        shop_distances = []
        
        for shop in shops:
            shop_grid_x, shop_grid_y = self.world.get_grid_position(shop.x, shop.y)
            dist = abs(shop_grid_x - current_grid_x) + abs(shop_grid_y - current_grid_y)
            shop_distances.append((dist, shop))
        
        shop_distances.sort(key=lambda x: x[0])
        
        for _, shop in shop_distances:
            shop_grid_x, shop_grid_y = self.world.get_grid_position(shop.x, shop.y)
            
            # Try positions adjacent to shop
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                check_x = shop_grid_x + dx
                check_y = shop_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        test_pos = self.world.get_pixel_position(check_x, check_y)
                        if self.set_target_position(test_pos):
                            return True
        
        return False

    def set_target_position(self, target_pos):
        """Set a new target position with validation"""
        if not target_pos or not self.world:
            return False
            
        # Convert target to grid coordinates
        target_grid_x, target_grid_y = self.world.get_grid_position(target_pos[0], target_pos[1])
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        
        # Validate target is within bounds
        if not (0 <= target_grid_x < self.world.current_size and 
                0 <= target_grid_y < self.world.current_size):
            return False
            
        # Check if target is occupied by a building
        occupants = self.world.get_grid_occupants(target_grid_x, target_grid_y)
        if any(isinstance(occupant, Building) for occupant in occupants):
            # Find nearest accessible position
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
                check_x = target_grid_x + dx
                check_y = target_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    check_occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in check_occupants):
                        target_grid_x, target_grid_y = check_x, check_y
                        break
            else:
                return False  # No accessible position found
        
        # Calculate path to target
        self.current_path = self.find_path(current_grid_x, current_grid_y, 
                                         target_grid_x, target_grid_y)
        if not self.current_path:
            return False
            
        self.target_position = target_pos
        self.last_target = target_pos
        self.path_index = 0
        return True

    def find_path(self, start_x, start_y, target_x, target_y):
        """Simple A* pathfinding"""
        if not (0 <= target_x < self.world.current_size and 
               0 <= target_y < self.world.current_size):
            return []
            
        # Manhattan distance heuristic
        def heuristic(x, y):
            return abs(target_x - x) + abs(target_y - y)
        
        # Initialize search with a more robust open set structure
        open_set = {(start_x, start_y)}  # Use set for O(1) operations
        open_set_f = {(start_x, start_y): heuristic(start_x, start_y)}  # Track f scores
        came_from = {}
        g_score = {(start_x, start_y): 0}
        
        while open_set:
            # Find node with minimum f_score
            current = min(open_set, key=lambda pos: open_set_f[pos])
            current_x, current_y = current
            
            if current_x == target_x and current_y == target_y:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append((start_x, start_y))
                path.reverse()
                return path
                
            # Remove current from open set
            open_set.remove(current)
            open_set_f.pop(current)
            
            # Check neighbors
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                next_x, next_y = current_x + dx, current_y + dy
                neighbor = (next_x, next_y)
                
                if not (0 <= next_x < self.world.current_size and 
                       0 <= next_y < self.world.current_size):
                    continue
                    
                # Check if neighbor is walkable
                occupants = self.world.get_grid_occupants(next_x, next_y)
                if any(isinstance(occupant, Building) for occupant in occupants):
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Found better path to neighbor
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(next_x, next_y)
                    open_set_f[neighbor] = f_score
                    open_set.add(neighbor)
        
        return []  # No path found
        
    # Accessibility methods
    def toggle_high_contrast(self):
        """Toggle high contrast mode for accessibility"""
        self.high_contrast_enabled = not self.high_contrast_enabled
        
    def set_text_scale(self, scale):
        """Set text size scaling for improved readability"""
        self.text_scale = max(0.8, min(1.5, scale))
