import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
import weakref

class EntityTag:
    """Entity tag constants"""
    PLAYER = 1
    ENEMY = 2
    PLAYER_BULLET = 3
    ENEMY_BULLET = 4

class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, entity_manager, position=None, tag=EntityTag.PLAYER):
        self.position = position if position else Vector2(0, 0)
        self.tag = tag  # Integer identifier (use EntityTag constants)
        self.active = True  # Whether the entity should be updated/drawn
        self.radius = 1  # Default collision radius
        self.color = (255, 255, 255)  # Default white color
        # Required reference to entity manager (weak reference to avoid circular dependencies)
        self._entity_manager_ref = weakref.ref(entity_manager)
        
    @abstractmethod
    def update(self):
        """Update the entity's state. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def draw(self, surface, camera_offset=None):
        """Draw the entity. Must be implemented by subclasses."""
        pass
    
    def get_entity_manager(self):
        """Get the entity manager"""
        return self._entity_manager_ref()  # Returns None if manager was garbage collected
    
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
    
    def is_offscreen(self, bounds_left=None, bounds_right=None, bounds_top=None, bounds_bottom=None):
        """Check if entity is outside the given bounds (defaults to world bounds)"""
        from globals import Globals
        
        if bounds_left is None: bounds_left = Globals.world_left
        if bounds_right is None: bounds_right = Globals.world_right  
        if bounds_top is None: bounds_top = Globals.world_top
        if bounds_bottom is None: bounds_bottom = Globals.world_bottom
        
        return (self.position.x < bounds_left - self.radius or 
                self.position.x > bounds_right + self.radius or
                self.position.y < bounds_top - self.radius or 
                self.position.y > bounds_bottom + self.radius)
    
    def __str__(self):
        return f"{self.tag} at ({self.position.x:.1f}, {self.position.y:.1f})"
