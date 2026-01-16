from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random as rd
import math as mt
import time 

game_over_boolean = False 
player_health_variable = 5
score_now = 0
total_missed_shots = 0
cheat_mode_boolean_Var = False
first_person_pov = False
auto_targeting_variable = False
previous_camera_variable = None  
player_speed_value = 17
previous_weapon_angle_value = None  

camera_position_val = (0, 500, 500)
camera_orientaiton_variable = 0

player_position_list = [0, 0, 0]
weapon_angle_value = 0
gun_barrel_length = 80
active_bullet_list = []
bullet_default_speed = 5
bullet_dimension_variable = 15

enemies_number = 5
total_enemy_list = []
enemy_speed_value = 0.3
size_of_enemy = 30
enemy_scale_value = 1.0
scale_change_value = 0.01

field_of_view = 122
arena_size_variable = 601
cheat_shot_counter_var = 0
last_update_time = time.time()

def init_game():
    global game_over_boolean, player_health_variable, score_now, total_missed_shots
    global player_position_list, weapon_angle_value, active_bullet_list, cheat_mode_boolean_Var, auto_targeting_variable
    global previous_weapon_angle_value
    
    game_over_boolean = False
    player_health_variable = 5
    score_now = 0
    total_missed_shots = 0
    player_position_list = [0, 0, 0]
    weapon_angle_value = 0
    active_bullet_list.clear()
    cheat_mode_boolean_Var = False
    auto_targeting_variable = False
    previous_weapon_angle_value = None
    spawn_enemies_function()

def spawn_enemies_function():
    total_enemy_list.clear()
    count = 0
    while count < enemies_number:
        x_pos = rd.randint(-arena_size_variable + 100, arena_size_variable - 100)
        y_pos = rd.randint(-arena_size_variable + 100, arena_size_variable - 100)

        if abs(x_pos) > 100 or abs(y_pos) > 100:
            total_enemy_list.append({
                'position': [x_pos, y_pos, size_of_enemy],
                'active': True
            })
            count += 1

def create_bullet_function(bullet_data):
    glPushMatrix()
    glTranslatef(*bullet_data['position'])
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(10)
    glPopMatrix()

def draw_arena_battlefield_function():
    cell_size_value = 50
    grid_cells_value = int(2 * arena_size_variable / cell_size_value)

    draw_arena_battlefield_function_condition(cell_size_value, grid_cells_value)

    wall_height = 115
    walls = [
        ((-arena_size_variable, -arena_size_variable), (arena_size_variable, -arena_size_variable), (0.7,0.5,1)),
        ((-arena_size_variable, arena_size_variable), (arena_size_variable, arena_size_variable), (0.9,.8,0)),
        ((-arena_size_variable, -arena_size_variable), (-arena_size_variable, arena_size_variable), (0,1,1)),
        ((arena_size_variable, -arena_size_variable), (arena_size_variable, arena_size_variable), (1,1,1))
    ]
    
    for (start, end, color) in walls:
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(start[0], start[1], 0)
        glVertex3f(end[0], end[1], 0)
        glVertex3f(end[0], end[1], wall_height)
        glVertex3f(start[0], start[1], wall_height)
        glEnd()

def draw_arena_battlefield_function_condition(cell_size_value, grid_cells_value):
    i = -grid_cells_value // 2
    while i < grid_cells_value // 2:
        j = -grid_cells_value // 2
        while j < grid_cells_value // 2:
            x1, x2 = i * cell_size_value, (i + 1) * cell_size_value
            y1, y2 = j * cell_size_value, (j + 1) * cell_size_value

            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)

            glBegin(GL_QUADS)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
            glEnd()

            j += 1
        i += 1

def draw_enemy(enemy_data):
    glPushMatrix()
    glTranslatef(*enemy_data['position'])
    glColor3f(0.8, 0.2, 0.2)
    gluSphere(gluNewQuadric(), size_of_enemy, 20, 20)
    
    glTranslatef(0, 0, size_of_enemy * 1.5)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), size_of_enemy * 0.5, 10, 10)

    glPopMatrix()

