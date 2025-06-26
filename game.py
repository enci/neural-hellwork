from typing import Any
import pygame
from vec2 import vec2
from player import Player
from enemy import Enemy
from bullets import PlayerBullet
from talakat import TalakatInterpreter, PATTERNS
from globals import Globals
import gymnasium as gym
from typing import Optional

class Game(gym.Env):
    def __init__(self):
        self._reset()
        
        # Initialize joystick support
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)

        # Set up the environment
        super().__init__()

        self.action_space = gym.spaces.Discrete(10)
        self.observation_space = gym.spaces.Dict({
            'total_damage_dealt': gym.spaces.Box(low=0, high=float('inf'), shape=(1,), dtype=float),
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
        self.player = Player()
        self.enemy = Enemy()
        self.enemy_bullets = []
        self.player_bullets = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.win = False
        self.interpreter = TalakatInterpreter()
        self.current_pattern = PATTERNS[self.enemy.pattern_index]
        self.shoot_cooldown = 0
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

    def get_gamepad_input(self):
        """Get gamepad input if available"""
        gamepad_input = {}
        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            gamepad_input['left_stick_x'] = joystick.get_axis(0)
            gamepad_input['left_stick_y'] = joystick.get_axis(1)
            gamepad_input['button_a'] = joystick.get_button(0)
            gamepad_input['button_start'] = joystick.get_button(7)
        return gamepad_input
        
    def update(self):
        """Update game state"""
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        gamepad_input = self.get_gamepad_input()
        
        # Update player
        self.player.update(keys, gamepad_input)
        
        # Player shooting
        shoot_pressed = (keys[pygame.K_SPACE] or 
                        gamepad_input.get('button_a', False))
        
        if shoot_pressed and self.shoot_cooldown <= 0:
            bullet_pos = vec2(self.player.position.x, 
                       self.player.position.y - self.player.radius)
            self.player_bullets.append(PlayerBullet(bullet_pos))
            self.shoot_cooldown = 10
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            
            # Check for collision with enemy
            if bullet.collides_with(self.enemy):
                self.player_bullets.remove(bullet)
                if self.enemy.hit():
                    self.score += 100
                    self.level += 1
                    self.spawn_enemy_timer = 120
                    break
                    
            # Remove offscreen bullets
            if bullet.is_offscreen():
                self.player_bullets.remove(bullet)
                
        # Enemy generation and bullet pattern update
        if self.spawn_enemy_timer > 0:
            self.spawn_enemy_timer -= 1
            if self.spawn_enemy_timer <= 0:
                self.enemy = Enemy()
                self.enemy.health = min(100 + (self.level - 1) * 20, 300)
                self.current_pattern = PATTERNS[self.enemy.pattern_index]
                self.interpreter.reset()
                self.pattern_change_effect_timer = 30
        else:
            # Update enemy
            pattern_changed = self.enemy.update()
            
            # Check if pattern changed
            if pattern_changed:
                self.current_pattern = PATTERNS[self.enemy.pattern_index]
                self.interpreter.reset()
                self.pattern_change_effect_timer = 30
            
            # Generate enemy bullets based on pattern
            self.enemy_shoot_timer += 1
            if self.enemy_shoot_timer >= 3:
                self.enemy_shoot_timer = 0
                if self.pattern_change_effect_timer <= 0:
                    new_bullets = self.interpreter.get_bullets(self.current_pattern, self.enemy.position)
                    self.enemy_bullets.extend(new_bullets)
        
        # Update pattern change effect timer
        if self.pattern_change_effect_timer > 0:
            self.pattern_change_effect_timer -= 1
        
        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            
            # Check for collision with player
            if bullet.collides_with(self.player):
                self.enemy_bullets.remove(bullet)
                if self.player.hit():
                    if self.player.lives <= 0:
                        self.game_over = True
                break
                
            # Remove offscreen bullets
            if bullet.is_offscreen():
                self.enemy_bullets.remove(bullet)
                
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
        
        # Draw player and enemy
        self.player.draw(game_surface)
        if self.spawn_enemy_timer <= 0:
            self.enemy.draw(game_surface)
        
        # Draw bullets
        for bullet in self.enemy_bullets:
            bullet.draw(game_surface)
            
        for bullet in self.player_bullets:
            bullet.draw(game_surface)
            
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
            if len(self.joysticks) > 0:
                if event.button == 7 and self.game_over:  # Start button
                    self.__init__()  # Reset the game