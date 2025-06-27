#!/usr/bin/env python3
"""
Comprehensive demonstration of the TalakatEvaluator with multiple patterns
"""

from talakat_evaluator import TalakatEvaluator, BulletSnapshot, FrameSnapshot
from talakat import PATTERNS, TokenType
from pygame.math import Vector2

def demonstrate_evaluator():
    """Demonstrate the TalakatEvaluator with different patterns"""
    
    print("=" * 60)
    print("TALAKAT EVALUATOR DEMONSTRATION")
    print("=" * 60)
    
    enemy_position = Vector2(0, 0)
    simulation_frames = 180  # 3 seconds at 60 FPS
    bounds = (-400, 400, -400, 400)  # Reasonable bounds
    
    # Test each pattern
    for i, pattern in enumerate(PATTERNS):
        print(f"\n🎯 PATTERN {i + 1}: {get_pattern_description(i)}")
        print("-" * 50)
        
        # Create evaluator
        evaluator = TalakatEvaluator(pattern, enemy_position, bounds)
        
        # Run simulation
        frames = evaluator.simulate(simulation_frames)
        
        # Print statistics
        evaluator.print_statistics()
        
        # Analyze danger zones
        analyze_danger_zones(evaluator, enemy_position)
        
        print()

def get_pattern_description(pattern_index: int) -> str:
    """Get a description of the pattern"""
    descriptions = [
        "Simple Aimed Pattern",
        "Wide Spread Pattern", 
        "Rotating Spiral",
        "Random Directional Burst",
        "Sweeping Wave"
    ]
    return descriptions[pattern_index] if pattern_index < len(descriptions) else f"Pattern {pattern_index}"

def analyze_danger_zones(evaluator: TalakatEvaluator, center: Vector2):
    """Analyze danger zones around a central point"""
    print("   📊 Danger Zone Analysis:")
    
    # Check different distances from center
    zones = [
        ("Close Range", 50),
        ("Medium Range", 100),
        ("Long Range", 200)
    ]
    
    for zone_name, radius in zones:
        density = evaluator.get_pattern_density_at_point(center, radius)
        if density:
            max_bullets = max(density)
            avg_bullets = sum(density) / len(density)
            print(f"   • {zone_name} (r={radius}): Max {max_bullets} bullets, Avg {avg_bullets:.1f}")

def test_custom_pattern():
    """Test with a custom pattern"""
    print("\n" + "=" * 60)
    print("CUSTOM PATTERN TEST")
    print("=" * 60)
    
    # Create a custom pattern: fast spiral
    custom_pattern = [
        (TokenType.LOOP, 60),  # Loop 60 times
        (TokenType.ANGLE, 0),  # Start at 0 degrees
        (TokenType.SEQUENCE, (TokenType.ANGLE, [i * 6 for i in range(60)])),  # Rotate 6 degrees each time
        (TokenType.COUNT, 3),  # 3 bullets per shot
        (TokenType.SPREAD, 15),  # Small spread
        (TokenType.SPEED, 3.0),  # Fast bullets
        (TokenType.SIZE, 4),
        (TokenType.WAIT, 2),  # Fire every 2 frames
        (TokenType.ENDLOOP, None)
    ]
    
    print("Custom Pattern: Fast Spiral (3 bullets, 6° rotation, every 2 frames)")
    
    evaluator = TalakatEvaluator(custom_pattern, Vector2(0, 0), (-500, 500, -500, 500))
    frames = evaluator.simulate(120)  # 2 seconds
    
    evaluator.print_statistics()
    
    # Show frame progression
    print("\n   📈 Frame Progression:")
    sample_frames = [0, 20, 40, 60, 80, 100]
    for frame_num in sample_frames:
        if frame_num < len(frames):
            frame = frames[frame_num]
            print(f"   Frame {frame_num:3d}: {frame.get_bullet_count():3d} bullets")

def test_pattern_comparison():
    """Compare different patterns side by side"""
    print("\n" + "=" * 60)
    print("PATTERN COMPARISON")
    print("=" * 60)
    
    enemy_pos = Vector2(0, 0)
    simulation_frames = 60  # 1 second
    bounds = (-300, 300, -300, 300)
    
    results = []
    
    # Test first 3 patterns for comparison
    for i in range(min(3, len(PATTERNS))):
        evaluator = TalakatEvaluator(PATTERNS[i], enemy_pos, bounds)
        frames = evaluator.simulate(simulation_frames)
        
        stats = {
            'name': get_pattern_description(i),
            'total_spawned': evaluator.get_total_bullets_spawned(),
            'max_on_screen': evaluator.get_max_bullet_count(),
            'avg_per_frame': sum(f.get_bullet_count() for f in frames) / len(frames),
            'coverage': evaluator.get_coverage_area()
        }
        results.append(stats)
    
    # Print comparison table
    print(f"{'Pattern':<20} {'Spawned':<8} {'Max':<5} {'Avg':<6} {'Coverage':<20}")
    print("-" * 65)
    
    for stats in results:
        min_x, max_x, min_y, max_y = stats['coverage']
        coverage_str = f"{max_x-min_x:.0f}×{max_y-min_y:.0f}"
        print(f"{stats['name']:<20} {stats['total_spawned']:<8} {stats['max_on_screen']:<5} {stats['avg_per_frame']:<6.1f} {coverage_str:<20}")

if __name__ == "__main__":
    demonstrate_evaluator()
    test_custom_pattern()
    test_pattern_comparison()
