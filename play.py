import pygame
import sys
from game import Game
from globals import Globals

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((Globals.screen_width, Globals.screen_height))
    pygame.display.set_caption("Neural Hellwork")
    
    # Set window icon (optional - only if icon file exists)
    try:
        icon = pygame.image.load("assets/icon.png")  # or "icon.ico" for Windows
        pygame.display.set_icon(icon)
    except pygame.error:
        print("Icon file not found, using default icon")
    
    # Clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create game instance
    game = Game()
    #game.start()
    
    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Pass events to the game for handling
            game.handle_event(event)
        
        # Fill the screen with background color
        screen.fill(Globals.bg_color)
                
        game.update()
        game.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Control frame rate (60 FPS)
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()