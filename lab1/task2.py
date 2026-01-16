import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import random
import time

class BouncingPointsSimulatorgame:
    def __init__(self):
        self.width, self.height = 1200, 800
        self.point_entities_list = []
        self.points_movement_rate = 0.1
        self.simulation_active_mode = True
        self.point_blink_mode = False
        self.points_blink_toogle = False
        self.last_blink_time = 0
        
    def initialize_window(self):
        glut.glutInit()
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
        glut.glutInitWindowSize(self.width, self.height)
        glut.glutCreateWindow(b"Bouncing Points game")
        gl.glClearColor(0.1, 0.0, 0.2, 1.0)
        
    def setup_event_handlers(self):
        glut.glutDisplayFunc(self.draw_points_output)
        glut.glutIdleFunc(self.draw_points_output)
        glut.glutMouseFunc(self.mouse_click_process_function)
        glut.glutKeyboardFunc(self.handle_key_presses)
        glut.glutSpecialFunc(self.handle_special_keybinds)
        
    def configure_projection_function(self):
        gl.glViewport(0, 0, self.width, self.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluOrtho2D(0, self.width, 0, self.height) 
        gl.glMatrixMode(gl.GL_MODELVIEW)
        
    def create_new_point(self, x, y): #right mouse click korle function call hobe
        direction_x = random.choice([-1, 1]) * random.uniform(0.3, 0.7) 
        direction_y = random.choice([-1, 1]) * random.uniform(0.3, 0.7)
        color = (random.random(), random.random(), random.random()) 
        
        new_point = {
            'x': x,
            'y': self.height - y, 
            'direction_x': direction_x,
            'direction_y': direction_y,
            'color': color,
            'visible': True
        }
        self.point_entities_list.append(new_point)
        
    def update_points_function(self):
        if not self.simulation_active_mode:
            return
            
        current_time = time.time()
        if current_time - self.last_blink_time > 0.5:  #blink every 0.5 seconds
            self.points_blink_toogle = not self.points_blink_toogle #visible after every 0.5 seconds
            self.last_blink_time = current_time

        self.update_points_conditions()
          
    def update_points_conditions(self):
        for point in self.point_entities_list:
            if self.point_blink_mode:
                point['visible'] = self.points_blink_toogle                
            if self.simulation_active_mode:
                point['x'] += point['direction_x'] * self.points_movement_rate
                point['y'] += point['direction_y'] * self.points_movement_rate
            self.boundary_collision_detection_check_function(point) 
    def boundary_collision_detection_check_function(self,point):
        if point['x'] <= 0 or point['x'] >= self.width:
            point['direction_x'] *= -1
        
        if point['y'] <= 0 or point['y'] >= self.height:
            point['direction_y'] *= -1            

    def print_drawing_function(self):
        gl.glPointSize(5)
        gl.glBegin(gl.GL_POINTS)
        for point in self.point_entities_list:
            if point['visible']:
                gl.glColor3f(*point['color'])
                gl.glVertex2f(point['x'], point['y'])
        gl.glEnd()
        
    def draw_points_output(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        self.update_points_function()
        self.print_drawing_function()
        glut.glutSwapBuffers()
        
    def mouse_click_process_function(self, button, mouse_button_flag, x, y):
        if button == glut.GLUT_RIGHT_BUTTON and mouse_button_flag == glut.GLUT_DOWN:
            self.create_new_point(x, y)
            
        elif button == glut.GLUT_LEFT_BUTTON and mouse_button_flag == glut.GLUT_DOWN:
            self.point_blink_mode = not self.point_blink_mode
            self.mouse_click_condition()


    def mouse_click_condition(self):
        if not self.point_blink_mode:  
                for point in self.point_entities_list:
                    point['visible'] = True  


    def handle_key_presses(self, key, x, y):
        if key == b' ':
            self.simulation_active_mode = not self.simulation_active_mode
            
    def handle_special_keybinds(self, key, x, y):  #speedup and slowdown
        if key == glut.GLUT_KEY_UP:
            self.points_movement_rate = min(3.0, self.points_movement_rate + 0.1)
        elif key == glut.GLUT_KEY_DOWN:
            self.points_movement_rate = max(0.2, self.points_movement_rate - 0.1)
            
    def start_point_simulation_funciton(self):
        self.initialize_window()
        self.setup_event_handlers()
        self.configure_projection_function()
        glut.glutMainLoop()

if __name__ == "__main__":
    simulator = BouncingPointsSimulatorgame()
    simulator.start_point_simulation_funciton()