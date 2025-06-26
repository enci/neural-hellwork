import random
import math
from enum import Enum

import pygame
from bullets import Bullet

class TokenType(Enum):
    ANGLE = "angle"
    COUNT = "count"
    SPEED = "speed"
    SIZE = "size"
    COLOR = "color"
    WAIT = "wait"
    SPREAD = "spread"
    LOOP = "loop"
    ENDLOOP = "endloop"
    RANDOM = "random"
    SEQUENCE = "sequence"

# Define patterns for 180x240 resolution with scaled values
PATTERNS = [
    # Simple aimed pattern
    [
        (TokenType.COUNT, 2),
        (TokenType.SPEED, 2),  # Scaled down speed
        (TokenType.SIZE, 3),   # Scaled down size
        (TokenType.ANGLE, 225),
        (TokenType.SPREAD, 20),
        (TokenType.WAIT, 15)
    ],
    
    # Wide spread pattern
    [
        (TokenType.COUNT, 6),
        (TokenType.SPREAD, 120),
        (TokenType.SPEED, 1.5),  # Scaled down speed
        (TokenType.SIZE, 3),     # Scaled down size
        (TokenType.ANGLE, 270),
        (TokenType.WAIT, 25)
    ],
    
    # Rotating spiral
    [
        (TokenType.LOOP, 24),
        (TokenType.ANGLE, 180),
        (TokenType.SEQUENCE, (TokenType.ANGLE, [15, 15])),
        (TokenType.COUNT, 2),
        (TokenType.SPREAD, 10),
        (TokenType.SPEED, 1.5),  # Scaled down speed
        (TokenType.SIZE, 2.5),   # Scaled down size
        (TokenType.WAIT, 4),
        (TokenType.ENDLOOP, None)
    ],
    
    # Random directional burst
    [
        (TokenType.LOOP, 4),
        (TokenType.RANDOM, (TokenType.ANGLE, 180, 360)),
        (TokenType.RANDOM, (TokenType.SPEED, 1, 2.5)),  # Scaled down speed
        (TokenType.RANDOM, (TokenType.SIZE, 2, 4)),     # Scaled down size
        (TokenType.COUNT, 10),
        (TokenType.SPREAD, 45),
        (TokenType.WAIT, 20),
        (TokenType.ENDLOOP, None)
    ],
    
    # Sweeping wave
    [
        (TokenType.LOOP, 8),
        (TokenType.COUNT, 8),
        (TokenType.SPREAD, 30),
        (TokenType.SEQUENCE, (TokenType.ANGLE, [200, 220, 240, 260, 280, 300, 320, 340])),
        (TokenType.SEQUENCE, (TokenType.SIZE, [2, 2.5, 3, 3.5, 3, 2.5, 2, 1.5])),  # Scaled down sizes
        (TokenType.SPEED, 1.25),  # Scaled down speed
        (TokenType.WAIT, 8),
        (TokenType.ENDLOOP, None)
    ]
]

class TalakatInterpreter:
    def __init__(self):
        self.default_values = {
            TokenType.ANGLE: 270,
            TokenType.COUNT: 1,
            TokenType.SPEED: 1.5,  # Scaled down for 180x240
            TokenType.SIZE: 3,     # Scaled down for 180x240
            TokenType.COLOR: (255, 255, 255),
            TokenType.WAIT: 0,
            TokenType.SPREAD: 0
        }
        
        self.current_values = {k: v for k, v in self.default_values.items()}
        self.loop_stack = []
        self.loop_iterations = []
        self.current_index = 0
        self.wait_counter = 0
        self.sequence_indices = {}
    
    def reset(self):
        """Reset interpreter state"""
        self.current_values = {k: v for k, v in self.default_values.items()}
        self.loop_stack = []
        self.loop_iterations = []
        self.current_index = 0
        self.wait_counter = 0
        self.sequence_indices = {}
    
    def get_bullets(self, tokens, enemy_pos):
        """Generate bullets based on the current state of the interpreter"""
        if self.wait_counter > 0:
            self.wait_counter -= 1
            return []
            
        if not tokens or self.current_index >= len(tokens):
            return []
            
        new_bullets = []
        token_type, value = tokens[self.current_index]
        
        # Handle different token types
        if token_type == TokenType.ANGLE:
            self.current_values[TokenType.ANGLE] = value
        elif token_type == TokenType.COUNT:
            self.current_values[TokenType.COUNT] = int(value)
        elif token_type == TokenType.SPEED:
            self.current_values[TokenType.SPEED] = value
        elif token_type == TokenType.SIZE:
            self.current_values[TokenType.SIZE] = value
        elif token_type == TokenType.COLOR:
            self.current_values[TokenType.COLOR] = value
        elif token_type == TokenType.WAIT:
            self.wait_counter = int(value)
        elif token_type == TokenType.SPREAD:
            self.current_values[TokenType.SPREAD] = value
        elif token_type == TokenType.LOOP:
            self.loop_stack.append(self.current_index)
            self.loop_iterations.append(int(value))
        elif token_type == TokenType.ENDLOOP:
            if self.loop_stack:
                loop_start = self.loop_stack[-1]
                self.loop_iterations[-1] -= 1
                
                if self.loop_iterations[-1] > 0:
                    self.current_index = loop_start
                else:
                    self.loop_stack.pop()
                    self.loop_iterations.pop()
        elif token_type == TokenType.RANDOM:
            param_type, min_val, max_val = value
            rand_value = random.uniform(min_val, max_val)
            if param_type == TokenType.COLOR:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                self.current_values[param_type] = (r, g, b)
            else:
                self.current_values[param_type] = rand_value
        elif token_type == TokenType.SEQUENCE:
            param_type, values = value
            if param_type not in self.sequence_indices:
                self.sequence_indices[param_type] = 0
                
            idx = self.sequence_indices[param_type]
            self.current_values[param_type] = values[idx % len(values)]
            self.sequence_indices[param_type] = (idx + 1) % len(values)
        
        # Create bullets based on current values
        if self.wait_counter == 0:
            # Ensure all necessary keys are in the dictionary
            for key in [TokenType.COUNT, TokenType.ANGLE, TokenType.SPREAD, 
                         TokenType.SPEED, TokenType.SIZE, TokenType.COLOR]:
                if key not in self.current_values:
                    self.current_values[key] = self.default_values[key]
            
            count = self.current_values[TokenType.COUNT]
            angle = self.current_values[TokenType.ANGLE]
            spread = self.current_values[TokenType.SPREAD]
            speed = self.current_values[TokenType.SPEED]
            size = self.current_values[TokenType.SIZE]
            color = self.current_values[TokenType.COLOR]
            
            for i in range(count):
                if count > 1 and spread > 0:
                    fraction = i / (count - 1) if count > 1 else 0
                    current_angle = angle - spread/2 + fraction * spread
                else:
                    current_angle = angle
                    
                # Convert angle to radians
                rad_angle = math.radians(current_angle)
                
                # Calculate velocity based on angle and speed
                vel_x = math.cos(rad_angle) * speed
                vel_y = math.sin(rad_angle) * speed
                
                new_bullet = Bullet(
                    pygame.math.Vector2(enemy_pos.x, enemy_pos.y),
                    pygame.math.Vector2(vel_x, vel_y),
                    size, color
                )
                new_bullets.append(new_bullet)
        
        # Move to next token
        self.current_index += 1
        
        # If we've reached the end, reset
        if self.current_index >= len(tokens):
            self.current_index = 0
            
        return new_bullets