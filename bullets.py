import pygame
from vec2 import vec2
from globals import Globals
from entity import Entity, EntityTag

class Bullet(Entity):
    """Base bullet class for enemy bullets"""
    def __init__(self, position, velocity, radius, color=(255, 255, 255)):
        super().__init__(position=position, tag=EntityTag.ENEMY_BULLET)
        self.velocity = velocity
        self.radius = radius
        self.color = color
        
    def update(self):
        """Update bullet position"""
        self.position = self.position + self.velocity
        
    def draw(self, surface):
        """Draw the bullet"""
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.radius))

class PlayerBullet(Entity):
    """Player bullet class"""
    def __init__(self, position):
        super().__init__(position=position, tag=EntityTag.PLAYER_BULLET)
        self.velocity = vec2(0, -Globals.bullet_speed)  # Upward movement
        self.radius = 2  # Scaled down for 180x240 resolution
        self.color = (255, 255, 0)  # Yellow
        
    def update(self):
        """Update bullet position"""
        self.position = self.position + self.velocity
        
    def draw(self, surface):
        """Draw the bullet"""
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius)
        
    def is_offscreen(self, bounds_left=-90, bounds_right=90, bounds_top=-120, bounds_bottom=120):
        """Check if bullet is offscreen (upward movement)"""
        return self.position.y < bounds_top - self.radius