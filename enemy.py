import pygame
from pygame.math import Vector2
import math
import random
from globals import Globals
from entity import Entity, EntityTag
from bullets import Bullet  # Enemy bullets
from tools import seconds_to_frames

class Enemy(Entity):
    def __init__(self, entity_manager):
        # Random starting X position above screen
        start_x = random.uniform(-60, 60)  # Don't start too close to edges
        super().__init__(entity_manager, position=Vector2(start_x, -150), tag=EntityTag.ENEMY)  # Start above screen
        self.radius = 8  # Scaled down for 180x240 resolution
        self.color = (255, 255, 255)  # White
        self.health = 100
        self.max_health = 100
        self.speed = Globals.enemy_speed
        
        # Movement state
        self.target_y = -90  # Target position (center-top of visible area)
        self.is_entering = True  # Whether enemy is still entering the screen
        self.enter_speed = 1.0  # Speed of vertical entrance movement
        
        # Invincibility system for newly spawned enemies
        self.invincible = True
        self.invincible_timer = seconds_to_frames(1.0)  # 1 second of invincibility
        
        # Bullet spawning system
        self.shoot_timer = 0
        self.new_bullets = []  # List to hold bullets created this frame
        
    def update(self):
        """Update enemy position and state"""
        self.new_bullets = []  # Clear bullets from previous frame
        
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Handle entrance movement
        if self.is_entering:
            # Move down towards target position
            self.position.y += self.enter_speed
            if self.position.y >= self.target_y:
                self.position.y = self.target_y
                self.is_entering = False
        else:
            # Normal side-to-side movement once in position
            self.position.x += math.sin(pygame.time.get_ticks() / 1000) * self.speed
        
        # Keep within bounds (centered coordinate system)
        # Screen is 180 wide, so bounds are -90 to +90
        self.position.x = max(-90 + self.radius, min(self.position.x, 90 - self.radius))
        
        # Handle bullet spawning (only when in position and not invincible)
        if not self.is_entering and not self.invincible:
            self._handle_bullet_spawning()
        
    def draw(self, surface, camera_offset=None):
        """Draw the enemy with camera offset"""
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # Flashing effect when invincible
        if self.invincible and self.invincible_timer % seconds_to_frames(0.167) < seconds_to_frames(0.083):  # Flash every 0.167s, visible for 0.083s
            # Don't draw on some frames to create flashing effect
            return
        
        # For now, draw as a circle - will be replaced with sprite later
        color = self.color
        if self.invincible:
            # Slightly dim the enemy when invincible
            color = (200, 200, 200)
        elif self.is_entering:
            # Different color when entering (yellow tint)
            color = (255, 255, 200)
            
        pygame.draw.circle(surface, color, 
                         (int(screen_pos.x), int(screen_pos.y)), 
                         self.radius)
        
        # Health bar (scaled for 180x240)
        bar_width = 25
        bar_height = 2
        fill_width = (self.health / self.max_health) * bar_width
        
        bar_x = screen_pos.x - bar_width // 2
        bar_y = screen_pos.y + self.radius + 5
        
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
        
    def hit(self):
        """Handle enemy being hit"""
        if self.invincible or self.is_entering:
            return False
            
        self.health -= 10
        if self.health <= 0:
            self.deactivate()
            return True
        return False
    
    def is_offscreen(self, bounds_left=-90, bounds_right=90, bounds_top=-120, bounds_bottom=120):
        return False
    
    def _handle_bullet_spawning(self):
        """Handle enemy bullet spawning"""
        self.shoot_timer += 1
        if self.shoot_timer >= seconds_to_frames(0.75):  # Shoot every 0.75 seconds (lower frequency for better playability)
            self.shoot_timer = 0
            
            # Generate bullets using simple pattern for now
            pattern = self._get_current_pattern()
            self._generate_bullets_from_pattern(pattern)

    
    def _get_current_pattern(self):
        """Get current bullet pattern - simplified to return default pattern"""
        # For now, just return a simple default pattern
        # This replaces the complex PATTERNS system
        return "default"
    
    def _generate_bullets_from_pattern(self, pattern):
        """Generate bullets from pattern - 5-bullet downward spread"""
        if pattern == "default":
            bullet_count = 5
            spread_angle = 60  # degrees total spread
            base_speed = 1.5   # slower speed for better playability
            
            # Calculate starting angle (90 degrees is straight down in screen coordinates)
            center_angle = 90  # Straight down
            start_angle = center_angle - spread_angle / 2
            
            # Get entity manager
            entity_manager = self.get_entity_manager()
            if not entity_manager:
                return
            
            # Create bullets in a spread pattern
            for i in range(bullet_count):
                if bullet_count > 1:
                    # Calculate angle for this bullet
                    angle_step = spread_angle / (bullet_count - 1)
                    current_angle = start_angle + (i * angle_step)
                else:
                    current_angle = center_angle
                
                # Convert angle to radians and calculate velocity
                # In screen coordinates, positive Y is downward
                angle_rad = math.radians(current_angle)
                velocity_x = math.cos(angle_rad) * base_speed
                velocity_y = math.sin(angle_rad) * base_speed
                
                # Create bullet position slightly offset from enemy center
                bullet_pos = Vector2(self.position.x, self.position.y + self.radius)
                bullet_velocity = Vector2(velocity_x, velocity_y)
                
                # Create bullet and add to entity manager
                bullet = Bullet(entity_manager, bullet_pos, bullet_velocity, radius=2)
                entity_manager.add_entity(bullet)
            