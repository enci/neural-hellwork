# store all global variables in one place

class Globals:
    # Game and display resolution (same for both)
    screen_width = 540
    screen_height = 720
    
    # Derived screen values (in game world coordinates)
    half_width = screen_width // 2     # 270
    half_height = screen_height // 2   # 360
    
    # World bounds (centered coordinate system: -half_width to +half_width)
    world_left = -half_width      # -270
    world_right = half_width      # 270
    world_top = -half_height      # -360
    world_bottom = half_height    # 360
    
    # Visual settings
    bg_color = (45, 46, 40)
    
    # UI colors
    ui_text_color = (200, 200, 200)    # Light gray for regular UI text
    player_color = (221, 151, 21)      # Orange/gold - matches player
    enemy_color = (255, 51, 0)         # Red - matches enemy
    
    # Game speeds (for native resolution)
    player_speed = 4.5    # Scaled up 3x from 1.5
    bullet_speed = 9.0    # Scaled up 3x from 3.0
    enemy_speed = 1.5     # Scaled up 3x from 0.5