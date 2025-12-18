#!/usr/bin/env python3
"""Demo showing different Talakat bullet patterns"""

import pygame
import sys
from pygame.math import Vector2
from globals import Globals
from enemy import Enemy
from entity_manager import EntityManager
from entity import EntityTag
from bullet_patterns import PATTERNS, get_pattern_for_level
from antialiased_draw import draw_antialiased_circle
from font_manager import font_manager

def main():
    pygame.init()
    screen = pygame.display.set_mode((Globals.screen_width, Globals.screen_height))
    pygame.display.set_caption("Talakat Bullet Patterns Demo")
    clock = pygame.time.Clock()
    
    # Create entity manager and enemy
    entity_manager = EntityManager()
    enemy = Enemy(entity_manager)
    entity_manager.add_entity(enemy)
    
    # Pattern cycling variables
    pattern_names = list(PATTERNS.keys())
    current_pattern_index = 0
    pattern_timer = 0
    pattern_duration = 300  # 5 seconds at 60fps
    
    # Set initial pattern
    enemy.current_pattern = PATTERNS[pattern_names[current_pattern_index]]
    enemy.talakat_interpreter.reset()
    
    camera_offset = Vector2(Globals.half_width, Globals.half_height)
    
    running = True
    frame_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Manually advance to next pattern
                    current_pattern_index = (current_pattern_index + 1) % len(pattern_names)
                    enemy.current_pattern = PATTERNS[pattern_names[current_pattern_index]]
                    enemy.talakat_interpreter.reset()
                    pattern_timer = 0
                elif event.key == pygame.K_r:
                    # Reset current pattern
                    enemy.talakat_interpreter.reset()
                elif event.key == pygame.K_c:
                    # Clear all bullets
                    bullets = entity_manager.get_entities_by_tag(EntityTag.ENEMY_BULLET)
                    for bullet in bullets:
                        bullet.deactivate()
                    entity_manager.cleanup_inactive()
        
        # Update pattern cycling
        pattern_timer += 1
        if pattern_timer >= pattern_duration:
            current_pattern_index = (current_pattern_index + 1) % len(pattern_names)
            enemy.current_pattern = PATTERNS[pattern_names[current_pattern_index]]
            enemy.talakat_interpreter.reset()
            pattern_timer = 0
        
        # Update entities
        entity_manager.update_all()
        
        # Clean up off-screen bullets
        active_entities = entity_manager.get_active_entities()
        for entity in active_entities:
            if entity.is_offscreen():
                entity.deactivate()
        entity_manager.cleanup_inactive()
        
        # Draw everything
        screen.fill((25, 25, 25))  # Dark background
        
        # Draw all entities
        entity_manager.draw_all(screen, camera_offset)
        
        # Draw UI
        current_pattern_name = pattern_names[current_pattern_index]
        pattern_progress = pattern_timer / pattern_duration
        
        # Title
        title_text = font_manager.render_text("Talakat Bullet Patterns Demo", 32, (255, 255, 255))
        screen.blit(title_text, (20, 20))
        
        # Current pattern
        pattern_text = font_manager.render_text(f"Pattern: {current_pattern_name}", 24, (200, 200, 255))
        screen.blit(pattern_text, (20, 60))
        
        # Progress bar
        bar_width = 300
        bar_height = 20
        bar_x = 20
        bar_y = 90
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Progress
        pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_width * pattern_progress), bar_height))
        # Border
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Instructions
        instructions = [
            "SPACE - Next pattern",
            "R - Reset pattern", 
            "C - Clear bullets",
            "ESC - Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_manager.render_text(instruction, 18, (180, 180, 180))
            screen.blit(text, (20, 130 + i * 25))
        
        # Pattern list
        list_text = font_manager.render_text("Available Patterns:", 20, (255, 255, 255))
        screen.blit(list_text, (20, 250))
        
        for i, pattern_name in enumerate(pattern_names):
            color = (255, 255, 100) if i == current_pattern_index else (150, 150, 150)
            text = font_manager.render_text(f"{i+1}. {pattern_name}", 16, color)
            screen.blit(text, (40, 280 + i * 22))
        
        # Entity count
        entity_count = len(entity_manager.get_active_entities())
        count_text = font_manager.render_text(f"Active entities: {entity_count}", 20, (255, 255, 255))
        screen.blit(count_text, (20, Globals.screen_height - 40))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()

if __name__ == "__main__":
    main()
