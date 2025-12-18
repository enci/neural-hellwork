"""
TalakatEvaluator - Simulates Talakat bullet patterns and tracks bullet positions over time
"""
import math
from typing import List, Tuple, Dict, Optional
from pygame.math import Vector2
from talakat import TalakatInterpreter, TokenType
from bullets import Bullet

class BulletSnapshot:
    """Represents a bullet's state at a specific frame"""
    def __init__(self, position: Vector2, velocity: Vector2, size: float, color: tuple, age: int):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.size = size
        self.color = color
        self.age = age  # How many frames this bullet has existed
        
    def __repr__(self):
        return f"BulletSnapshot(pos=({self.position.x:.1f}, {self.position.y:.1f}), vel=({self.velocity.x:.1f}, {self.velocity.y:.1f}), age={self.age})"

class FrameSnapshot:
    """Represents all bullets at a specific frame"""
    def __init__(self, frame_number: int):
        self.frame_number = frame_number
        self.bullets: List[BulletSnapshot] = []
        
    def add_bullet(self, bullet_snapshot: BulletSnapshot):
        """Add a bullet snapshot to this frame"""
        self.bullets.append(bullet_snapshot)
        
    def get_bullet_count(self) -> int:
        """Get the number of bullets in this frame"""
        return len(self.bullets)
        
    def get_bullets_in_area(self, center: Vector2, radius: float) -> List[BulletSnapshot]:
        """Get all bullets within a circular area"""
        bullets_in_area = []
        for bullet in self.bullets:
            distance = bullet.position.distance_to(center)
            if distance <= radius:
                bullets_in_area.append(bullet)
        return bullets_in_area
        
    def __repr__(self):
        return f"FrameSnapshot(frame={self.frame_number}, bullets={len(self.bullets)})"

