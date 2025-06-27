import pygame
from pygame.math import Vector2
from globals import Globals
from entity import Entity, EntityTag

class Player(Entity):
    def __init__(self, entity_manager):
        super().__init__(entity_manager, position=Vector2(0, 80), tag=EntityTag.PLAYER)  # Center-bottom
        self.radius = 5  # Scaled down for 180x240 resolution
        self.color = (255, 255, 255)  # White
        self.speed = Globals.player_speed
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        
        # Shooting system
        self.shoot_cooldown = 0
        
        # Gamepad support
        self.gamepad = None
        self._init_gamepad()
        
    def _init_gamepad(self):
        """Initialize gamepad if available"""
        # Initialize joystick subsystem if not already initialized
        if not pygame.get_init() or not pygame.joystick.get_init():
            pygame.joystick.init()
            
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
    
    def _get_gamepad_input(self):
        """Get current gamepad input state"""
        if not self.gamepad:
            return {}
            
        gamepad_input = {}
        
        # Left stick for movement
        gamepad_input['left_stick_x'] = self.gamepad.get_axis(0)
        gamepad_input['left_stick_y'] = self.gamepad.get_axis(1)
        
        # Buttons for shooting (A button or right trigger)
        try:
            gamepad_input['shoot'] = (self.gamepad.get_button(0) or  # A button
                                    self.gamepad.get_axis(5) > 0.5)  # Right trigger
        except pygame.error:
            # Handle cases where controller doesn't have all expected inputs
            gamepad_input['shoot'] = False
            
        return gamepad_input
        
    def update(self):
        """Update player position and state"""
        
        # Get current input state
        keys = pygame.key.get_pressed()
        gamepad_input = self._get_gamepad_input()
        
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
        movement = Vector2(move_x, move_y) * self.speed
        self.position += movement
            
        # Keep player within bounds (centered coordinate system)
        # Screen is 180x240, so bounds are -90 to +90 horizontally, -120 to +120 vertically
        self.position.x = max(-90 + self.radius, min(self.position.x, 90 - self.radius))
        self.position.y = max(-120 + self.radius, min(self.position.y, 120 - self.radius))
        
        # Handle shooting
        self._handle_shooting(keys, gamepad_input)
        
        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
    def draw(self, surface, camera_offset=None):
        """Draw the player with camera offset"""
        # Blinking effect when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
            return
        
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # For now, draw as a circle - will be replaced with sprite later
        pygame.draw.circle(surface, self.color, 
                         (int(screen_pos.x), int(screen_pos.y)), 
                         self.radius)
        
    def hit(self):
        """Handle player being hit"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 90  # 1.5 seconds at 60 FPS
            
            # Reset position when hit (center-bottom)
            self.position = Vector2(0, 80)
    
    def get_center(self):
        """Get the center position for bullet spawning"""
        return self.position
    
    def _handle_shooting(self, keys, gamepad_input):
        """Handle player shooting logic"""
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Check for shooting input
        shoot_pressed = (keys[pygame.K_SPACE] or 
                        gamepad_input.get('shoot', False))
        
        # Create bullet if shooting and cooldown is ready
        if shoot_pressed and self.shoot_cooldown <= 0:
            from bullets import PlayerBullet
            bullet_pos = Vector2(self.position.x, 
                               self.position.y - self.radius)
            
            # Create bullet and add directly to entity manager
            entity_manager = self.get_entity_manager()
            if entity_manager:  # Check in case weak reference was garbage collected
                bullet = PlayerBullet(entity_manager, bullet_pos)
                entity_manager.add_entity(bullet)
                self.shoot_cooldown = 10