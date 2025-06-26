from typing import Any
import pygame
from pygame.math import Vector2
import numpy as np
from player import Player
from enemy import Enemy
from bullets import PlayerBullet
from talakat import TalakatInterpreter, PATTERNS
from globals import Globals
from entity import EntityTag
from entity_manager import EntityManager
import gymnasium as gym
from typing import Optional

class Game(gym.Env):
    def __init__(self):
        self._reset()
        
        # Initialize joystick support
        pygame.joystick.init()
        
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
            'total_damage_dealt': self.total_damage_dealt,
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
        
        # Create entities
        self.player = Player()
        self.enemy = Enemy()  # Back to single enemy
        
        # Add entities to manager
        self.entity_manager.add_entity(self.player)
        self.entity_manager.add_entity(self.enemy)
        
        # Game state
        self.score = 0
        self.level = 1
        self.game_over = False
        self.win = False
        self.interpreter = TalakatInterpreter()
        self.current_pattern = PATTERNS[self.enemy.pattern_index]
        self.enemy_shoot_timer = 0
        self.spawn_enemy_timer = 0
        self.pattern_change_effect_timer = 0
        self.total_damage_dealt = 0

    def step(self, action: Any):
        """Perform a game step based on the action"""
        if self.game_over:
            return self._get_obs(), 0, True, False, self._get_info()
        
        # Update game state
        self.update()
        
        # Calculate reward
        reward = 0
        if self.win:
            reward = 1000
        elif self.game_over:
            reward = -1000
        
        observation = self._get_obs()
        terminated = self.game_over
        truncated = False  # No truncation logic in this game
        info = self._get_info()

        return observation, reward, terminated, truncated, info
        
    def update(self):
        """Update game state"""

        if self.game_over:
            return
            
        # Update player (now handles input and shooting internally)
        self.player.update()
        
        # Get any new bullets from player and add them to entity manager
        new_bullets = self.player.get_new_bullets()
        for bullet in new_bullets:
            self.entity_manager.add_entity(bullet)
            
        # Update player bullets and remove offscreen ones
        player_bullets = self.entity_manager.get_entities_by_tag(EntityTag.PLAYER_BULLET)
        for bullet in player_bullets[:]:
            bullet.update()
            if bullet.is_offscreen():
                bullet.deactivate()
        
        # Update enemy bullets and remove offscreen ones
        enemy_bullets = self.entity_manager.get_entities_by_tag(EntityTag.ENEMY_BULLET)
        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.is_offscreen():
                bullet.deactivate()
        
        # Handle all collision interactions
        self.add_collision_handlers()
                
        # Enemy generation and bullet pattern update
        if self.spawn_enemy_timer > 0:
            self.spawn_enemy_timer -= 1
            if self.spawn_enemy_timer <= 0:
                # Remove old enemy and create new one
                self.entity_manager.remove_entity(self.enemy)
                self.enemy = Enemy()
                self.enemy.health = min(100 + (self.level - 1) * 20, 300)
                self.entity_manager.add_entity(self.enemy)
                self.current_pattern = PATTERNS[self.enemy.pattern_index]
                self.interpreter.reset()
                self.pattern_change_effect_timer = 30
        else:
            # Update enemy
            self.enemy.update()
            
            # Check if pattern changed
            if self.enemy.did_pattern_change():
                self.current_pattern = PATTERNS[self.enemy.pattern_index]
                self.interpreter.reset()
                self.pattern_change_effect_timer = 30
            
            # Generate enemy bullets based on pattern (only when enemy is in position)
            self.enemy_shoot_timer += 1
            if self.enemy_shoot_timer >= 3:
                self.enemy_shoot_timer = 0
                if (self.pattern_change_effect_timer <= 0 and 
                    not self.enemy.is_entering):  # Don't shoot while entering
                    new_bullets = self.interpreter.get_bullets(self.current_pattern, self.enemy.position)
                    for bullet in new_bullets:
                        self.entity_manager.add_entity(bullet)
        
        # Update pattern change effect timer
        if self.pattern_change_effect_timer > 0:
            self.pattern_change_effect_timer -= 1
        
        # Clean up inactive entities
        self.entity_manager.cleanup_inactive()
                
        # Check win condition
        if self.level > 10:
            self.win = True
            self.game_over = True
    
    def draw(self, screen):
        """Draw everything to the screen"""
        # Create a surface for the actual game resolution
        game_surface = pygame.Surface((Globals.screen_width // 3, Globals.screen_height // 3))

        
        # Clear with background color
        game_surface.fill(Globals.bg_color)

        # Set up camera offset for centered coordinates (0,0 at center)
        # Game resolution is 180x240, so center is at (90, 120)
        camera_offset = Vector2(90, 120)

        # draw a red circle at the center (0,0 in our coordinate system)
        center_screen_pos = Vector2(0, 0) + camera_offset
        pygame.draw.circle(game_surface, (255, 0, 0), (int(center_screen_pos.x), int(center_screen_pos.y)), 10)
        
        # Draw all entities using entity manager with camera offset
        self.entity_manager.draw_all(game_surface, camera_offset)
            
        # Draw UI
        self._draw_ui(game_surface)
        
        # Scale up 3x and blit to main screen
        scaled_surface = pygame.transform.scale(game_surface, (Globals.screen_width, Globals.screen_height))
        screen.blit(scaled_surface, (0, 0))
        
    def _draw_ui(self, surface):
        """Draw UI elements"""
        font = pygame.font.Font(None, 12)  # Smaller font for 180x240 resolution
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (5, 5))
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        surface.blit(level_text, (5, 15))
        
        # Lives
        lives_text = font.render(f"Lives: {self.player.lives}", True, (255, 255, 255))
        surface.blit(lives_text, (5, 25))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((180, 240))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))
            
            if self.win:
                result_text = font.render("YOU WIN!", True, (0, 255, 0))
            else:
                result_text = font.render("GAME OVER", True, (255, 0, 0))
                
            text_rect = result_text.get_rect(center=(90, 100))
            surface.blit(result_text, text_rect)
            
            restart_text = font.render("Press R to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(90, 120))
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
    
    def add_collision_handlers(self):
        """Add collision handlers using the generic collision system"""
        
        # Player bullets vs enemy
        player_bullets = self.entity_manager.get_entities_by_tag(EntityTag.PLAYER_BULLET)
        def handle_bullet_enemy_collision(bullet, enemy):
            bullet.deactivate()
            if enemy.hit():
                self.score += 100
                self.total_damage_dealt += 1
                self.level += 1
                self.spawn_enemy_timer = 180  # 3 seconds instead of 2
                
                # Clear all remaining player bullets when enemy dies
                remaining_bullets = self.entity_manager.get_entities_by_tag(EntityTag.PLAYER_BULLET)
                for remaining_bullet in remaining_bullets:
                    remaining_bullet.deactivate()
        
        self.test_collisions(player_bullets, self.enemy, handle_bullet_enemy_collision)
        
        # Enemy bullets vs player
        enemy_bullets = self.entity_manager.get_entities_by_tag(EntityTag.ENEMY_BULLET)
        def handle_bullet_player_collision(bullet, player):
            bullet.deactivate()
            player.hit()  # Player handles its own state
        
        self.test_collisions(enemy_bullets, self.player, handle_bullet_player_collision)
        
        # Check game over condition separately
        if self.player.lives <= 0:
            self.game_over = True