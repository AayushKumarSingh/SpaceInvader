import pygame
import os
import asyncio


def gradient_maker():
    with open(r"color_temp.txt", "w") as file:
        for i in range(1080):
            for j in range(720):
                file.write(f"{i} {j}\n")


def use_gradient():
    global screen
    with open(r"color_temp.txt", "r") as file:
        lt = list()
        while True:
            try:
                x = list(map(int, file.readline().split()))
                if not x:
                    break
                lt.append(x)
            except ValueError:
                break
        for color in lt:
            screen.set_at((color[0], color[1]), (color[1] / 5, color[1] / 5, color[0] / 5))


def play_clicked():
    pos = play_des.x <= mouse[0] < play_des.x + play_des.w and play_des.y <= mouse[1] < play_des.y + play_des.h
    return pos and (pygame.mouse.get_pressed(5)[0] is True)


def setting_clicked():
    pos = setting_des.x <= mouse[0] < setting_des.x + setting_des.w and setting_des.y <= mouse[
        1] < setting_des.y + setting_des.h
    return pos and (pygame.mouse.get_pressed(5)[0] is True)


def quit_clicked():
    pos = quit_des.x <= mouse[0] < quit_des.x + quit_des.w and quit_des.y <= mouse[1] < quit_des.y + quit_des.h
    return pos and (pygame.mouse.get_pressed(5)[0] is True)


pygame.init()
pygame.mouse.set_cursor(pygame.cursors.tri_left)
screen = pygame.display.set_mode((1080, 720), pygame.NOFRAME, 2, 0)
screen.fill((0, 100, 128))
# use_gradient()


font_size = 70
text_style = pygame.font.SysFont("seogui", font_size, italic=True, bold=True)
text_color = (250, 0, 0)
# text_bg_color = (0, 0, 0)

play_button = text_style.render("Play", True, text_color)
play_des = play_button.get_rect()
play_des.x, play_des.y = (0.45 * 1080, 0.2 * 720)

setting_button = text_style.render("Settings", True, text_color)
setting_des = setting_button.get_rect()
setting_des.x, setting_des.y = (0.42 * 1080, 0.4 * 720)


quit_button = text_style.render("Quit", True, text_color)
quit_des = quit_button.get_rect()
quit_des.x, quit_des.y = (0.45 * 1080, 0.6 * 720)

while True:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    if play_clicked():
        os.system(r"python .\game.pyw")

    if setting_clicked():
        os.system(r"notepad .\config.json")

    if quit_clicked():
        exit("Program exited using main menu")

    screen.blits(blit_sequence=[(play_button, play_des), (setting_button, setting_des), (quit_button, quit_des)])
    pygame.display.update()
