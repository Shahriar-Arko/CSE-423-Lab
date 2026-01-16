import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import random

rain_drop_speed_list= []
raindrop_direction_change_counter= 0.0

def roof_shape_function():
    GL.glColor3f(0.5, 0.3, 0.7)
    GL.glBegin(GL.GL_TRIANGLES)
    GL.glVertex2f(300, 380)
    GL.glVertex2f(420, 420)
    GL.glVertex2f(540, 380)
    GL.glEnd()
def body_shape_creating_funciton():
    GL.glColor3f(0.8, 0.6, 0.4)
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex2f(320, 260) #bottom-left
    GL.glVertex2f(520, 260) #bottom-right
    GL.glVertex2f(520, 380) #top-right
    GL.glVertex2f(320, 380) #top-left
    GL.glEnd()



def door_shape_function():
    
    door_base_shape()

    door_cross_design_funciton()

    # Door lock
    GL.glColor3f(0.4, 0.7, 0.7)
    GL.glPointSize(4)
    GL.glBegin(GL.GL_POINTS)
    GL.glVertex2f(496, 288)
    GL.glEnd()
def door_cross_design_funciton():
     # Cross Design
    GL.glLineWidth(1.5)
    GL.glColor3f(1.0, 1.0, 1.0)
    GL.glBegin(GL.GL_LINES)

    # Vertical line
    GL.glVertex2f(480, 260)
    GL.glVertex2f(480, 330)

    # Horizontal line
    GL.glVertex2f(460, 295)
    GL.glVertex2f(500, 295)
    GL.glEnd()

def door_base_shape():
    GL.glColor3f(0.4, 0.2, 0.0) 
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex2f(460, 260)
    GL.glVertex2f(460, 330)
    GL.glVertex2f(500, 330)
    GL.glVertex2f(500, 260)
    GL.glEnd()

def left_window_shape_funciton(): 
    GL.glColor3f(0.0, 0.5, 0.8) 
    GL.glBegin(GL.GL_TRIANGLES)
    GL.glVertex2f(340, 320)
    GL.glVertex2f(340, 360)
    GL.glVertex2f(380, 320)
    GL.glVertex2f(340, 360)
    GL.glVertex2f(380, 360)
    GL.glVertex2f(380, 320)
    GL.glEnd()

