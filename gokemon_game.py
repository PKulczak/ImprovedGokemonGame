import pygame
from Welcome import Welcome
from canvas import Canvas
from frame import Frame
from clock import Clock
from entities import Player
from world import Background
from game import Game, Keyboard, WIDTH, HEIGHT, ensure_save_files_exist

pygame.init()

#creates the live save files from the bundled defaults if they don't exist yet -
#e.g. right after cloning the repo, since the live files themselves aren't committed
ensure_save_files_exist()

kbd = Keyboard()
clock = Clock()
player = Player(clock)
welcome = Welcome("welcome.png")
tutorial = Welcome("tutorial.png")
background = Background("map2y", WIDTH, HEIGHT)

#sets up frame and all the event handlers
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gokemon')
canvas = Canvas(screen)
frame = Frame(screen, canvas)
frame.set_canvas_background('Black')

game = Game(welcome, tutorial, player, kbd, background, frame)
game.load_game()

frame.add_input("Player Name:", player.add_name, pygame.K_r)
frame.add_input("Type 'yes' to start a new game:", game.new_game, pygame.K_n)
frame.set_draw_handler(game.draw)
frame.set_keydown_handler(kbd.keyDown)
frame.set_keyup_handler(kbd.keyUp)
frame.start()
pygame.quit()
