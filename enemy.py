import pygame
from pygame.math import Vector2
import math
import random
from globals import Globals
from entity import Entity, EntityTag
from bullets import Bullet  # Enemy bullets
from tools import seconds_to_frames
from antialiased_draw import draw_antialiased_circle, draw_antialiased_rect
from shape_renderer import ShapeRenderer
from talakat import TalakatInterpreter
from bullet_patterns import get_pattern_for_level

class Enemy(Entity):
    def __init__(self, entity_manager):
        # Random starting X position above screen
        start_x = random.uniform(Globals.world_left + 90, Globals.world_right - 90)  # Don't start too close to edges
        super().__init__(entity_manager, position=Vector2(start_x, Globals.world_top - 90), tag=EntityTag.ENEMY)  # Start above screen
        entity_manager.add_entity(self)  # Add to entity manager
        self.radius = 24  # Scaled up for native resolution
        self.color = (255, 51, 0)
        self.health = 100
        self.max_health = 100
        self.speed = Globals.enemy_speed
        
        # Movement state
        self.target_y = Globals.world_top + 90  # Target position (center-top of visible area)
        self.is_entering = True  # Whether enemy is still entering the screen
        self.enter_speed = 3.0  # Speed of vertical entrance movement (scaled up)
        
        # Invincibility system for newly spawned enemies
        self.invincible = True
        self.invincible_timer = seconds_to_frames(1.0)  # 1 second of invincibility
        
        # Bullet spawning system with Talakat
        self.shoot_timer = 0
        self.talakat_interpreter = TalakatInterpreter()
        self.current_pattern = get_pattern_for_level(1)  # Start with level 1 pattern
        self.pattern_level = 1
        
    def update(self):
        """Update enemy position and state"""
        
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
        self.position.x = max(Globals.world_left + self.radius, min(self.position.x, Globals.world_right - self.radius))
        
        # Handle bullet spawning using Talakat (only when in position and not invincible)
        if not self.is_entering and not self.invincible:
            self._handle_talakat_bullet_spawning()
        
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
        
        # Determine color based on enemy state
        color = self.color
        if self.invincible:
            # Slightly dim the enemy when invincible
            color = (200, 200, 200)
        elif self.is_entering:
            # Different color when entering (yellow tint)
            color = (255, 255, 200)
        
        # Draw main enemy body with anti-aliasing
        draw_antialiased_circle(surface, color, 
                               (screen_pos.x, screen_pos.y), 
                               self.radius)
        
        # Arc health bar around the enemy (always visible)
        health_percentage = self.health / self.max_health
        
        # Health bar parameters
        arc_radius = self.radius + 8  # Distance from enemy center
        arc_thickness = 4             # Thickness of the arc
        
        # Full circle health bar
        start_angle = -math.pi / 2    # Start at top
        total_arc = 2 * math.pi       # Full circle (2π radians)
        health_arc = total_arc * health_percentage
        
        # Background arc (gray to show missing health) - always full circle
        ShapeRenderer.draw_arc(surface, (80, 80, 80), 
                             (screen_pos.x, screen_pos.y), 
                             arc_radius, start_angle, start_angle + total_arc, 
                             arc_thickness, antialiased=True)
        
        # Health arc (bright red for remaining health)
        if health_percentage > 0:
            ShapeRenderer.draw_arc(surface, (255, 51, 0), 
                                 (screen_pos.x, screen_pos.y), 
                                 arc_radius, start_angle, start_angle + health_arc, 
                                 arc_thickness, antialiased=True)
        
    def hit(self):
        """Handle enemy being hit"""
        if self.invincible or self.is_entering:
            return False
            
        self.health -= 10
        if self.health <= 0:
            self.deactivate()
            return True
        return False
    
    def is_offscreen(self, bounds_left=None, bounds_right=None, bounds_top=None, bounds_bottom=None):
        """Check if enemy is offscreen using Globals bounds"""
        if bounds_left is None: bounds_left = Globals.world_left
        if bounds_right is None: bounds_right = Globals.world_right  
        if bounds_top is None: bounds_top = Globals.world_top
        if bounds_bottom is None: bounds_bottom = Globals.world_bottom
        return False
    
    def _handle_talakat_bullet_spawning(self):
        """Handle enemy bullet spawning using Talakat patterns"""
        # Get entity manager
        entity_manager = self.get_entity_manager()
        if not entity_manager:
            return
        
        # Use Talakat interpreter to generate bullets
        new_bullets = self.talakat_interpreter.get_bullets(
            self.current_pattern, 
            self.position, 
            entity_manager
        )
        
        # Add all generated bullets to the entity manager
        for bullet in new_bullets:
            entity_manager.add_entity(bullet)
    
    def set_pattern_level(self, level: int):
        """Update the bullet pattern based on game level"""
        if level != self.pattern_level:
            self.pattern_level = level
            self.current_pattern = get_pattern_for_level(level)
            # Reset interpreter when changing patterns
            self.talakat_interpreter.reset()
    
    def reset_pattern(self):
        """Reset the Talakat interpreter (useful when enemy respawns)"""
        self.talakat_interpreter.reset()
            