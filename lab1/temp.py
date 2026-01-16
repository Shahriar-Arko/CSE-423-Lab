from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

width = 900
height = 900

s_count = 0
catcher_position = 450
catcher_col = [1.0,1.0,1.0]

paused = False
over = False
last_time = time.time()

dmnd_x = random.randint(50,800)
dmnd_y = 825
dmnd_position = [dmnd_x,dmnd_y]
dmnd_col = (random.random(),random.random(),random.random())
dmnd_speed = 2

def zone_detect(x1,y1,x2,y2):
    dx = x2-x1
    dy = y2-y1
    
    if abs(dx) >= abs(dy):
        if dx > 0:
            if dy > 0:
                return 0
            else:
                return 7
        else:
            if dy > 0:
                return 3
            else:
                return 4    
    else:
        if dy > 0:
            if dx > 0:
                return 1
            else:
                return 2
        else:
            if dx > 0:
                return 6
            else:
                return 5
            
            
def convert_zone0(og_zone,x,y):
    if og_zone == 0:
        return x,y
    elif og_zone == 1:
        return y,x
    elif og_zone == 2:
        return -y,x
    elif og_zone == 3:
        return -x,y
    elif og_zone == 4:
        return -x,-y
    elif og_zone == 5:
        return -y,-x
    elif og_zone == 6:
        return y,-x
    elif og_zone == 7:
        return x,-y
    
def back2_ogzone(og_zone,x,y):
    if og_zone == 0:
        return x,y
    elif og_zone == 1:
        return y,x
    elif og_zone == 2:
        return -y,x
    elif og_zone == 3:
        return -x,y
    elif og_zone == 4:
        return -x,-y
    elif og_zone == 5:
        return -y,-x
    elif og_zone == 6:
        return y,-x
    elif og_zone == 7:
        return x,-y                       
    
def midpoint(zone,x1,y1,x2,y2):
    dx = x2-x1
    dy = y2-y1
    
    d = (2*dy) - dx
    incNE = 2*(dy-dx) 
    incE = 2*dy
    x,y =x1,y1
    
    glPointSize(2)
    glBegin(GL_POINTS)
    while x < x2:
        og_x,og_y = back2_ogzone(zone,x,y)
        glVertex2f(og_x,og_y)
        
        if d > 0:
            x += 1
            y += 1    
            d += incNE
        else:
            x += 1
            d += incE
    glEnd()        

def eightway_symmetry(x1,y1,x2,y2):
    zone = zone_detect(x1,y1,x2,y2)
    conv_x1,conv_y1 = convert_zone0(zone,x1,y1) 
    conv_x2,conv_y2 = convert_zone0(zone,x2,y2)
    midpoint(zone,conv_x1,conv_y1,conv_x2,conv_y2)

def left_arrow():
    
    glColor3f(0.0, 1.0, 1.0)  
    eightway_symmetry(50, 850, 100, 850)  # Horizontal line
    eightway_symmetry(50, 850, 75, 875)   # Upper diagonal
    eightway_symmetry(50, 850, 75, 825)   # Lower diagonal

def cross():
    
    glColor3f(1.0, 0.0, 0.0)  
    eightway_symmetry(800, 875, 850, 825)  
    eightway_symmetry(800, 825, 850, 875)  
                                   
def play_pause_button():
    glColor3f(1.0, 1.0, 0.0)  
    
    if paused:
    
        eightway_symmetry(435, 850, 435, 800)  # Left side
        eightway_symmetry(435, 850, 475, 825)  # Top diagonal
        eightway_symmetry(435, 800, 475, 825)  # Bottom diagonal
    else:
        
        eightway_symmetry(440, 850, 440, 800)  # Left line
        eightway_symmetry(460, 850, 460, 800)  # Right line        
   
def diamonds(x,y,colors):
    val = 25        
    glColor3f(colors[0],colors[1],colors[2])
    eightway_symmetry(x,y+val,x+val,y)
    eightway_symmetry(x+val,y,x,y-val)
    eightway_symmetry(x,y-val,x-val,y)
    eightway_symmetry(x-val,y,x,y+val)
    
