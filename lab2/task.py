import OpenGL
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import random
import numpy as np
import time as timer
game_width = 1200
game_height = 900

score = 0
catcher_x = 600
catcher_color = [1.0, 1.0, 1.0]

is_paused = False
game_over = False
prev_time = timer.time()

class Diamond:
    def __init__(self):
        self.x = np.random.randint(50, 800)
        self.y = np.random.randint(900, 1000)
        self.color = (np.random.random(), np.random.random(), np.random.random())
        self.speed = 2

current_diamond = Diamond()

def zone_detection_function(x1, y1, x2, y2):
    delta_x_value = x2 - x1
    delta_y_value = y2 - y1
    
    return zone_detection_condition(delta_x_value, delta_y_value)
  
def zone_detection_condition(delta_x_value, delta_y_value):
    delta_x_bigger_val = abs(delta_x_value) >= abs(delta_y_value)

    if delta_x_bigger_val: #deltax value boro
        if delta_x_value > 0 and delta_y_value > 0:
            return 0
        elif delta_x_value > 0 and delta_y_value <= 0:
            return 7
        elif delta_x_value < 0 and delta_y_value > 0:
            return 3
        else:
            return 4
    else: #deltay value boro
        if delta_y_value > 0 and delta_x_value > 0:
            return 1
        elif delta_y_value > 0 and delta_x_value <= 0:
            return 2
        elif delta_y_value < 0 and delta_x_value > 0:
            return 6
        else:
            return 5
                
def tranforme_to_zone(zone, x, y):
    transformations = {
        0: (x, y),
        1: (y, x),
        2: (-y, x),
        3: (-x, y),
        4: (-x, -y),
        5: (-y, -x),
        6: (y, -x),
        7: (x, -y)
    }
    return transformations[zone]
    
def eight_way_symmetry_conversion(zone, x, y):
    return tranforme_to_zone(zone, x, y)

def midpoint_algorithm_funciton(zone, x1, y1, x2, y2):
    delta_x_value = x2 - x1
    delta_y_value = y2 - y1
    
    decision_value = (2 * delta_y_value) - delta_x_value
    increase_NE_value = 2 * (delta_y_value - delta_x_value) 
    increase_E_value = 2 * delta_y_value
    x, y = x1, y1
    gl.glPointSize(2)
    gl.glBegin(gl.GL_POINTS)
    midpoint_algorithm_condition(x, y, zone, x1, x2, decision_value, increase_NE_value, increase_E_value) #condition call
    gl.glEnd()  


def midpoint_algorithm_condition(x, y, zone, x1, x2, decision_value, increase_NE_value, increase_E_value):
    for i in range(x1,x2):
        original_x, original_y = eight_way_symmetry_conversion(zone, x, y)
        gl.glVertex2f(original_x, original_y)
        
        if decision_value > 0:
            x += 1
            y += 1    
            decision_value += increase_NE_value
        else:
            x += 1
            decision_value += increase_E_value
    

def render_line(x1, y1, x2, y2):
    zone = zone_detection_function(x1, y1, x2, y2)
    new_x1, new_y1 = tranforme_to_zone(zone, x1, y1) 
    new_x2, new_y2 = tranforme_to_zone(zone, x2, y2)
    midpoint_algorithm_funciton(zone, new_x1, new_y1, new_x2, new_y2)

def draw_restart_icon():
    gl.glColor3f(0.0, 1.0, 1.0)

    base_x = 50
    base_y = game_height - 50 

    render_line(base_x, base_y, base_x + 50, base_y)        
    render_line(base_x, base_y, base_x + 25, base_y + 25)    
    render_line(base_x, base_y, base_x + 25, base_y - 25)     

def draw_exit_icon():
    gl.glColor3f(1.0, 0.0, 0.0)
    base_x = game_width - 100   
    base_y = game_height - 75   
    size = 50

    # Draw x icon
    render_line(base_x, base_y + size, base_x + size, base_y)
    render_line(base_x, base_y, base_x + size, base_y + size)
                                   
def draw_play_pause():
    gl.glColor3f(1.0, 1.0, 0.0)  
    
    if is_paused:
        render_line(580, 850, 580, 800)
        render_line(580, 850, 620, 825)
        render_line(580, 800, 620, 825)
    else:
        render_line(585, 850, 585, 800)
        render_line(605, 850, 605, 800)
     
   
def draw_diamond(x, y, colors):
    size = 25        
    gl.glColor3f(*colors)
    render_line(x, y+size, x+size, y)
    render_line(x+size, y, x, y-size)
    render_line(x, y-size, x-size, y)
    render_line(x-size, y, x, y+size)
    
