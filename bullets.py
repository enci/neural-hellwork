import pygame
from pygame.math import Vector2
from globals import Globals
from entity import Entity, EntityTag
from antialiased_draw import draw_antialiased_circle

class Bullet(Entity):
    """Base bullet class for enemy bullets"""
    def __init__(self, entity_manager, position, velocity, radius=12, color=(255, 51, 0)):
        super().__init__(entity_manager, position=position, tag=EntityTag.ENEMY_BULLET)
        self.velocity = velocity
        self.radius = radius  # Scaled up for native resolution
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
        
        # Draw with anti-aliasing
        draw_antialiased_circle(surface, self.color, 
                               (screen_pos.x, screen_pos.y), 
                               self.radius)

class PlayerBullet(Entity):
    """Player bullet class"""
    def __init__(self, entity_manager, position):
        super().__init__(entity_manager, position=position, tag=EntityTag.PLAYER_BULLET)
        self.velocity = Vector2(0, -Globals.bullet_speed)  # Upward movement
        self.radius = 16  # Scaled up for native resolution
        self.color = (221, 151, 21)
        
    def update(self):
        """Update bullet position"""
        self.position += self.velocity
        
    def draw(self, surface, camera_offset=None):
        """Draw the bullet with camera offset"""
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # Draw with anti-aliasing
        draw_antialiased_circle(surface, self.color, 
                               (screen_pos.x, screen_pos.y), 
                               self.radius)