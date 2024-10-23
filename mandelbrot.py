import numba as nb
import pygame
import sys
import numpy as np
import math
import os
import time 

gradient = np.array([
    [153, 50, 204],  # Dark Orchid
    [255, 165, 0],   # Orange
    [138, 43, 226],  # Blue Violet (repeated for a smoother gradient)
    [138, 43, 226],  # Blue Violet
    [147, 112, 219], # Medium Purple
    [148, 0, 211],   # Dark Violet (repeated for a smoother gradient)
    [75, 0, 130],    # Indigo
    [148, 0, 211],   # Dark Violet
    [0, 0, 255],     # Blue
    [0, 0, 205],     # Medium Blue
    [0, 255, 0],     # Green
    [128, 0, 128],   # Purple
    [65, 105, 225],  # Royal Blue
    [0, 255, 255],   # Cyan
    [255, 0, 0],     # Red
    [0, 255, 127],   # Spring Green
    [124, 252, 0],   # Lawn Green
    [127, 255, 0],   # Chartreuse
    [173, 255, 47],  # Green Yellow
    [255, 215, 0],   # Gold
    [255, 69, 0],    # Red Orange
    [160, 32, 240],  # Purple
    [255, 255, 0],   # Yellow
    [255, 140, 0],   # Dark Orange
], dtype=np.int64)
    

@nb.njit
def rgb_value(value, max_value, index_rgb, minval, maxval):
    # val = value % max_value 
    range = maxval - minval
    val = value - minval
    segment_length = range / (len(gradient) - 1)
    segment_index = min(int((val) // segment_length), len(gradient) - 2)
    segment_position = ((val) % segment_length) / segment_length
    
    start_color, end_color = gradient[segment_index], gradient[segment_index + 1]
    
    color_val = int(start_color[index_rgb] + (end_color[index_rgb] - start_color[index_rgb]) * segment_position)
    
    return color_val

@nb.njit
def value_to_r(value, max_value, min, max):
    return rgb_value(value, max_value, 0, min, max)

@nb.njit
def value_to_g(value, max_value, min, max):
    return rgb_value(value, max_value, 1, min, max)


@nb.njit
def value_to_b(value, max_value, min, max):
    return rgb_value(value, max_value, 2, min, max)

@nb.njit
def log_base(x, base):
    return math.log(x) / math.log(base)


@nb.njit(parallel=True)
def mandelbrot(width, height, zoom, offset_x, offset_y):
    max_iterations = int(350 +  zoom/2)#  log_base(float(zoom), 1))
    values = np.zeros((height, width, 3), dtype=np.uint64)
    max = 0
    
    for y in nb.prange(height):
        for x in range(width):
            c_real = (x / width) * 3 / zoom + offset_x
            c_imag = (y / height) * 3 / zoom + offset_y
            x_real = 0
            x_imag = 0
            iterations = 0
            
            while x_real * x_real + x_imag * x_imag <= 4 and iterations < max_iterations:
                x_temp = x_real * x_real - x_imag * x_imag + c_real
                x_imag = 2 * x_real * x_imag + c_imag
                x_real = x_temp
                iterations += 1 
            
            if(iterations > max and iterations < max_iterations):
                max = iterations
                print(f"{iterations} and {max}" )
                

            values[y, x] = (iterations,iterations,iterations)
    print(max)

    minval = np.min(values)
    print(minval)
    maxval = max
    print(maxval)
    for y in nb.prange(height):
        for x in range(width):   
            iterations = values [y,x,1]
            # if iterations > 200:
                # print(iterations)
            if iterations < max_iterations:
                r = value_to_r(iterations, max_iterations, minval, maxval)
                g = value_to_g(iterations, max_iterations, minval, maxval)
                b = value_to_b(iterations, max_iterations, minval, maxval)
                values[y, x] = (r, g, b)
            else:
                values[y, x] = (0, 0, 0) 
    
    return values


def calculate_offset(zoom, offset_old, old_zoom, mouse, total):
    point = offset_old + (mouse/total) * 3/old_zoom
    # old zooming strategy with cursor as new middle 
    # middle= offset_old + 1.5/old_zoom
    # distance = (middle - point) / zoom
    # offset = point + distance - 1.5/zoom

    # new zooming strategy with cursor = zoomed cursor
    offset = point - (mouse/total) * 3/zoom

    return offset

def create_animation(x, y, depth, fps, zoom_factor, width, height,iterations_init=100,  iterations_factor = 0.5):
    output_dir = f"{x}_{y}_{depth}"
    path = os.path.dirname(os.path.realpath(__file__))+ "\\animations\\" + output_dir
    os.makedirs(path, exist_ok=True)
    print("path:"+path)
    print(x)
    print(y)
    distance_x = x + 2.5
    distance_y =y - 0.5
    original_mouse_position_x = distance_x/3 * width
    original_mouse_position_y = distance_y/3 * height
    zoom = 1
    offset_x = -2.5 - (-1 - x)
    offset_y = -1.5 + y
    print(offset_x)
    print(offset_y)
    for i in range(depth * fps):
        print(i)
        old_zoom = zoom
        zoom *= zoom_factor
        offset_x = calculate_offset(zoom=zoom, old_zoom=old_zoom, offset_old=offset_x, mouse=width/2, total=width)
        offset_y = calculate_offset(zoom=zoom, old_zoom=old_zoom, offset_old=offset_y, mouse=height/2, total=height)
        values = mandelbrot(width, height, zoom, offset_x, offset_y)
        filename = os.path.join(path, f"mandelbrot_{i}.npy")
        np.save(filename, values)
        if i % 10 == 0:
            mandelbrot_surface = pygame.surfarray.make_surface(np.transpose(values, (1, 0, 2)))
            screen.blit(mandelbrot_surface, (0, 0))
            pygame.display.flip()

def show_animation(path, fps):
    dir = os.path.dirname(path)
    for i in range(len(os.listdir(dir))):
        time.sleep(1/fps)
        values = np.load(dir+f"\\mandelbrot_{i}.npy")
        print(f"\\mandelbrot_{i}.npy")
        mandelbrot_surface = pygame.surfarray.make_surface(np.transpose(values, (1, 0, 2)))
        screen.blit(mandelbrot_surface, (0, 0))
        pygame.display.flip()

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
                create_animation(point_x, point_y, 50, 6, 1.03, width, height)
                print("pressed")

            elif button2_x <= mouse[0] <= button2_x + button2_width and button2_y <= mouse[1] <= button2_y + button2_height: 
                path = easygui.fileopenbox()
                # animation_dir = os.path.dirname(path)
                # animation_files = os.listdir(dir)
                show_animation(path, 24)

            
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