def fire_projectile_function(angle=None):
    global active_bullet_list
    
    if game_over_boolean:
        return
    
    if angle is None:
        angle = weapon_angle_value
    
    angle_rad = mt.radians(angle)
    
    if first_person_pov: #gun end theke bullet fire korbe
        start_pos = [
            player_position_list[0] + mt.cos(angle_rad) * gun_barrel_length,
            player_position_list[1] + mt.sin(angle_rad) * gun_barrel_length,
            player_position_list[2] + 80
        ]
    else:
        start_pos = [
            player_position_list[0] + mt.cos(angle_rad) * gun_barrel_length,
            player_position_list[1] + mt.sin(angle_rad) * gun_barrel_length,
            player_position_list[2] + 100
        ]
    
    bullet_speed_value = 10 if cheat_mode_boolean_Var else bullet_default_speed
    bullet_lifetime_value = 500 if cheat_mode_boolean_Var else 100
    
    active_bullet_list.append({
        'position': start_pos,
        'angle': angle,
        'lifetime': bullet_lifetime_value,
        'speed': bullet_speed_value
    })

def update_projectiles(): 
    global active_bullet_list, score_now, total_missed_shots, game_over_boolean
    
    expired_bullets = []
    
    i = 0
    while i < len(active_bullet_list):
        bullet = active_bullet_list[i]
        angle_rad = mt.radians(bullet['angle'])
        
        bullet_speed_value = bullet.get('speed', bullet_default_speed)
        bullet['position'][0] += mt.cos(angle_rad) * bullet_speed_value
        bullet['position'][1] += mt.sin(angle_rad) * bullet_speed_value
        bullet['lifetime'] -= 1

        if (abs(bullet['position'][0]) > arena_size_variable or 
            abs(bullet['position'][1]) > arena_size_variable or 
            bullet['lifetime'] <= 0):
            expired_bullets.append(bullet)
            total_missed_shots += 1
            if total_missed_shots >= 10:
                game_over_boolean = True
            i += 1
            continue
        j = 0 #collsion with enemy
        while j < len(total_enemy_list):
            enemy = total_enemy_list[j]
            if enemy['active']:
                dx = bullet['position'][0] - enemy['position'][0]
                dy = bullet['position'][1] - enemy['position'][1]
                distance_value = mt.hypot(dx, dy)

                if distance_value < size_of_enemy:
                    expired_bullets.append(bullet)
                    respawn_enemy_function(enemy)
                    score_now += 1
                    break 
            j += 1

        i += 1
    bullet_cleanup_looping_function(expired_bullets)

def bullet_cleanup_looping_function(expired_bullets):
    k = 0
    while k < len(expired_bullets):
        bullet = expired_bullets[k]
        if bullet in active_bullet_list:
            active_bullet_list.remove(bullet)
        k += 1

def update_enemies():
    global player_health_variable, game_over_boolean
    
    i = 0
    while i < len(total_enemy_list):
        enemy = total_enemy_list[i]
        update_enemy_loop_condition(enemy)
        i += 1


def update_enemy_loop_condition(enemy):
    global player_health_variable, game_over_boolean
    if enemy['active']:
        dx = player_position_list[0] - enemy['position'][0]
        dy = player_position_list[1] - enemy['position'][1]
        distance_value = mt.hypot(dx, dy)
        
        if distance_value > 0:
            enemy['position'][0] += (dx / distance_value) * enemy_speed_value
            enemy['position'][1] += (dy / distance_value) * enemy_speed_value
        
        if distance_value < 60:
            respawn_enemy_function(enemy)
            player_health_variable -= 1
            if player_health_variable <= 0:
                game_over_boolean = True



def respawn_enemy_function(enemy):
    while True:
        x = rd.randint(-arena_size_variable + 100, arena_size_variable - 100)
        y = rd.randint(-arena_size_variable + 100, arena_size_variable - 100)
        if (abs(x - player_position_list[0]) > 200 or 
            abs(y - player_position_list[1]) > 200):
            enemy['position'] = [x, y, size_of_enemy]
            break

