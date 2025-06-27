import pygame
from pygame.math import Vector2
from globals import Globals
from entity import Entity, EntityTag

class Bullet(Entity):
    """Base bullet class for enemy bullets"""
    def __init__(self, entity_manager, position, velocity, radius, color=(255, 255, 255)):
        super().__init__(entity_manager, position=position, tag=EntityTag.ENEMY_BULLET)
        self.velocity = velocity
        self.radius = radius
        self.color = color
        
    def update(self):
        """Update bullet position"""
        self.position += self.velocity
        
    def draw(self, surface, camera_offset=None):
        """Draw the bullet with camera offset"""
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(screen_pos.x), int(screen_pos.y)), 
                         int(self.radius))

class PlayerBullet(Entity):
    """Player bullet class"""
    def __init__(self, entity_manager, position):
        super().__init__(entity_manager, position=position, tag=EntityTag.PLAYER_BULLET)
        self.velocity = Vector2(0, -Globals.bullet_speed)  # Upward movement
        self.radius = 2  # Scaled down for 180x240 resolution
        self.color = (255, 255, 0)  # Yellow
        
    def update(self):
        """Update bullet position"""
        self.position += self.velocity
        
    def draw(self, surface, camera_offset=None):
        """Draw the bullet with camera offset"""
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(screen_pos.x), int(screen_pos.y)), 
                         self.radius)