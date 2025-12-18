"""
Predefined Talakat bullet patterns for the enemy
"""
from random import Random
from talakat import TokenType

# Collection of predefined bullet patterns
PATTERNS = {
    "basic_spread": [
        (TokenType.COUNT, 5),
        (TokenType.ANGLE, 90),      # Straight down
        (TokenType.SPREAD, 60),     # 60 degree spread
        (TokenType.SPEED, 4.5),     # Match current bullet speed
        (TokenType.SIZE, 12),       # Match current bullet size
        (TokenType.COLOR, (255, 51, 0)),  # Enemy red color
        (TokenType.WAIT, 45),       # Wait 45 frames (~0.75 seconds at 60fps)
    ],
    
    "rapid_fire": [
        (TokenType.COUNT, 3),
        (TokenType.ANGLE, 90),
        (TokenType.SPREAD, 30),
        (TokenType.SPEED, 5.0),
        (TokenType.SIZE, 10),
        (TokenType.COLOR, (255, 80, 80)),
        (TokenType.WAIT, 15),       # Faster firing
    ],
    
    "circular_burst": [
        (TokenType.COUNT, 8),
        (TokenType.ANGLE, 0),
        (TokenType.SPREAD, 360),    # Full circle
        (TokenType.SPEED, 3.5),
        (TokenType.SIZE, 14),
        (TokenType.COLOR, (255, 100, 0)),
        (TokenType.WAIT, 60),       # Slower but more bullets
    ],
    
    "spiral": [
        (TokenType.LOOP, 12),       # 12 iterations
        (TokenType.COUNT, 3),
        (TokenType.SEQUENCE, (TokenType.ANGLE, [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])),
        (TokenType.SPREAD, 15),
        (TokenType.SPEED, 4.0),
        (TokenType.SIZE, 8),
        (TokenType.COLOR, (255, 150, 50)),
        (TokenType.WAIT, 8),
        (TokenType.ENDLOOP),
        (TokenType.WAIT, 90),       # Pause between spirals
    ],
    
    "random_chaos": [
        (TokenType.LOOP, 8),
        (TokenType.COUNT, 2),
        (TokenType.RANDOM, (TokenType.ANGLE, 0, 360)),
        (TokenType.RANDOM, (TokenType.SPEED, 3.0, 6.0)),
        (TokenType.SPREAD, 45),
        (TokenType.SIZE, 10),
        (TokenType.RANDOM, (TokenType.COLOR, None, None)),  # Random color
        (TokenType.WAIT, 12),
        (TokenType.ENDLOOP),
        (TokenType.WAIT, 60),
    ],
    
    "wave_pattern": [
        (TokenType.LOOP, 5),        # 5 waves
        (TokenType.COUNT, 7),
        (TokenType.ANGLE, 90),
        (TokenType.SPREAD, 120),
        (TokenType.SEQUENCE, (TokenType.SPEED, [3.0, 4.0, 5.0, 4.0, 3.0])),
        (TokenType.SIZE, 11),
        (TokenType.COLOR, (255, 120, 120)),
        (TokenType.WAIT, 20),
        (TokenType.ENDLOOP),
        (TokenType.WAIT, 100),
    ],
    
    "focused_beam": [
        (TokenType.COUNT, 1),
        (TokenType.ANGLE, 90),      # Straight down toward player
        (TokenType.SPREAD, 0),      # No spread
        (TokenType.SPEED, 7.0),     # Fast bullet
        (TokenType.SIZE, 8),
        (TokenType.COLOR, (255, 255, 0)),  # Yellow for visibility
        (TokenType.WAIT, 30),       # Medium frequency
    ],
    
    "alternating_sides": [
        (TokenType.LOOP, 10),
        (TokenType.COUNT, 3),
        (TokenType.SEQUENCE, (TokenType.ANGLE, [45, 135])),  # Left then right
        (TokenType.SPREAD, 30),
        (TokenType.SPEED, 4.5),
        (TokenType.SIZE, 12),
        (TokenType.COLOR, (255, 80, 120)),
        (TokenType.WAIT, 25),
        (TokenType.ENDLOOP),
        (TokenType.WAIT, 75),
    ]
}

# Pattern progression for different difficulty levels
PATTERN_SEQUENCE = [
    "basic_spread",      # Level 1-2
    "rapid_fire",        # Level 3-4  
    "circular_burst",    # Level 5-6
    "wave_pattern",      # Level 7-8
    "spiral",           # Level 9
    "random_chaos"      # Level 10+
]

def get_pattern_for_level(level: int) -> list:
    # Randmize everything
    rd = Random()  # Ensure consistent random patterns for each level
    angle = 90 + rd.randint(-10, 10)  # Randomize angle slightly
    count = int(level * 1.5 + rd.randint(1, 3))  # Randomize count between 2 and 6
    speed = 4.5 + rd.uniform(-2.0, 2.0)  # Randomize speed slightly
    size = 6 + level * 2 + rd.randint(-3, 3)  # Randomize size slightly
    wait = 90 - level * 10 - rd.randint(0, 30)  # Decrease wait time with level, minimum 15
    spread = rd.randint(30, 120)  # Randomize spread between 30 and 120 degrees

    default_values = [
            (TokenType.LOOP, 2),
            (TokenType.ANGLE, angle),
            (TokenType.COUNT, count),
            (TokenType.SPEED, speed),  # Scaled down for 180x240
            (TokenType.SIZE, size),     # Scaled down for 180x240
            (TokenType.COLOR, (255, 51, 0)),
            (TokenType.WAIT, wait),
            (TokenType.SPREAD, spread)
    ]
    return default_values


    """Get the appropriate pattern for the given level"""
    if level <= 0:
        level = 1
        
    # Use pattern sequence, but cycle through if level is higher
    pattern_index = min(level - 1, len(PATTERN_SEQUENCE) - 1)
    
    # For very high levels, use random patterns
    if level > len(PATTERN_SEQUENCE):
        import random
        pattern_name = random.choice(list(PATTERNS.keys()))
    else:
        pattern_name = PATTERN_SEQUENCE[pattern_index]
    
    return PATTERNS[pattern_name]

def get_random_pattern() -> list:
    """Get a random pattern"""
    import random
    pattern_name = random.choice(list(PATTERNS.keys()))
    return PATTERNS[pattern_name]
