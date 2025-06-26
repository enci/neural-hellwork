from globals import Globals

class Game:
    def __init__(self):
        self.score = 0
        print("Globals.screen_width: ", Globals.screen_width)
        print("Globals.screen_height: ", Globals.screen_height)
        print("Globals.bg_color: ", Globals.bg_color)
        print("Globals.player_speed: ", Globals.player_speed)
        print("Globals.bullet_speed: ", Globals.bullet_speed)
        print("Globals.enemy_speed: ", Globals.enemy_speed)


    def start(self):
        print("Game started!")

    def play(self):
        # Placeholder for game logic
        print("Playing the game...")

    def end(self):
        print("Game over! Your score:", self.score)
        