def catcher():
    global catcher_position, catcher_col
    length = 250
    height = 50
    halflen = length // 2
    
    x1 = catcher_position - halflen  # Left edge of top
    x4 = catcher_position + halflen  # Right edge of top
    
   
    x2 = x1 + 60  # Left inside bottom 
    x3 = x4 - 60  # Right inside bottom 
    
    y1 = 10       # Bottom 
    y2 = y1 + height  # Top 

    glColor3f(catcher_col[0], catcher_col[1], catcher_col[2])

    eightway_symmetry(x2, y1, x3, y1)  # Bottom line 
    eightway_symmetry(x1, y2, x4, y2)  # Top line 
    eightway_symmetry(x1, y2, x2, y1)  # Left diagonal
    eightway_symmetry(x3, y1, x4, y2)  # Right diagonal
 

def cillision_checker():
    global dmnd_position, s_count, dmnd_col, dmnd_speed, over, catcher_position, catcher_col
    dmnd_box = (dmnd_position[0] - 25, dmnd_position[1] - 25, 50, 50)
    
    catcher_box = (catcher_position - 125, 10, 250, 50)  
    
    
    collision = (dmnd_box[0] < catcher_box[0] + catcher_box[2] and
                dmnd_box[0] + dmnd_box[2] > catcher_box[0] and
                dmnd_box[1] < catcher_box[1] + catcher_box[3] and
                dmnd_box[1] + dmnd_box[3] > catcher_box[1])
    
    
    if collision:
        s_count += 1
        print(f"Score: {s_count}")
        dmnd_position[0] = random.randint(50, 800)
        dmnd_position[1] = 825      
        dmnd_col = (random.random(), random.random(), random.random())
        dmnd_speed = 2 + (s_count * 0.5)
        
        return True
    
    
    if dmnd_position[1] < 0 and not over:
        over = True
        catcher_col[0] = 1.0  
        catcher_col[1] = 0.0
        catcher_col[2] = 0.0
        print(f"Game Over! Score: {s_count}")
    
    return False

def update(value):
    global paused, dmnd_position, dmnd_speed, last_time, over
    
    if not paused and not over:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Move diamond down with time-based movement
        dmnd_position[1] -= dmnd_speed * delta_time * 100

        cillision_checker()
    else:
        # maintain smooth transition from pause to restart
        last_time = time.time()
                    
    glutTimerFunc(16, update, 0)  
    glutPostRedisplay()
    
    
def mouseListener(button, state, x, y):
    global paused, catcher_position, s_count, over, dmnd_position, dmnd_col, dmnd_speed, catcher_col
    new_y = height - y  

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Pause/play button 
        if 435 <= x <= 475 and 800 <= new_y <= 850:
            paused = not paused
            if paused:
                pass
                
        # Exit button 
        if 800 <= x <= 850 and 825 <= new_y <= 875:
            print(f"Goodbye! Score: {s_count}")
            glutLeaveMainLoop()

        # Restart button 
        if 50 <= x <= 100 and 825 <= new_y <= 875:
            catcher_position = 450  
            catcher_col = [1.0, 1.0, 1.0]  
            over = False 
            paused = False  
            s_count = 0  
            dmnd_position[0] = random.randint(50, 800)  
            dmnd_position[1] = 825 
            dmnd_col = (random.random(), random.random(), random.random())  
            dmnd_speed = 2  
            print("Starting Over!")

    glutPostRedisplay()  
    
def KeyListener(key, x, y):
    global catcher_position
    speed = 25    
    if not over and not paused:
        if key == GLUT_KEY_RIGHT and catcher_position < 750:
            catcher_position += speed 
        elif key == GLUT_KEY_LEFT and catcher_position > 125:
             catcher_position -= speed   
             
    glutPostRedisplay()         
    
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    left_arrow()
    cross()
    play_pause_button()
    diamonds(dmnd_position[0], dmnd_position[1], dmnd_col)
    catcher()
    #glFlush()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Catch the Diamonds!")
glClearColor(0.0, 0.0, 0.0, 1.0)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, width, 0, height)
glMatrixMode(GL_MODELVIEW)
glutDisplayFunc(display)
glutMouseFunc(mouseListener)
glutSpecialFunc(KeyListener)
glutTimerFunc(0, update, 0)
glutMainLoop()