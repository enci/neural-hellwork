import pygame
from vec2 import vec2
from globals import Globals

class Bullet:
    """Base bullet class for enemy bullets"""
    def __init__(self, position, velocity, radius, color=(255, 255, 255)):
        self.position = position
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
        
    def is_offscreen(self):
        """Check if bullet is offscreen (180x240 resolution)"""
        return (self.position.x < -self.radius or self.position.x > 180 + self.radius or
                self.position.y < -self.radius or self.position.y > 240 + self.radius)
                
    def collides_with(self, other):
        """Check collision with another circular object"""
        distance = ((self.position.x - other.position.x) ** 2 + 
                   (self.position.y - other.position.y) ** 2) ** 0.5
        return distance < (self.radius + other.radius)

class PlayerBullet:
    """Player bullet class"""
    def __init__(self, position):
        self.position = position
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
        
    def is_offscreen(self):
        """Check if bullet is offscreen (upward movement)"""
        return self.position.y < -self.radius
        
    def collides_with(self, other):
        """Check collision with another circular object"""
        distance = ((self.position.x - other.position.x) ** 2 + 
                   (self.position.y - other.position.y) ** 2) ** 0.5
        return distance < (self.radius + other.radius)