def catcher_drawing_function():
    global catcher_x, catcher_color
    length = 250
    height = 50
    half_length = length // 2
    
    left_top = catcher_x - half_length
    right_top = catcher_x + half_length
    
    left_bottom = left_top + 60
    right_bottom = right_top - 60
    
    bottom_y = 10
    top_y = bottom_y + height

    gl.glColor3f(*catcher_color)

    render_line(left_bottom, bottom_y, right_bottom, bottom_y)
    render_line(left_top, top_y, right_top, top_y)
    render_line(left_top, top_y, left_bottom, bottom_y)
    render_line(right_bottom, bottom_y, right_top, top_y)
 

def check_collision():
    global current_diamond, score, game_over, catcher_x, catcher_color
    diamond_box = (current_diamond.x - 25, current_diamond.y - 25, 50, 50)
    catcher_box = (catcher_x - 125, 10, 250, 50)  
    
    colliding = (diamond_box[0] < catcher_box[0] + catcher_box[2] and
                diamond_box[0] + diamond_box[2] > catcher_box[0] and
                diamond_box[1] < catcher_box[1] + catcher_box[3] and
                diamond_box[1] + diamond_box[3] > catcher_box[1])
    return collision_condition(colliding)

def collision_condition(colliding):
    global current_diamond, score, game_over, catcher_x, catcher_color
        
    if colliding:
        score += 1
        print(f"Score: {score}")
        current_diamond = Diamond()
        current_diamond.speed = 2 + (score * 0.5)
        return True
    
    if current_diamond.y < 0 and not game_over:
        game_over = True
        catcher_color = [1.0, 0.0, 0.0]
        print(f"Game Over! Score: {score}")
    
    return False


def game_update(value):
    global is_paused, prev_time, game_over
    
    if not is_paused and not game_over:
        now = timer.time()
        time_elapsed = now - prev_time
        prev_time = now
        
        current_diamond.y -= current_diamond.speed * time_elapsed * 100

        check_collision()
                    
    glut.glutIdleFunc(16, game_update, 0)  
    glut.glutPostRedisplay()
    
    
def handle_mouse(button, state, x, y):
    global is_paused, catcher_x, score, game_over, current_diamond, catcher_color
    y = game_height - y 

    if button == glut.GLUT_LEFT_BUTTON and state == glut.GLUT_DOWN:

        if 580 <= x <= 620 and 850 <= y <= 900:
            is_paused = not is_paused
            # print(is_paused)

        elif 1100 <= x <= 1150 and 850 <= y <= 900:
            print(f"Goodbye! Score: {score}")
            glut.glutLeaveMainLoop()

        elif 50 <= x <= 100 and 850 <= y <= 900:
            catcher_x = 450
            catcher_color = [1.0, 1.0, 1.0]
            game_over = False
            is_paused = False
            score = 0
            current_diamond = Diamond()
            print("Starting Over!")

    glut.glutPostRedisplay()

    
def handle_keys(key, x, y):
    global catcher_x
    move_speed = 30
    if not game_over and not is_paused:
        if key == glut.GLUT_KEY_RIGHT and catcher_x < 750:
            catcher_x += move_speed 
        elif key == glut.GLUT_KEY_LEFT and catcher_x > 125:
             catcher_x -= move_speed   
             
    glut.glutPostRedisplay()         
    
def render():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glLoadIdentity()
    draw_restart_icon()
    draw_exit_icon()
    draw_play_pause()
    draw_diamond(current_diamond.x, current_diamond.y, current_diamond.color)
    catcher_drawing_function()
    glut.glutSwapBuffers()
def game_update():
    global is_paused, prev_time, game_over

    if not is_paused and not game_over:
        now = timer.time()
        time_elapsed = now - prev_time
        prev_time = now

        current_diamond.y -= current_diamond.speed * time_elapsed * 100

        check_collision()

    glut.glutPostRedisplay()
    
def main():
    glut.glutInit()
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
    glut.glutInitWindowSize(game_width, game_height)
    glut.glutInitWindowPosition(450, 100)
    glut.glutCreateWindow(b"diamond_catcher_game")
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, game_width, 0, game_height)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    glut.glutDisplayFunc(render)
    glut.glutMouseFunc(handle_mouse)
    glut.glutSpecialFunc(handle_keys)
    glut.glutIdleFunc(game_update)
    glut.glutMainLoop()

if __name__ == "__main__":
    main()