def window_cross_shape_funciton(): 
    GL.glLineWidth(1)
    GL.glColor3f(1.0, 1.0, 1.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2f(340, 340)
    GL.glVertex2f(380, 340)
    GL.glVertex2f(360, 320)
    GL.glVertex2f(360, 360)
    GL.glEnd()

def doow_window_color_function():
    GL.glColor3f(0.6, 0.8, 0.95)

def ground_coordinate_shape_funciton():
    GL.glColor3f(0.45, 0.6, 0.36)
    GL.glBegin(GL.GL_TRIANGLES)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(0, 300)        
    GL.glVertex2f(800, 0)
    GL.glVertex2f(0, 300)
    GL.glVertex2f(800, 0)
    GL.glVertex2f(800, 300)
    GL.glEnd()


def rain_drop_shape(x1, y1):
    GL.glLineWidth(2.5)
    GL.glColor3f(0.5, 0.6, 1.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2f(x1, y1)
    GL.glVertex2f(x1, y1-15)
    GL.glEnd()

def tree_shape_draw_function():
    tree_positions_list = [20, 110, 200, 300, 400, 500, 600, 700]  

    i = 0
    while i < len(tree_positions_list):
        base_x_coordinate = tree_positions_list[i]

        GL.glColor3f(0.55, 0.27, 0.07)  
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(base_x_coordinate + 15, 300)
        GL.glVertex2f(base_x_coordinate + 15, 340)
        GL.glVertex2f(base_x_coordinate + 35, 340)
        GL.glVertex2f(base_x_coordinate + 35, 300)
        GL.glEnd()

        GL.glColor3f(0.0, 0.6, 0.0)  # Green
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glVertex2f(base_x_coordinate, 340)
        GL.glVertex2f(base_x_coordinate + 25, 380)
        GL.glVertex2f(base_x_coordinate + 50, 340)

        GL.glVertex2f(base_x_coordinate + 5, 360)
        GL.glVertex2f(base_x_coordinate + 25, 400)
        GL.glVertex2f(base_x_coordinate + 45, 360)

        GL.glVertex2f(base_x_coordinate + 10, 380)
        GL.glVertex2f(base_x_coordinate + 25, 420)
        GL.glVertex2f(base_x_coordinate + 40, 380)
        GL.glEnd()

        i += 1



background_col_red_effect=0.0
background_col_green_effect=0.0
background_col_blue_effect= 0.0


def keyboard_key_bind(key_bind, x, y):
    light_dark_condition(key_bind)
    GLUT.glutPostRedisplay() #refresh the display after key press


def light_dark_condition(key_bind):
    global background_col_red_effect, background_col_green_effect, background_col_blue_effect
    if key_bind == b'l':
        if background_col_blue_effect< 1:
            background_col_red_effect += .08
            background_col_green_effect += .08
            background_col_blue_effect+= .08
    elif key_bind == b'n':
        if background_col_blue_effect>= 0.0:
            background_col_red_effect -= .08
            background_col_green_effect -= .08
            background_col_blue_effect-= .08
    

def raindrop_direction_change_funciton(arrow_key_bind, x, y):
    direction_change_condition(arrow_key_bind)
    rain_drop_speed_check(arrow_key_bind)
    GLUT.glutPostRedisplay()

def direction_change_condition(arrow_key_bind):
    global raindrop_direction_change_counter
    if arrow_key_bind == GLUT.GLUT_KEY_LEFT:
        raindrop_direction_change_counter=max(raindrop_direction_change_counter - 0.5, -2.5)
        print("Raindrop direction change to left detected")
    elif arrow_key_bind == GLUT.GLUT_KEY_RIGHT:
        raindrop_direction_change_counter=min(raindrop_direction_change_counter + 0.5, 2.5)
        print("Raindrop direction change to right detected")

raindrop_fall_speed_multiplier = 10.0

def rain_drop_speed_check(arrow_key_bind):
    global raindrop_fall_speed_multiplier

    if arrow_key_bind == GLUT.GLUT_KEY_UP:
        raindrop_fall_speed_multiplier=min(raindrop_fall_speed_multiplier + .2, 5.0)
        print(f"Speed up detected")

    elif arrow_key_bind == GLUT.GLUT_KEY_DOWN:
        raindrop_fall_speed_multiplier=max(raindrop_fall_speed_multiplier - 0.2, 0.2)
        print(f"Speed down detected")


def update_raindrop_position_function(x, y):
    
    return update_raindrop_condition(x,y)
   

def update_raindrop_condition(x,y):
    y -= random.uniform(1, 5)
    if y < 0:
        x = random.uniform(0, 1200)
        y = random.uniform(0, 900)

    x += raindrop_direction_change_counter
    x = max(0, min(x, 800))  
    return x, y

def raindrop_animation_display():
    global rain_drop_speed_list
    updated_raindrops_list = []
    raindrop_display_loop(updated_raindrops_list)
    rain_drop_speed_list=updated_raindrops_list
    GLUT.glutPostRedisplay() #refresh the display after key press

def raindrop_display_loop(updated_raindrops_list):
    for x, y in rain_drop_speed_list:
        new_x_axis_coordinate, new_y_axis_coordinate = update_raindrop_position_function(x, y) #new x,y coordinates
        updated_raindrops_list.append((new_x_axis_coordinate, new_y_axis_coordinate)) #append the new coordinates to the updated list
    return updated_raindrops_list

def projoectionmodelview():
    GL.glViewport(0, 0, 800, 600)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(0.0, 780, 0.0, 600, 0.0, 1.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

def show_output_animation_function():
    GL.glClearColor(background_col_red_effect, background_col_green_effect, background_col_blue_effect, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity() #Resets the transformations so we can draw fresh
    projoectionmodelview()
    ground_coordinate_shape_funciton()   
    tree_shape_draw_function()    
    roof_shape_function()
    body_shape_creating_funciton()        
    doow_window_color_function()
    door_shape_function()
    left_window_shape_funciton()
    window_cross_shape_funciton()
    
    for i in rain_drop_speed_list:
        rain_drop_shape(i[0], i[1])
    GLUT.glutSwapBuffers()

def glut_calling_funcitons():
    GLUT.glutInit() 
    GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA) #calling the display mode
    GLUT.glutInitWindowSize(800, 600) #calling the window size
    GLUT.glutInitWindowPosition(500,350) #calling the window position
    window_name=GLUT.glutCreateWindow(b"Lab 1: Rain Animation & Building")
    GLUT.glutDisplayFunc(show_output_animation_function)
    GLUT.glutIdleFunc(raindrop_animation_display) #calling the raindrop animation function
    GLUT.glutKeyboardFunc(keyboard_key_bind) #calling the keyboard key bind function
    GLUT.glutSpecialFunc(raindrop_direction_change_funciton)
    

glut_calling_funcitons()

for j in range(200):  # Generate 200 raindrops
    x_axis_random_value = random.uniform(0, 1200)
    y_axis_random_value = random.uniform(0, 800)
    rain_drop_speed_list.append((x_axis_random_value, y_axis_random_value))

GLUT.glutMainLoop()