class TalakatEvaluator:
    """
    Evaluates and simulates Talakat bullet patterns over time
    """
    
    def __init__(self, pattern: List[Tuple], enemy_position: Vector2, bounds: Optional[Tuple[float, float, float, float]] = None):
        """
        Initialize the evaluator with a pattern and enemy position
        
        Args:
            pattern: Talakat pattern (list of (TokenType, value) tuples)
            enemy_position: Starting position of the enemy
            bounds: Optional bounds (left, right, top, bottom) for bullet culling
        """
        self.pattern = pattern
        self.enemy_position = enemy_position.copy()
        self.interpreter = TalakatInterpreter()
        
        # Set bounds for bullet culling (default to large area)
        if bounds:
            self.bounds_left, self.bounds_right, self.bounds_top, self.bounds_bottom = bounds
        else:
            # Default large bounds
            self.bounds_left = -1000
            self.bounds_right = 1000
            self.bounds_top = -1000
            self.bounds_bottom = 1000
            
        # Simulation state
        self.active_bullets: List[Dict] = []  # List of bullet dictionaries with position, velocity, etc.
        self.frames: List[FrameSnapshot] = []  # Historical data
        self.current_frame = 0
        
    def simulate(self, num_frames: int) -> List[FrameSnapshot]:
        """
        Run the simulation for the specified number of frames
        
        Args:
            num_frames: Number of frames to simulate
            
        Returns:
            List of FrameSnapshot objects, one for each frame
        """
        self.frames.clear()
        self.active_bullets.clear()
        self.interpreter.reset()
        self.current_frame = 0
        
        for frame in range(num_frames):
            self._simulate_frame()
            
        return self.frames
    
    def _simulate_frame(self):
        """Simulate a single frame"""
        frame_snapshot = FrameSnapshot(self.current_frame)
        
        # Generate new bullets from the pattern using a custom method
        new_bullets = self._get_bullets_from_pattern()
        
        # Add new bullets to active bullets list
        for bullet_data in new_bullets:
            self.active_bullets.append(bullet_data)
        
        # Update existing bullets and create snapshots
        bullets_to_remove = []
        for i, bullet in enumerate(self.active_bullets):
            # Create snapshot before updating (so age reflects current frame)
            snapshot = BulletSnapshot(
                position=bullet['position'].copy(),
                velocity=bullet['velocity'].copy(),
                size=bullet['size'],
                color=bullet['color'],
                age=bullet['age']
            )
            
            # Update position and age for next frame
            bullet['position'] += bullet['velocity']
            bullet['age'] += 1
            
            # Check if bullet is out of bounds
            if self._is_bullet_out_of_bounds(bullet['position']):
                bullets_to_remove.append(i)
            
            # Add to frame snapshot (even if it will be removed next frame)
            frame_snapshot.add_bullet(snapshot)
        
        # Remove out-of-bounds bullets (in reverse order to maintain indices)
        for i in reversed(bullets_to_remove):
            del self.active_bullets[i]
        
        # Store the frame
        self.frames.append(frame_snapshot)
        self.current_frame += 1
    
    def _get_bullets_from_pattern(self) -> List[Dict]:
        """
        Generate bullet data from the pattern without creating actual Bullet objects
        This is a simplified version of TalakatInterpreter.get_bullets() for simulation
        """
        if self.interpreter.wait_counter > 0:
            self.interpreter.wait_counter -= 1
            return []
            
        if not self.pattern or self.interpreter.current_index >= len(self.pattern):
            return []
            
        new_bullets = []
        token_type, value = self.pattern[self.interpreter.current_index]
        
        # Handle different token types (simplified from TalakatInterpreter)
        if token_type == TokenType.ANGLE:
            self.interpreter.current_values[TokenType.ANGLE] = value
        elif token_type == TokenType.COUNT:
            self.interpreter.current_values[TokenType.COUNT] = int(value)
        elif token_type == TokenType.SPEED:
            self.interpreter.current_values[TokenType.SPEED] = value
        elif token_type == TokenType.SIZE:
            self.interpreter.current_values[TokenType.SIZE] = value
        elif token_type == TokenType.COLOR:
            self.interpreter.current_values[TokenType.COLOR] = value
        elif token_type == TokenType.WAIT:
            self.interpreter.wait_counter = int(value)
        elif token_type == TokenType.SPREAD:
            self.interpreter.current_values[TokenType.SPREAD] = value
        elif token_type == TokenType.LOOP:
            self.interpreter.loop_stack.append(self.interpreter.current_index)
            self.interpreter.loop_iterations.append(int(value))
        elif token_type == TokenType.ENDLOOP:
            if self.interpreter.loop_stack:
                loop_start = self.interpreter.loop_stack[-1]
                self.interpreter.loop_iterations[-1] -= 1
                
                if self.interpreter.loop_iterations[-1] > 0:
                    self.interpreter.current_index = loop_start
                else:
                    self.interpreter.loop_stack.pop()
                    self.interpreter.loop_iterations.pop()
        elif token_type == TokenType.RANDOM:
            import random
            param_type, min_val, max_val = value
            if param_type == TokenType.COLOR:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                self.interpreter.current_values[param_type] = (r, g, b)
            else:
                rand_value = random.uniform(min_val, max_val)
                self.interpreter.current_values[param_type] = rand_value
        elif token_type == TokenType.SEQUENCE:
            param_type, values = value
            if param_type not in self.interpreter.sequence_indices:
                self.interpreter.sequence_indices[param_type] = 0
                
            idx = self.interpreter.sequence_indices[param_type]
            self.interpreter.current_values[param_type] = values[idx % len(values)]
            self.interpreter.sequence_indices[param_type] = (idx + 1) % len(values)
        
        # Create bullet data based on current values
        if self.interpreter.wait_counter == 0:
            # Ensure all necessary keys are in the dictionary
            for key in [TokenType.COUNT, TokenType.ANGLE, TokenType.SPREAD, 
                         TokenType.SPEED, TokenType.SIZE, TokenType.COLOR]:
                if key not in self.interpreter.current_values:
                    self.interpreter.current_values[key] = self.interpreter.default_values[key]
            
            count = self.interpreter.current_values[TokenType.COUNT]
            angle = self.interpreter.current_values[TokenType.ANGLE]
            spread = self.interpreter.current_values[TokenType.SPREAD]
            speed = self.interpreter.current_values[TokenType.SPEED]
            size = self.interpreter.current_values[TokenType.SIZE]
            color = self.interpreter.current_values[TokenType.COLOR]
            
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
                
                # Create bullet data dictionary instead of Bullet object
                bullet_data = {
                    'position': Vector2(self.enemy_position.x, self.enemy_position.y),
                    'velocity': Vector2(vel_x, vel_y),
                    'size': size,
                    'color': color,
                    'age': 0
                }
                new_bullets.append(bullet_data)
        
        # Move to next token
        self.interpreter.current_index += 1
        
        # If we've reached the end, reset
        if self.interpreter.current_index >= len(self.pattern):
            self.interpreter.current_index = 0
            
        return new_bullets
    
    def _is_bullet_out_of_bounds(self, position: Vector2) -> bool:
        """Check if a bullet is outside the simulation bounds"""
        return (position.x < self.bounds_left or 
                position.x > self.bounds_right or 
                position.y < self.bounds_top or 
                position.y > self.bounds_bottom)
    
    def get_frame(self, frame_number: int) -> Optional[FrameSnapshot]:
        """Get a specific frame snapshot"""
        if 0 <= frame_number < len(self.frames):
            return self.frames[frame_number]
        return None
    
    def get_max_bullet_count(self) -> int:
        """Get the maximum number of bullets present in any single frame"""
        if not self.frames:
            return 0
        return max(frame.get_bullet_count() for frame in self.frames)
    
    def get_total_bullets_spawned(self) -> int:
        """Get the total number of bullets spawned throughout the simulation"""
        total = 0
        for frame in self.frames:
            # Count bullets with age 0 (newly spawned this frame)
            total += sum(1 for bullet in frame.bullets if bullet.age == 0)
        return total
    
    def get_pattern_density_at_point(self, point: Vector2, radius: float = 50.0) -> List[int]:
        """
        Get the number of bullets near a point across all frames
        
        Args:
            point: Center point to check
            radius: Radius around the point
            
        Returns:
            List of bullet counts per frame
        """
        density = []
        for frame in self.frames:
            count = len(frame.get_bullets_in_area(point, radius))
            density.append(count)
        return density
    
    def get_coverage_area(self) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of all bullet positions across all frames
        
        Returns:
            (min_x, max_x, min_y, max_y) tuple
        """
        if not self.frames:
            return (0, 0, 0, 0)
            
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for frame in self.frames:
            for bullet in frame.bullets:
                min_x = min(min_x, bullet.position.x)
                max_x = max(max_x, bullet.position.x)
                min_y = min(min_y, bullet.position.y)
                max_y = max(max_y, bullet.position.y)
        
        return (min_x, max_x, min_y, max_y)
    
    def print_statistics(self):
        """Print simulation statistics"""
        if not self.frames:
            print("No simulation data available")
            return
            
        print("=== Talakat Pattern Simulation Statistics ===")
        print(f"Frames simulated: {len(self.frames)}")
        print(f"Total bullets spawned: {self.get_total_bullets_spawned()}")
        print(f"Max bullets on screen: {self.get_max_bullet_count()}")
        
        min_x, max_x, min_y, max_y = self.get_coverage_area()
        print(f"Coverage area: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
        print(f"Coverage width: {max_x - min_x:.1f}")
        print(f"Coverage height: {max_y - min_y:.1f}")
        
        # Frame-by-frame bullet count
        bullet_counts = [frame.get_bullet_count() for frame in self.frames]
        avg_bullets = sum(bullet_counts) / len(bullet_counts)
        print(f"Average bullets per frame: {avg_bullets:.1f}")

def test_evaluator():
    """Test function for the TalakatEvaluator"""
    from bullet_patterns import PATTERNS
    
    # Test with a simple pattern
    test_pattern = PATTERNS["basic_spread"]  # Basic spread pattern
    enemy_pos = Vector2(0, 0)
    
    # Create evaluator with bounds
    evaluator = TalakatEvaluator(
        pattern=test_pattern,
        enemy_position=enemy_pos,
        bounds=(-500, 500, -500, 500)
    )
    
    # Run simulation
    print("Running Talakat pattern simulation...")
    frames = evaluator.simulate(120)  # 2 seconds at 60 FPS
    
    # Print statistics
    evaluator.print_statistics()
    
    # Show some frame details
    print("\n=== Sample Frame Data ===")
    for i in [0, 30, 60, 90]:
        if i < len(frames):
            frame = frames[i]
            print(f"Frame {i}: {frame.get_bullet_count()} bullets")
            if frame.bullets:
                print(f"  First bullet: {frame.bullets[0]}")

if __name__ == "__main__":
    test_evaluator()
