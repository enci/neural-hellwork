import pygame
from vec2 import vec2
from globals import Globals
from entity import Entity, EntityTag

class Player(Entity):
    def __init__(self):
        super().__init__(position=vec2(90, 200), tag=EntityTag.PLAYER)
        self.radius = 5  # Scaled down for 180x240 resolution
        self.color = (255, 255, 255)  # White
        self.speed = Globals.player_speed
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        
    def update(self, keys, gamepad_input=None):
        """Update player position and state"""
        # Player movement - keyboard
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1
            
        # Gamepad movement
        if gamepad_input:
            # Left stick for movement
            stick_x = gamepad_input.get('left_stick_x', 0)
            stick_y = gamepad_input.get('left_stick_y', 0)
            
            # Apply deadzone
            deadzone = 0.15
            if abs(stick_x) > deadzone:
                move_x += stick_x
            if abs(stick_y) > deadzone:
                move_y += stick_y
        
        # Apply movement
        self.position.x += move_x * self.speed
        self.position.y += move_y * self.speed
            
        # Keep player within bounds (180x240 resolution)
        self.position.x = max(self.radius, min(self.position.x, 180 - self.radius))
        self.position.y = max(self.radius, min(self.position.y, 240 - self.radius))
        
        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
    def draw(self, surface):
        """Draw the player"""
        # Blinking effect when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
            return
        
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius)
        
    def hit(self):
        """Handle player being hit"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 90  # 1.5 seconds at 60 FPS
            
            # Reset position when hit
            self.position = vec2(90, 200)
            return True
        return False
    
    def get_center(self):
        """Get the center position for bullet spawning"""
        return self.position