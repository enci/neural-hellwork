import pygame
import math
import random
from vec2 import vec2
from globals import Globals

class Enemy:
    def __init__(self):
        self.radius = 8  # Scaled down for 180x240 resolution
        self.position = vec2(90, 30)  # Top center of 180x240 screen
        self.color = (255, 255, 255)  # White
        self.health = 100
        self.max_health = 100
        self.speed = Globals.enemy_speed
        
        # Pattern system
        from talakat import PATTERNS
        self.pattern_index = random.randint(0, len(PATTERNS) - 1)
        self.pattern_switch_timer = 300  # 5 seconds at 60 FPS
        
    def update(self):
        """Update enemy position and state"""
        # Simple movement - side to side
        self.position.x += math.sin(pygame.time.get_ticks() / 1000) * self.speed
        
        # Keep within bounds (180x240 resolution)
        self.position.x = max(self.radius, min(self.position.x, 180 - self.radius))
        
        # Update pattern switch timer
        self.pattern_switch_timer -= 1
        if self.pattern_switch_timer <= 0:
            # Change to a new random pattern
            from talakat import PATTERNS
            old_pattern_index = self.pattern_index
            while self.pattern_index == old_pattern_index:
                self.pattern_index = random.randint(0, len(PATTERNS) - 1)
            self.pattern_switch_timer = 300  # Reset timer
            return True  # Signal that pattern changed
        return False  # No pattern change
        
    def draw(self, surface):
        """Draw the enemy"""
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius)
        
        # Health bar (scaled for 180x240)
        bar_width = 25
        bar_height = 2
        fill_width = (self.health / self.max_health) * bar_width
        
        bar_x = self.position.x - bar_width // 2
        bar_y = self.position.y + self.radius + 5
        
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
        
        # Pattern switch timer indicator
        pattern_switch_percentage = self.pattern_switch_timer / 300
        indicator_width = 15
        indicator_height = 1
        indicator_x = self.position.x - indicator_width // 2
        indicator_y = self.position.y + self.radius + 10
        
        pygame.draw.rect(surface, (255, 255, 255), (indicator_x, indicator_y, indicator_width, indicator_height), 1)
        pygame.draw.rect(surface, (255, 255, 0), (indicator_x, indicator_y, indicator_width * pattern_switch_percentage, indicator_height))
        
    def hit(self):
        """Handle enemy being hit"""
        self.health -= 10
        if self.health <= 0:
            return True
        return False
    
    def get_center(self):
        """Get the center position for bullet spawning"""
        return self.position