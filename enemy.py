import pygame
from pygame.math import Vector2
import math
import random
from globals import Globals
from entity import Entity, EntityTag

class Enemy(Entity):
    def __init__(self):
        # Random starting X position above screen
        start_x = random.uniform(-60, 60)  # Don't start too close to edges
        super().__init__(position=Vector2(start_x, -150), tag=EntityTag.ENEMY)  # Start above screen
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
        self.invincible_timer = 60  # 1 second of invincibility at 60 FPS
        
        # Pattern system
        from talakat import PATTERNS
        self.pattern_index = random.randint(0, len(PATTERNS) - 1)
        self.pattern_switch_timer = 300  # 5 seconds at 60 FPS
        self.pattern_just_changed = False  # Track if pattern changed this frame
        
    def update(self):
        """Update enemy position and state"""
        self.pattern_just_changed = False  # Reset flag
        
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
        
        # Update pattern switch timer (only when not entering)
        if not self.is_entering:
            self.pattern_switch_timer -= 1
            if self.pattern_switch_timer <= 0:
                # Change to a new random pattern
                from talakat import PATTERNS
                old_pattern_index = self.pattern_index
                while self.pattern_index == old_pattern_index:
                    self.pattern_index = random.randint(0, len(PATTERNS) - 1)
                self.pattern_switch_timer = 300  # Reset timer
                self.pattern_just_changed = True
    
    def did_pattern_change(self):
        """Check if pattern changed this frame"""
        return self.pattern_just_changed
        
    def draw(self, surface, camera_offset=None):
        """Draw the enemy with camera offset"""
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # Flashing effect when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
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
        
        # Pattern switch timer indicator
        pattern_switch_percentage = self.pattern_switch_timer / 300
        indicator_width = 15
        indicator_height = 1
        indicator_x = screen_pos.x - indicator_width // 2
        indicator_y = screen_pos.y + self.radius + 10
        
        pygame.draw.rect(surface, (255, 255, 255), (indicator_x, indicator_y, indicator_width, indicator_height), 1)
        pygame.draw.rect(surface, (255, 255, 0), (indicator_x, indicator_y, indicator_width * pattern_switch_percentage, indicator_height))
        
    def hit(self):
        """Handle enemy being hit"""
        # Don't take damage if invincible or still entering
        if self.invincible or self.is_entering:
            return False
            
        self.health -= 10
        if self.health <= 0:
            return True
        return False
    
    def get_center(self):
        """Get the center position for bullet spawning"""
        return self.position