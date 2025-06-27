import pygame
import math
from pygame.math import Vector2
from globals import Globals
from entity import Entity, EntityTag
from tools import seconds_to_frames
from antialiased_draw import draw_antialiased_circle
import math

class Player(Entity):
    def __init__(self, entity_manager):
        super().__init__(entity_manager, position=Vector2(0, Globals.world_bottom - 120), tag=EntityTag.PLAYER)  # Center-bottom
        self.radius = 15  # Scaled up for native resolution
        self.color = (221, 151, 21)
        self.speed = Globals.player_speed
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        
        # Shooting system
        self.shoot_cooldown = 0
        
        # Gamepad support
        self.gamepad = None
        self._init_gamepad()
        
        # Bot AI system
        self.bot_enabled = False  # Bot is enabled by default
        self.bot_cast_count = 12  # Number of directional casts
        self.bot_cast_width = 8   # Width of box cast
        self.bot_cast_length = 30  # Length of box cast
        self.bot_desired_direction = Vector2(0, 0)  # Current bot movement direction
        
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
        
        # Check for bot toggle (B key)
        if keys[pygame.K_b] and not hasattr(self, '_b_key_pressed'):
            self.bot_enabled = not self.bot_enabled
            self._b_key_pressed = True
            print(f"Bot {'enabled' if self.bot_enabled else 'disabled'}")
        elif not keys[pygame.K_b]:
            self._b_key_pressed = False
        
        # Update based on control mode
        if self.bot_enabled:
            self._update_bot()
        else:
            self._update_human(keys, gamepad_input)
        
        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
    def draw(self, surface, camera_offset=None):
        """Draw the player with camera offset"""
        # Blinking effect when invincible
        if self.invincible and self.invincible_timer % seconds_to_frames(0.167) < seconds_to_frames(0.083):  # Flash every 0.167s, visible for 0.083s
            return
        
        # Calculate screen position with camera offset
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        screen_pos = self.position + camera_offset
        
        # Choose color based on bot status
        color = self.color
        if self.bot_enabled:
            color = (100, 255, 100)  # Green tint when bot is active
        
        # Draw with anti-aliasing
        draw_antialiased_circle(surface, color, 
                               (screen_pos.x, screen_pos.y), 
                               self.radius)
        
    def hit(self):
        """Handle player being hit"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = seconds_to_frames(1.5)  # 1.5 seconds of invincibility
            
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
                self.shoot_cooldown = seconds_to_frames(0.167)  # ~0.167 seconds between shots
    
    def _update_human(self, keys, gamepad_input):
        """Update player with human input"""
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
            
        # Keep player within bounds
        self._clamp_to_bounds()
        
        # Handle shooting
        self._handle_shooting(keys, gamepad_input)
    
    def _update_bot(self):
        """Update player with bot AI"""
        # Get entity manager to access other entities
        entity_manager = self.get_entity_manager()
        if not entity_manager:
            return
        
        # Get all enemy bullets
        enemy_bullets = entity_manager.get_entities_by_tag(EntityTag.ENEMY_BULLET)
        enemies = entity_manager.get_entities_by_tag(EntityTag.ENEMY)
        
        # Perform directional box casts to find safe movement
        safe_direction = self._find_safe_direction(enemy_bullets, enemies)
        
        # Apply bot movement
        if safe_direction.length() > 0:
            movement = safe_direction.normalize() * self.speed
            self.position += movement
        
        # Keep player within bounds
        self._clamp_to_bounds()
        
        # Bot shooting - always shoot when not in cooldown
        self._bot_shooting()
    
    def _find_safe_direction(self, enemy_bullets, enemies):
        """Find safe direction using directional box casts"""
        best_direction = Vector2(0, 0)
        best_score = -1000
        
        # Test directions in a circle around the player
        for i in range(self.bot_cast_count):
            angle = (i * 360 / self.bot_cast_count)
            angle_rad = math.radians(angle)
            
            # Direction vector
            direction = Vector2(math.cos(angle_rad), math.sin(angle_rad))
            
            # Score this direction
            score = self._score_direction(direction, enemy_bullets, enemies)
            
            if score > best_score:
                best_score = score
                best_direction = direction
        
        # Try to move to center-bottom for good shooting position
        if best_score < 0:
            # Try to move to center-bottom for good shooting position
            target_pos = Vector2(0, Globals.world_bottom - 40)  # Center-bottom area
            to_target = target_pos - self.position
            if to_target.length() > 0:
                return to_target.normalize()
        
        return best_direction
    
    def _score_direction(self, direction, enemy_bullets, enemies):
        """Score a direction based on safety and tactical value"""
        # Cast position
        cast_end = self.position + direction * self.bot_cast_length
        
        # Safety score - negative points for bullets in path
        safety_score = 100
        
        # Check collision with enemy bullets
        for bullet in enemy_bullets:
            if self._box_intersects_bullet(self.position, cast_end, bullet):
                # Penalize based on bullet proximity and trajectory
                distance = (bullet.position - self.position).length()
                if distance < 20:
                    safety_score -= 50
                elif distance < 40:
                    safety_score -= 25
                else:
                    safety_score -= 10
        
        # Tactical score - prefer positions that allow good shooting
        tactical_score = 0
        
        # Prefer being in lower half of screen for shooting upward
        if cast_end.y > 0:
            tactical_score += 20
        
        # Prefer being somewhat centered horizontally
        center_distance = abs(cast_end.x)
        if center_distance < Globals.half_width // 3:  # Within 1/3 of screen width
            tactical_score += 10
        
        # Avoid screen edges
        margin = 10
        if (cast_end.x < Globals.world_left + margin or cast_end.x > Globals.world_right - margin or 
            cast_end.y < Globals.world_top + margin or cast_end.y > Globals.world_bottom - margin):
            safety_score -= 30
        
        return safety_score + tactical_score
    
    def _box_intersects_bullet(self, start_pos, end_pos, bullet):
        """Check if a box cast intersects with a bullet"""
        # Simple box intersection check
        # Get bullet future position based on its velocity
        bullet_future = bullet.position + bullet.velocity * 10  # Look ahead 10 frames
        
        # Check if bullet path intersects with our box cast
        cast_center = (start_pos + end_pos) * 0.5
        cast_half_width = self.bot_cast_width * 0.5
        cast_half_length = (end_pos - start_pos).length() * 0.5
        
        # Distance from bullet to cast center
        to_bullet = bullet.position - cast_center
        to_bullet_future = bullet_future - cast_center
        
        # Simple distance check (could be improved with proper box collision)
        min_dist = min(to_bullet.length(), to_bullet_future.length())
        return min_dist < (cast_half_width + bullet.radius)
    
    def _clamp_to_bounds(self):
        """Keep player within screen bounds"""
        self.position.x = max(Globals.world_left + self.radius, min(self.position.x, Globals.world_right - self.radius))
        self.position.y = max(Globals.world_top + self.radius, min(self.position.y, Globals.world_bottom - self.radius))
    
    def _bot_shooting(self):
        """Handle bot shooting logic"""
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Always shoot when cooldown is ready
        if self.shoot_cooldown <= 0:
            from bullets import PlayerBullet
            bullet_pos = Vector2(self.position.x, 
                               self.position.y - self.radius)
            
            # Create bullet and add directly to entity manager
            entity_manager = self.get_entity_manager()
            if entity_manager:
                bullet = PlayerBullet(entity_manager, bullet_pos)
                entity_manager.add_entity(bullet)
                self.shoot_cooldown = seconds_to_frames(0.167)  # ~0.167 seconds between shots