def cheat_action_function():
    global weapon_angle_value, cheat_shot_counter_var, last_update_time, previous_weapon_angle_value

    if cheat_mode_boolean_Var and not game_over_boolean:
        now = time.time()
        delta = now - last_update_time
        last_update_time = now
        
        if previous_weapon_angle_value is None:
            previous_weapon_angle_value = weapon_angle_value
        
        rotation_speed = 460
        delta_angle = rotation_speed * delta
        new_angle = (weapon_angle_value + delta_angle) % 360
        
        prev = previous_weapon_angle_value % 360
        curr = new_angle % 360
        delta_a = (curr - prev) % 360
        
        for enemy in total_enemy_list:
            if enemy['active']:
                dx = enemy['position'][0] - player_position_list[0]
                dy = enemy['position'][1] - player_position_list[1]
                distance_value = mt.hypot(dx, dy)
                
                if distance_value >= 500:
                    continue
                
                target_angle = mt.degrees(mt.atan2(dy, dx)) % 360
                rel_target = (target_angle - prev) % 360
                
                if rel_target <= delta_a:
                    fire_projectile_function(angle=target_angle)
        
        previous_weapon_angle_value = new_angle
        weapon_angle_value = new_angle

def handle_keyboard_function(key, x, y):
    global player_position_list, weapon_angle_value, cheat_mode_boolean_Var, game_over_boolean, auto_targeting_variable
    
    if game_over_boolean and key == b'r':
        init_game()
        return
    
    if game_over_boolean:
        return
    
    move_speed = player_speed_value if key == b'w' else -5 if key == b's' else 0
    
    if move_speed != 0:
        angle_rad = mt.radians(weapon_angle_value)
        new_x = player_position_list[0] + mt.cos(angle_rad) * move_speed
        new_y = player_position_list[1] + mt.sin(angle_rad) * move_speed
        
        if abs(new_x) < arena_size_variable - 30 and abs(new_y) < arena_size_variable - 30:
            player_position_list[0], player_position_list[1] = new_x, new_y
    
    return keybinds_funciton_condition(key)

def keybinds_funciton_condition(key):
    global weapon_angle_value, cheat_mode_boolean_Var, auto_targeting_variable
    if key == b'd':
        weapon_angle_value = (weapon_angle_value - 5) % 360
    elif key == b'a':
        weapon_angle_value = (weapon_angle_value + 5) % 360
    elif key == b'c':
        cheat_mode_boolean_Var = not cheat_mode_boolean_Var
    elif key == b'v':
        auto_targeting_variable = not auto_targeting_variable

def handle_special_keys(key, x, y):
    global camera_position_val, camera_orientaiton_variable
    cam_x, cam_y, cam_z = camera_position_val
    handle_special_keys_condition(key, cam_x, cam_y, cam_z)
    glutPostRedisplay()

def handle_special_keys_condition(key, cam_x, cam_y, cam_z):
    global camera_orientaiton_variable, camera_position_val
    if key == GLUT_KEY_UP and cam_z < 1000:
        cam_z += 20
    elif key == GLUT_KEY_DOWN and cam_z > 100:
        cam_z -= 20
    elif key == GLUT_KEY_LEFT:
        camera_orientaiton_variable = (camera_orientaiton_variable - 5) % 360
    elif key == GLUT_KEY_RIGHT:
        camera_orientaiton_variable = (camera_orientaiton_variable + 5) % 360
    
    camera_position_val = (cam_x, cam_y, cam_z)

def handle_mouse(button, state, x, y):
    global first_person_pov
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over_boolean:
        fire_projectile_function()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_pov = not first_person_pov

