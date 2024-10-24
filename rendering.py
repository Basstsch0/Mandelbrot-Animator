import numba as nb
import pygame
import sys
import numpy as np
import math
import os
import time 
import easygui
from mandelbrot import *

pygame.init()
width, height = 1000, 1000

pygame.font.init()
font_size = 18
font = pygame.font.SysFont('Arial', font_size)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mandelbrot Set")

# white color 
color = (255,255,255) 
  
# light shade of the button 
color_light = (170,170,170) 
  
# dark shade of the button 
color_dark = (100,100,100) 

text = font.render('Create zoom anmiation at this point' , True , color) 
text2 = font.render('Play zoom animation' , True , color)

# Initial parameters
zoom = 1
offset_x = -2.5
offset_y = -1.5
old_zoom = 1

# Convert the values array to a pygame surface
values = mandelbrot(width, height, zoom, offset_x, offset_y)
mandelbrot_surface = pygame.surfarray.make_surface(np.transpose(values, (1, 0, 2)))


animation_dir = ""
animation_files = 0
old_mouse_x = 0
old_mouse_y = 0
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            old_zoom = zoom
            if event.button == 4:  # zoom in
                old_mouse_x = mouse_x
                old_mouse_y = mouse_y
                zoom *= 2
                
            elif event.button == 5:  # zoom out
                zoom /= 2

            elif button_x <= mouse[0] <= button_x + button_width and button_y <= mouse[1] <= button_y + button_height:  # button pressed
                point_x = offset_x + (mouse_x/width) * 3/zoom
                point_y = offset_y + (mouse_y/height) * 3/zoom

                distance_x = point_x + 2.5
                distance_y =point_y - 0.5

                original_mouse_position_x = distance_x/3 * width
                original_mouse_position_y = distance_y/3 * height
                create_animation(point_x, point_y, 60, 10, 1.01, width, height)
                print("pressed")

            elif button2_x <= mouse[0] <= button2_x + button2_width and button2_y <= mouse[1] <= button2_y + button2_height: 
                path = easygui.fileopenbox()
                # animation_dir = os.path.dirname(path)
                # animation_files = os.listdir(dir)
                if(path):
                    show_animation(path, 40)

            
            if(zoom != old_zoom):
                offset_x = calculate_offset(zoom=zoom, old_zoom=old_zoom, offset_old=offset_x, mouse=mouse_x, total=width)
                offset_y = calculate_offset(zoom=zoom, old_zoom=old_zoom, offset_old=offset_y, mouse=mouse_y, total=height)
                values = mandelbrot(width, height, zoom, offset_x, offset_y)
                mandelbrot_surface = pygame.surfarray.make_surface(np.transpose(values, (1, 0, 2)))

    mouse = pygame.mouse.get_pos() 

    # Update the display
    screen.fill((0, 0, 0))
    screen.blit(mandelbrot_surface, (0, 0))
    text1_surface = font.render('Zoom: {:.1f}'.format(zoom), True, (255, 255, 255))
    text2_surface = font.render('Coordinates: ({:.2f}, {:.2f})'.format(offset_x+ 1.5/zoom, offset_y + 1.5/zoom), True, (255, 255, 255))

    rect_width = max(text1_surface.get_width(), text2_surface.get_width()) + 20
    rect_height = 2 * font_size + 20  # For two lines of text and padding
    rect_x = 10  # Distance from the left screen edge
    rect_y = height - rect_height - 10  # Distance from the bottom screen edge

    # Draw a dark rectangle at the bottom left of the screen
    info_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, (50, 50, 50), info_rect)  # Change the rectangle color if needed

    # if mouse is hovered on a button it 
    # changes to lighter shade 
    button_width = text.get_width() + 20
    button_height = 2* font_size + 10
    button_x = rect_x + rect_width + 20
    button_y = rect_y
    info_rect = pygame.Rect(button_x, button_y,button_width, button_height)
    if button_x <= mouse[0] <= button_x + button_width and button_y <= mouse[1] <= button_y + button_height: 
        pygame.draw.rect(screen,color_light,info_rect) 

    else: 
        pygame.draw.rect(screen,color_dark,info_rect) 

    button2_width = text2.get_width() + 20
    button2_height = 2* font_size + 10
    button2_x = button_x + button_width + 20
    button2_y = rect_y
    info_rect = pygame.Rect(button2_x, button2_y,button2_width, button2_height)
    if button2_x <= mouse[0] <= button2_x + button2_width and button2_y <= mouse[1] <= button2_y + button2_height: 
        pygame.draw.rect(screen,color_light,info_rect) 

    else: 
        pygame.draw.rect(screen,color_dark,info_rect) 
      
    # Blit the text onto the screen
    screen.blit(text , (button_x + 10 , button_y + 10) )
    screen.blit(text2 , (button2_x + 10 , button2_y + 10) )
    screen.blit(text1_surface, (rect_x + 10, rect_y + 5))
    screen.blit(text2_surface, (rect_x + 10, rect_y + 5 + font_size + 5))
    pygame.display.flip()


# Quit pygame
pygame.quit()
sys.exit()