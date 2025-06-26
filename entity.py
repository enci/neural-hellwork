import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod

class EntityTag:
    """Entity tag constants"""
    PLAYER = 1
    ENEMY = 2
    PLAYER_BULLET = 3
    ENEMY_BULLET = 4

class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, position=None, tag=EntityTag.PLAYER):
        self.position = position if position else Vector2(0, 0)
        self.tag = tag  # Integer identifier (use EntityTag constants)
        self.active = True  # Whether the entity should be updated/drawn
        self.radius = 1  # Default collision radius
        self.color = (255, 255, 255)  # Default white color
        
    @abstractmethod
    def update(self, *args, **kwargs):
        """Update the entity's state. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def draw(self, surface, camera_offset=None):
        """Draw the entity. Must be implemented by subclasses."""
        pass
    
    def is_active(self):
        """Check if entity is active"""
        return self.active
    
    def deactivate(self):
        """Mark entity as inactive (for removal)"""
        self.active = False
    
    def get_center(self):
        """Get the center position of the entity"""
        return self.position
    
    def collides_with(self, other):
        """Check collision with another entity (circle-based)"""
        if not isinstance(other, Entity):
            return False
        
        distance = self.position.distance_to(other.position)
        return distance < (self.radius + other.radius)
    
    def is_offscreen(self, bounds_left=-90, bounds_right=90, bounds_top=-120, bounds_bottom=120):
        """Check if entity is outside the given bounds (default: centered coordinate system)"""
        return (self.position.x < bounds_left - self.radius or 
                self.position.x > bounds_right + self.radius or
                self.position.y < bounds_top - self.radius or 
                self.position.y > bounds_bottom + self.radius)
    
    def __str__(self):
        return f"{self.tag} at ({self.position.x:.1f}, {self.position.y:.1f})"