def configure_camera_function():
    global first_person_pov, previous_camera_variable, camera_orientaiton_variable, camera_position_val
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(field_of_view, 1.10, 0.5, 2000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    return configure_camera_funciton_condition()



def configure_camera_funciton_condition():
    global first_person_pov, previous_camera_variable, camera_orientaiton_variable, camera_position_val, player_position_list, weapon_angle_value, cheat_mode_boolean_Var, auto_targeting_variable
    if first_person_pov:
        eye_x = player_position_list[0] + 30
        eye_y = player_position_list[1]
        eye_z = player_position_list[2] + 120
    
        if cheat_mode_boolean_Var and auto_targeting_variable:
            angle_rad = mt.radians(weapon_angle_value)
            look_x = eye_x + mt.cos(angle_rad) * 10
            look_y = eye_y + mt.sin(angle_rad) * 10
            look_z = eye_z - 10
            previous_camera_variable = (eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
            gluLookAt(*previous_camera_variable)
        else:
            gluLookAt(*(previous_camera_variable if previous_camera_variable else (eye_x, eye_y, eye_z, 
                    eye_x + 10, eye_y, eye_z - 10, 0, 0, 1)))
    else:
        cam_x = player_position_list[0] + 500 * mt.cos(mt.radians(camera_orientaiton_variable))
        cam_y = player_position_list[1] + 500 * mt.sin(mt.radians(camera_orientaiton_variable))
        gluLookAt(cam_x, cam_y, camera_position_val[2],
                *player_position_list,
                0, 0, 1)
def game_loop():
    if not game_over_boolean:
        update_projectiles()
        update_enemies()
        if cheat_mode_boolean_Var:
            cheat_action_function()
    glutPostRedisplay()

def display_text_function(x_pos, y_pos, text_str, font=GLUT_BITMAP_HELVETICA_18, color=(0.9, 0.9, 1.0)):
    glColor3f(*color)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 930, 0, 580)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x_pos, y_pos)

    for ch in text_str:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_player_function():
    glPushMatrix()
    glTranslatef(*player_position_list)
    
    if game_over_boolean:
        glRotatef(-90, 0, 1, 0)
    else:
        glRotatef(weapon_angle_value, 0, 0, 1)

    glColor3f(0.3, 0.4, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 90)
    glutSolidCube(45)
    glPopMatrix()
    
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 150)
    gluSphere(gluNewQuadric(), 28, 10, 5)
    glPopMatrix()
    
    for side in [15, -15]:
        glColor3f(0, 0, 1)
        glPushMatrix()
        glTranslatef(20, side, 0)
        gluCylinder(gluNewQuadric(), 7, 12, 70, 10, 10)
        glPopMatrix()
    
    glColor3f(0.75, 0.75, 0.75)
    glPushMatrix()
    glTranslatef(0, 0, 100)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 12, 7, 80, 10, 10)
    glPopMatrix()
    
    for side in [15, -15]:
        glColor3f(1, 0.85, 0.7)
        glPushMatrix()
        glTranslatef(20, side, 100)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 10, 6, 30, 10, 10)
        glPopMatrix()

    glPopMatrix()

def render_scene_function():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 930, 580)  # Match window size
    glEnable(GL_DEPTH_TEST)
    configure_camera_function()
    draw_arena_battlefield_function()
    render_player_function()
    render_scene_condition_function()

    glutSwapBuffers()

def render_scene_condition_function():
    for bullet in active_bullet_list:
        create_bullet_function(bullet)
    
    for enemy in total_enemy_list:
        if enemy['active']:
            draw_enemy(enemy)
    
    if not game_over_boolean:
        display_text_function(10, 550, f"Health: {player_health_variable}")
        display_text_function(10, 520, f"Score: {score_now}")
        display_text_function(10, 490, f"Misses: {total_missed_shots}/10")
    else:
        display_text_function(465, 350, f"Game Over! Final Score: {score_now}", GLUT_BITMAP_HELVETICA_18, (1.0, 0.0, 0.0))
        display_text_function(465, 320, "Press R to Restart", GLUT_BITMAP_HELVETICA_18, (0.9, 0.8, 0.0))

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(930, 580)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D_shooting_game") 
    spawn_enemies_function()
    glutDisplayFunc(render_scene_function)
    glutKeyboardFunc(handle_keyboard_function)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse)
    glutIdleFunc(game_loop)
    glutMainLoop()

if __name__ == "__main__":
    main()