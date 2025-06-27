from typing import Any
import pygame
from pygame.math import Vector2
import numpy as np
from player import Player
from enemy import Enemy
from globals import Globals
from entity import EntityTag
from entity_manager import EntityManager
from antialiased_draw import draw_antialiased_circle
from font_manager import font_manager
import gymnasium as gym
from typing import Optional

# Game State Enum
class GameState:
    START = 0
    RUNNING = 1
    DANGER = 2 # when a new enemy is spawned
    PAUSED = 3
    GAME_OVER = 4

class Game(gym.Env):
    def __init__(self):
        # Initialize pygame and joystick early
        pygame.init()
        pygame.joystick.init()
        
        self._reset()
        
        # Set up the environment
        super().__init__()

        self.action_space = gym.spaces.Discrete(10)
        self.observation_space = gym.spaces.Dict({
            'total_damage_dealt': gym.spaces.Box(low=0, high=float('inf'), shape=(1,), dtype=np.float32),
            'player_hp': gym.spaces.Discrete(4)  # 0 to 3 lives
        })


    def _get_obs(self):
        """Get the current observation of the game state"""
        obs = {
            'total_damage_dealt': self.damage_dealt,
            'player_hp': self.player.lives
        }
        return obs

    def _get_info(self):
        return {}

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None): # type: ignore
        super().reset(seed=seed, options=options)
        self._reset()

        observation = self._get_obs()
        info = self._get_info()
        return observation, info
        

    def _reset(self):
        """Reset the game state"""
        # Initialize entity manager
        self.entity_manager = EntityManager()
        
        # Create entities with entity manager reference
        self.player = Player(self.entity_manager)
        self.enemy = Enemy(self.entity_manager)  # Back to single enemy
        
        # Add entities to manager
        self.entity_manager.add_entity(self.player)
        self.entity_manager.add_entity(self.enemy)
        
        # Game state
        self.score = 0
        self.level = 1
        self.game_over = False
        self.win = False
        self.spawn_enemy_timer = 0
        self.damage_dealt = 0
        self.damage_recieved = 0

    def step(self, action: Any):
        """Perform a game step based on the action"""
        if self.game_over:
            return self._get_obs(), 0, True, False, self._get_info()
        
        # Update game state
        self.update()
        
        # Calculate reward
        reward = 0
        if self.win:
            reward = 100
        elif self.game_over:
            reward = -100
        
        observation = self._get_obs()
        terminated = self.game_over
        truncated = False  # No truncation logic in this game
        info = self._get_info()

        return observation, reward, terminated, truncated, info
        
    def update(self):
        """Update game state"""

        if self.game_over:
            return
        
        # Update entity manager (handles all active entities)
        self.entity_manager.update_all()


        # Player bullets vs enemy
        player_bullets = self.entity_manager.get_entities_by_tag(EntityTag.PLAYER_BULLET)
        self.test_collisions(player_bullets, self.enemy, self.handle_bullet_enemy_collision)

        # Enemy bullets vs player
        enemy_bullets = self.entity_manager.get_entities_by_tag(EntityTag.ENEMY_BULLET)        
        self.test_collisions(enemy_bullets, self.player, self.handle_bullet_player_collision)

        active_entities = self.entity_manager.get_active_entities()
        for entity in active_entities:
            if entity.is_offscreen():
                entity.deactivate()
                        
        # Check win condition
        if self.level > 10:
            self.win = True
            self.game_over = True

        # Check game over condition separately
        if self.player.lives <= 0:
            self.game_over = True

         # Clean up inactive entities
        self.entity_manager.cleanup_inactive()
    
    def draw(self, screen):
        """Draw everything to the screen"""
        # Clear with background color
        screen.fill(Globals.bg_color)

        # Set up camera offset for centered coordinates (0,0 at center)
        camera_offset = Vector2(Globals.half_width, Globals.half_height)

        # draw a red circle at the center (0,0 in our coordinate system) with anti-aliasing
        center_screen_pos = Vector2(0, 0) + camera_offset
        draw_antialiased_circle(screen, (255, 0, 0), (center_screen_pos.x, center_screen_pos.y), 10)
        
        # Draw all entities using entity manager with camera offset
        self.entity_manager.draw_all(screen, camera_offset)
            
        # Draw UI
        self._draw_ui(screen)
        
    def _draw_ui(self, surface):
        """Draw UI elements using custom Pulsewidth font"""
        # Use normal font sizes - FontManager will scale them appropriately for Pulsewidth font
        large_font_size = 42   # For game over/win text
        medium_font_size = 28  # For main UI elements  
        small_font_size = 22   # For smaller text
        
        # Score
        score_text = font_manager.render_text(f"Score: {self.score}", medium_font_size, (255, 255, 255))
        surface.blit(score_text, (15, 15))
        
        # Level
        level_text = font_manager.render_text(f"Level: {self.level}", medium_font_size, (255, 255, 255))
        surface.blit(level_text, (15, 50))
        
        # Lives
        lives_text = font_manager.render_text(f"Lives: {self.player.lives}", medium_font_size, (255, 255, 255))
        surface.blit(lives_text, (15, 85))
        
        # Active entities count (bottom left corner)
        active_entities_count = self.entity_manager.count_active_entities()
        entities_text = font_manager.render_text(f"Entities: {active_entities_count}", small_font_size, (255, 255, 255))
        surface.blit(entities_text, (15, Globals.screen_height - 35))  # Bottom left
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((Globals.screen_width, Globals.screen_height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))
            
            if self.win:
                result_text = font_manager.render_text("YOU WIN!", large_font_size, (0, 255, 0))
            else:
                result_text = font_manager.render_text("GAME OVER", large_font_size, (255, 0, 0))
                
            text_rect = result_text.get_rect(center=(Globals.half_width, Globals.half_height - 60))
            surface.blit(result_text, text_rect)
            
            restart_text = font_manager.render_text("Press R to restart", medium_font_size, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(Globals.half_width, Globals.half_height))
            surface.blit(restart_text, restart_rect)
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_over:
                self.__init__()  # Reset the game
                
        elif event.type == pygame.JOYBUTTONDOWN:
            # Handle gamepad restart (Start button is usually button 7)
            if event.button == 7 and self.game_over:  # Start button
                self.__init__()  # Reset the game
    
    def test_collisions(self, entities_a, entities_b, collision_handler):
        """
        Test collisions between two lists of entities and perform custom operations
        
        Args:
            entities_a: First list of entities
            entities_b: Second list of entities (can be a single entity or list)
            collision_handler: Function that takes (entity_a, entity_b) and handles the collision
        """
        # Handle case where entities_b is a single entity
        if not isinstance(entities_b, list):
            entities_b = [entities_b]
            
        for entity_a in entities_a[:]:  # Use slice copy to allow modification during iteration
            if not entity_a.is_active():
                continue
                
            for entity_b in entities_b[:]:
                if not entity_b.is_active():
                    continue
                    
                if entity_a.collides_with(entity_b):
                    # Call the collision handler - no need for return value
                    collision_handler(entity_a, entity_b)

    def handle_bullet_enemy_collision(self, bullet, enemy):
        bullet.deactivate()
        if enemy.hit():
            self.score += 100
            self.damage_dealt += 1
        
    def handle_bullet_player_collision(self, bullet, player):
        bullet.deactivate()
        if player.hit():
            self.damage_recieved += 1
            