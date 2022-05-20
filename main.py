import math

import pygame
from pygame.math import Vector2

class Wall(object):
    def __init__(self, size, position):
        super().__init__()
        self.info = [size, position]
        self.surface = pygame.surface.Surface((size))
        self.rect = self.surface.get_rect()
        self.rect.topleft = position

    def return_rect(self):
        return self.rect

class Buttons(object):
    def __init__(self, text, position, font_size, color, bg, window):
        super().__init__()
        self.position = position
        self.font = pygame.font.SysFont("Arial", font_size)
        self.text = self.font.render(text, True, color)
        self.surface = pygame.surface.Surface((self.text.get_size()))
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = self.surface.get_rect()
        self.rect.center = self.position
        self.window = window

    def show(self):
        self.window.blit(self.surface, (self.position[0] - self.text.get_size()[0]/2,
                                        self.position[1] - self.text.get_size()[1]/2))

    def return_rect(self):
        return self.rect

class Ball(pygame.sprite.Sprite):
    def __init__(self, walls):
        super().__init__()
        self.walls = walls
        self.start_point = Vector2(100, 100)
        self.image = pygame.image.load("ball.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.start_point
        self.speed = Vector2(0.001, 0.001)
        self.position = self.start_point
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0.001, 0.001)
        self.ready_to_shot = round(abs(self.velocity[0]), 2) == 0 and round(abs(self.velocity[1]), 2) == 0

    def update(self):
        self.ready_to_shot = round(self.velocity[0], 0) == 0 and round(self.velocity[1], 2) == 0
        self.physics()

    def physics(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        self.rect.center = self.position
        self.velocity *= 0.99
        self.acceleration *= 0

        self.bouncing()

    def bouncing(self):
        # Collide with screen border
        if self.rect.right >= 1300:
            self.velocity[0] *= -1
            self.position[0] -= 4
        if self.rect.left <= 0:
            self.velocity[0] *= -1
            self.position[0] += 4
        if self.rect.bottom >= 900:
            self.velocity[1] *= -1
            self.position[1] -= 4
        if self.rect.top <= 0:
            self.velocity[1] *= -1
            self.position[1] += 4

        # collide with walls
        for wall in self.walls:
            wall_rect = wall.return_rect()
            if self.rect.colliderect(wall_rect):
                if abs(wall_rect.left - self.rect.right) < 10:
                    print("right")
                    self.velocity[0] *= -1
                    self.position[0] -= 2
                elif abs(wall_rect.right - self.rect.left) < 10:
                    print("left")
                    self.velocity[0] *= -1
                    self.position[0] += 2
                elif abs(wall_rect.top - self.rect.bottom) < 10:
                    print("bottom")
                    self.velocity[1] *= -1
                    self.position[1] -= 2
                elif abs(wall_rect.bottom - self.rect.top) < 10:
                    print("top")
                    self.velocity[1] *= -1
                    self.position[1] += 2

    def speeding(self, menu, main_game_rect):
        mouse_position = pygame.mouse.get_pos()
        if not menu.active_menu:
            if main_game_rect.collidepoint(mouse_position):
                if self.ready_to_shot:
                    self.velocity *= 0
                    space_mouse_ball = Vector2(mouse_position[0] - self.position[0],
                                               mouse_position[1] - self.position[1])
                    multipler = math.sqrt((space_mouse_ball[0] ** 2 + space_mouse_ball[1] ** 2) / 100)
                    new_acceleration = [space_mouse_ball[0] / multipler,
                                        space_mouse_ball[1] / multipler]
                    self.velocity = Vector2(new_acceleration[0], new_acceleration[1])

class Menu:
    def __init__(self, window):
        self.window = window
        self.start_button = Buttons("start", [800, 450], 50, (50, 50, 50), (15, 15, 15), window)
        self.menu = pygame.surface.Surface((1600, 900))
        self.menu_rect = self.menu.get_rect()
        self.menu_rect.topleft = (0, 0)
        self.active_menu = True

    def show(self):
        if self.active_menu:
            pygame.draw.rect(self.window, (15, 15, 15), self.menu_rect)
            self.start_button.show()

    def if_clicked_buttons(self):
        mouse_position = pygame.mouse.get_pos()
        if self.start_button.return_rect().collidepoint(mouse_position):
            self.active_menu = False

class Editor:
    def __init__(self, walls, window):
        self.walls = walls
        self.active_editor = False
        self.editor_button = Buttons("editor", [1600 - 150, 50], 50, (15, 15, 15), (50, 50, 50), window)
        self.close_button = Buttons("close", [1600 - 150, 50], 50, (15, 15, 15), (50, 50, 50), window)
        self.new_wall_button = Buttons("new wall", [1600 - 150, 100], 50, (15, 15, 15), (50, 50, 50), window)
        self.undo_button = Buttons("undo", [1600 - 150, 150], 50, (15, 15, 15), (50, 50, 50), window)
        self.adding_wall = False

    def show(self):
        if self.active_editor:
            self.close_button.show()
            self.new_wall_button.show()
            self.undo_button.show()
        else:
            self.editor_button.show()

    def change_mode(self):
        if self.active_editor:
            self.active_editor = False
        else:
            self.active_editor = True

    def new_wall(self, size, position):
        abs_size = (abs(size[0]), abs(size[1]))
        if size[0] > 0 and size[1] > 0:
            print(1)
            self.walls.add_wall(Wall(abs_size, (position[0] - abs_size[0], position[1] - abs_size[1])))
        elif size[0] > 0 and size[1] < 0:
            print(2)
            self.walls.add_wall(Wall(abs_size, (position[0] - abs_size[0], position[1])))
        elif size[1] > 0 and size[0] < 0:
            print(3)
            self.walls.add_wall(Wall(abs_size, (position[0], position[1] - abs_size[1])))
        else:
            print(4)
            self.walls.add_wall(Wall(abs_size, position))


    def change_new_wall_mode(self):
        if self.adding_wall:
            self.adding_wall = False
        else:
            self.adding_wall = True

    def if_clicked_buttons(self):
        mouse_position = pygame.mouse.get_pos()
        if not self.active_editor:
            if self.editor_button.return_rect().collidepoint(mouse_position):
                self.change_mode()
        elif self.close_button.return_rect().collidepoint(mouse_position):
            self.change_mode()
        elif self.new_wall_button.return_rect().collidepoint(mouse_position):
            self.change_new_wall_mode()
        elif self.undo_button.return_rect().collidepoint(mouse_position):
            self.walls.delete_last_wall()

class Walls:
    def __init__(self):
        self.walls_list = []

    def add_wall(self, wall):
        print(f"added wall at: {wall.info[1]}, size: {wall.info[0]}, id: {len(self.walls_list)}")
        self.walls_list.append(wall)

    def delete_last_wall(self):
        if len(self.walls_list) > 0:
            print(f"deleted wall from: {self.walls_list[len(self.walls_list) - 1].info[1]}, size: {self.walls_list[len(self.walls_list) - 1].info[0]}, id: {len(self.walls_list) - 1}")
            self.walls_list.pop(len(self.walls_list) - 1)

# Window
pygame.init()
window = pygame.display.set_mode((1600, 900))
# Menu
menu = Menu(window)

# Main game
main_game = pygame.surface.Surface((1300, 900))
main_game_rect = main_game.get_rect()
main_game_rect.topleft = (0, 0)

# Walls
walls = Walls()

# Ball
ball = Ball(walls.walls_list)
ball_group = pygame.sprite.Group()
ball_group.add(ball)

# Left panel
left_panel = pygame.surface.Surface((300, 900))
left_panel_rect = left_panel.get_rect()
left_panel_rect.topleft = (1600 - 300, 0)

# Editor
editor = Editor(walls, window)
new_wall_position = []

run = True
while run:
    pygame.time.Clock().tick(100)
    for e in pygame.event.get():
        event = e.type
        if event == pygame.QUIT:
            run = False
        if event == pygame.MOUSEBUTTONDOWN:
            if editor.adding_wall:
                new_wall_position = pygame.mouse.get_pos()
        if event == pygame.MOUSEBUTTONUP:
            if editor.adding_wall:
                new_wall_size = (new_wall_position[0] - pygame.mouse.get_pos()[0], new_wall_position[1] - pygame.mouse.get_pos()[1])
                editor.change_new_wall_mode()
                editor.new_wall(new_wall_size, new_wall_position)
            else:
                if not editor.active_editor:
                    ball.speeding(menu, main_game_rect)
                editor.if_clicked_buttons()
                menu.if_clicked_buttons()

    # Show
    pygame.draw.rect(window, (40, 40, 40), main_game_rect)

    ball_group.draw(window)
    ball_group.update()

    for wall in walls.walls_list:
        pygame.draw.rect(window, (0, 0, 0), wall.return_rect())

    pygame.draw.rect(window, (50, 50, 50), left_panel_rect)
    editor.show()

    menu.show()

    pygame.display.update()