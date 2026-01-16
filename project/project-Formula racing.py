import random
import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
window_screen_width = 1100
window_screen_height = 900
track_grid_size = 3300
track_grid_divisions = 20
track_lane_width = 150
track_inner_radius_x = 1485
track_inner_radius_y = 990
track_outer_radius_x = track_inner_radius_x + track_lane_width
track_outer_radius_y = track_inner_radius_y + track_lane_width
track_segment_count = 64
track_surface_height = 3.0
vehicle_max_speed = 4.0
vehicle_acceleration = 0.5
vehicle_friction = 0.02
vehicle_turn_speed = 3.0
off_track_slowdown_factor = 0.3
camera_initial_distance = 20.0
camera_initial_height = 10.0
camera_min_distance = 10.0
camera_max_distance = 40.0
camera_min_height = 5.0
camera_max_height = 20.0
camera_zoom_step = 2.0
camera_rotation_step = 5.0
cone_base_length = 20
cone_height_size = 30
cone_total_count = 25
pothole_radius = 15
pothole_total_count = 17
minimum_obstacle_distance = 50
respawn_display_duration = 2.0
flicker_total_count = 4
player_max_health = 100
player_health_penalty = 25
pothole_speed_penalty_factor = 0.7
bike_acceleration_rate = 0.1
bike_friction_rate = 0.03
bike_turning_speed = 2.0
bike_maximum_lean_angle = 25.0
game_total_time = 180.0
required_laps_count = 5
powerup_total_count = 5
powerup_radius = 15
powerup_effect_duration = 3.0
powerup_speed_multiplier_factor = 2.0
powerdown_total_count = 5
powerdown_radius = 15
powerdown_time_penalty = 30.0
banana_trap_total_count = 5
banana_trap_radius = 15
banana_trap_effect_duration = 4.0


class GameState:

    def __init__(self):
        self.vehicle_position_x = track_inner_radius_x + track_lane_width / 2
        self.vehicle_position_y = 0.0
        self.vehicle_angle = 0.0
        self.previous_angle = 0.0
        self.vehicle_speed = 0.0
        self.flicker_timer = 0.0
        self.player_health = player_max_health
        self.keys_pressed = set()
        self.laps_completed_count = 0
        self.has_crossed_start_line = False
        self.last_update_time = time.time()
        self.camera_distance = camera_initial_distance
        self.camera_height = camera_initial_height
        self.camera_angle_offset = 90.0
        self.last_valid_position_x = self.vehicle_position_x
        self.last_valid_position_y = self.vehicle_position_y
        self.last_valid_angle = self.vehicle_angle
        self.cone_positions = []
        self.pothole_positions = []
        self.powerup_positions = []
        self.powerdown_positions = []
        self.banana_trap_positions = []
        self.banana_trap_active = False
        self.banana_trap_timer = 0.0
        self.is_game_over = False
        self.is_start_screen = True
        self.selected_vehicle_type = None
        self.bike_lean_angle_state = 0.0
        self.game_start_time = None
        self.game_final_time = None
        self.is_first_person_view = False
        self.is_powerup_active = False
        self.powerup_timer = 0.0
        self.original_max_speed_setting = vehicle_max_speed
        angle_step = 2 * math.pi / cone_total_count
        self.generate_cones(angle_step)
        self.generate_potholes()
        self.generate_powerups()
        self.generate_powerdowns()
        self.generate_banana_pills()
    def generate_cones(self,angle_step):
        while angle_step < cone_total_count:
            angle = angle_step * angle_step
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)

            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                self.cone_positions.append((position_x_value, position_y_value))
            
            angle_step += 1


    def generate_potholes(self):
        placed_potholes = 0
        while placed_potholes < pothole_total_count:
            angle = random.uniform(0, 2 * math.pi)
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)

            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                valid = True              
                for center_x, center_y in self.cone_positions:
                    dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                if valid:
                    for position_x, position_y in self.pothole_positions:
                        dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                        if dist < minimum_obstacle_distance:
                            valid = False
                            break
                if valid:
                    self.pothole_positions.append((position_x_value, position_y_value))
                    placed_potholes += 1



    def generate_powerups(self):
        placed_powerups = 0
        while placed_powerups < powerup_total_count:
            max_attempts = 10
            attempts = 0

            while attempts < max_attempts:
                angle = random.uniform(0, 2 * math.pi)
                time_value = random.uniform(0, 1)
                x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
                y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
                position_x_value = x_radius * math.cos(angle)
                position_y_value = y_radius * math.sin(angle)
                start_x = track_inner_radius_x + track_lane_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)

                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > minimum_obstacle_distance:
                    valid = True

                    for center_x, center_y in self.cone_positions:
                        dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                        if dist < minimum_obstacle_distance:
                            valid = False
                            break

                    if valid:
                        for position_x, position_y in self.pothole_positions:
                            dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                            if dist < minimum_obstacle_distance:
                                valid = False
                                break
                    if valid:
                        for ppx, ppy in self.powerup_positions:
                            dist = math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2)
                            if dist < minimum_obstacle_distance:
                                valid = False
                                break
                    
                    if valid:
                        self.powerup_positions.append((position_x_value, position_y_value))
                        placed_powerups += 1
                        break 
                
                attempts += 1

    
    def generate_powerdowns(self):
        placed_powerdowns = 0
        while placed_powerdowns < powerdown_total_count:
            max_attempts = 20
            attempts = 0

            while attempts < max_attempts:
                angle = random.uniform(0, 2 * math.pi)
                time_value = random.uniform(0, 1)
                x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
                y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
                position_x_value = x_radius * math.cos(angle)
                position_y_value = y_radius * math.sin(angle)
                start_x = track_inner_radius_x + track_lane_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)

                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > minimum_obstacle_distance:
                    valid = True
                    
                    for center_x, center_y in self.cone_positions:
                        if math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2) < minimum_obstacle_distance:
                            valid = False
                            break

                    if valid:
                        for position_x, position_y in self.pothole_positions:
                            if math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        for ppx, ppy in self.powerup_positions:
                            if math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        for pdx, pdy in self.powerdown_positions:
                            if math.sqrt((position_x_value - pdx) ** 2 + (position_y_value - pdy) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        self.powerdown_positions.append((position_x_value, position_y_value))
                        placed_powerdowns += 1
                        break

                attempts += 1


    def generate_banana_pills(self):
        placed_banana_pills = 0
        while placed_banana_pills < banana_trap_total_count:
            max_attempts = 20
            attempts = 0

            while attempts < max_attempts:
                angle = random.uniform(0, 2 * math.pi)
                time_value = random.uniform(0, 1)
                x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
                y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
                position_x_value = x_radius * math.cos(angle)
                position_y_value = y_radius * math.sin(angle)
                start_x = track_inner_radius_x + track_lane_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)

                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > minimum_obstacle_distance:
                    valid = True
                    
                    for center_x, center_y in self.cone_positions:
                        if math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2) < minimum_obstacle_distance:
                            valid = False
                            break

                    if valid:
                        for position_x, position_y in self.pothole_positions:
                            if math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        for ppx, ppy in self.powerup_positions:
                            if math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        for pdx, pdy in self.powerdown_positions:
                            if math.sqrt((position_x_value - pdx) ** 2 + (position_y_value - pdy) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        for bpx, bpy in self.banana_trap_positions:
                            if math.sqrt((position_x_value - bpx) ** 2 + (position_y_value - bpy) ** 2) < minimum_obstacle_distance:
                                valid = False
                                break

                    if valid:
                        self.banana_trap_positions.append((position_x_value, position_y_value))
                        placed_banana_pills += 1
                        break

                attempts += 1

        self.respawn_timer = 0.0
        self.is_flicker_active = False
        self.flicker_total_count = 0
        self.last_collision_time = 0.0
        self.is_colliding = False
game_state_manager = GameState()
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_screen_width, window_screen_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'FORMULA F1 RACING GAME')
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(update)
    glutMainLoop()

def update():
    updatre_condition()


    glutPostRedisplay()


def updatre_condition():
    if game_state_manager.is_start_screen:
        glutPostRedisplay()
        return
    current_time = time.time()
    delta_time = current_time - game_state_manager.last_update_time
    game_state_manager.last_update_time = current_time
    if game_state_manager.is_game_over:
        if game_state_manager.game_final_time is None:
            game_state_manager.game_final_time = max(0, game_total_time - (current_time - game_state_manager.game_start_time))
        glutPostRedisplay()
        return
    if game_state_manager.game_start_time is None:
        game_state_manager.game_start_time = current_time
    time_elapsed = current_time - game_state_manager.game_start_time
    if time_elapsed >= game_total_time and game_state_manager.laps_completed_count < required_laps_count:
        game_state_manager.is_game_over = True
        game_state_manager.game_final_time = 0
        glutPostRedisplay()
        return
    if game_state_manager.laps_completed_count >= required_laps_count:
        game_state_manager.is_game_over = True
        game_state_manager.game_final_time = max(0, game_total_time - time_elapsed)
        glutPostRedisplay()
        return
    if game_state_manager.is_powerup_active:
        game_state_manager.powerup_timer += delta_time
        if game_state_manager.powerup_timer >= powerup_effect_duration:
            game_state_manager.is_powerup_active = False
            game_state_manager.powerup_timer = 0.0
            game_state_manager.original_max_speed_setting = vehicle_max_speed
            if game_state_manager.vehicle_speed > game_state_manager.original_max_speed_setting:
                game_state_manager.vehicle_speed = game_state_manager.original_max_speed_setting
            elif game_state_manager.vehicle_speed < -game_state_manager.original_max_speed_setting / 2:
                game_state_manager.vehicle_speed = -game_state_manager.original_max_speed_setting / 2
    if game_state_manager.banana_trap_active:
        game_state_manager.banana_trap_timer += delta_time
        if game_state_manager.banana_trap_timer >= banana_trap_effect_duration:
            game_state_manager.banana_trap_active = False
            game_state_manager.banana_trap_timer = 0.0
    on_track = is_on_track(game_state_manager.vehicle_position_x, game_state_manager.vehicle_position_y)
    if on_track:
        game_state_manager.last_valid_position_x = game_state_manager.vehicle_position_x
        game_state_manager.last_valid_position_y = game_state_manager.vehicle_position_y
        game_state_manager.last_valid_angle = game_state_manager.vehicle_angle
    if on_track:
        track_angle = math.atan2(game_state_manager.vehicle_position_y, game_state_manager.vehicle_position_x)
        if track_angle < 0:
            track_angle += 2 * math.pi
        if game_state_manager.previous_angle < 0:
            game_state_manager.previous_angle += 2 * math.pi
        finish_line_angle = 0
        angle_tolerance = math.radians(10)
        if abs(track_angle) < angle_tolerance or abs(track_angle - 2 * math.pi) < angle_tolerance:
            if game_state_manager.previous_angle > math.pi and track_angle < math.pi:
                game_state_manager.laps_completed_count += 1
                print(f'Lap completed: {game_state_manager.laps_completed_count}')
        game_state_manager.previous_angle = track_angle
    current_max_speed = game_state_manager.original_max_speed_setting * off_track_slowdown_factor if not on_track else game_state_manager.original_max_speed_setting
    if game_state_manager.selected_vehicle_type == 'bike':
        current_acceleration = bike_acceleration_rate * off_track_slowdown_factor if not on_track else bike_acceleration_rate
        current_friction = bike_friction_rate * off_track_slowdown_factor if not on_track else bike_friction_rate
        current_turn_speed = bike_turning_speed * off_track_slowdown_factor if not on_track else bike_turning_speed
    else:
        current_acceleration = vehicle_acceleration * off_track_slowdown_factor if not on_track else vehicle_acceleration
        current_friction = vehicle_friction * off_track_slowdown_factor if not on_track else vehicle_friction
        current_turn_speed = vehicle_turn_speed * off_track_slowdown_factor if not on_track else vehicle_turn_speed
    if game_state_manager.respawn_timer > 0:
        game_state_manager.respawn_timer -= delta_time
        game_state_manager.flicker_timer += delta_time
        if game_state_manager.flicker_timer >= 0.1:
            game_state_manager.is_flicker_active = not game_state_manager.is_flicker_active
            game_state_manager.flicker_total_count += 1
            game_state_manager.flicker_timer = 0.0
        if game_state_manager.respawn_timer <= 0:
            game_state_manager.flicker_total_count = 0
            game_state_manager.bike_lean_angle_state = 0.0
            game_state_manager.is_flicker_active = False
            game_state_manager.flicker_timer = 0.0
        game_state_manager.vehicle_speed = 0
        return
    if b'w' in game_state_manager.keys_pressed:
        if game_state_manager.banana_trap_active:
            game_state_manager.vehicle_speed -= current_acceleration * delta_time * 60
        else:
            game_state_manager.vehicle_speed += current_acceleration * delta_time * 60
    elif b's' in game_state_manager.keys_pressed:
        if game_state_manager.banana_trap_active:
            game_state_manager.vehicle_speed += current_acceleration * delta_time * 60
        else:
            game_state_manager.vehicle_speed -= current_acceleration * delta_time * 60
    elif game_state_manager.vehicle_speed > 0:
        game_state_manager.vehicle_speed = max(0, game_state_manager.vehicle_speed - current_friction * delta_time * 60)
    else:
        game_state_manager.vehicle_speed = min(0, game_state_manager.vehicle_speed + current_friction * delta_time * 60)
    game_state_manager.vehicle_speed = max(-current_max_speed / 2, min(current_max_speed, game_state_manager.vehicle_speed))
    movement_angle = game_state_manager.vehicle_angle + 90
    if game_state_manager.selected_vehicle_type == 'bike':
        if abs(game_state_manager.vehicle_speed) > 0.01:
            speed_factor = abs(game_state_manager.vehicle_speed) / game_state_manager.original_max_speed_setting
            target_lean = 0.0
            lean_rate = current_turn_speed * 2.0
            if b'a' in game_state_manager.keys_pressed:
                if game_state_manager.banana_trap_active:
                    game_state_manager.vehicle_angle -= current_turn_speed * delta_time * 60
                    target_lean = -bike_maximum_lean_angle * speed_factor
                else:
                    game_state_manager.vehicle_angle += current_turn_speed * delta_time * 60
                    target_lean = bike_maximum_lean_angle * speed_factor
            elif b'd' in game_state_manager.keys_pressed:
                if game_state_manager.banana_trap_active:
                    game_state_manager.vehicle_angle += current_turn_speed * delta_time * 60
                    target_lean = bike_maximum_lean_angle * speed_factor
                else:
                    game_state_manager.vehicle_angle -= current_turn_speed * delta_time * 60
                    target_lean = -bike_maximum_lean_angle * speed_factor
            lean_diff = target_lean - game_state_manager.bike_lean_angle_state
            game_state_manager.bike_lean_angle_state += lean_diff * min(1.0, lean_rate * delta_time * 60)
            game_state_manager.bike_lean_angle_state = max(-bike_maximum_lean_angle, min(bike_maximum_lean_angle, game_state_manager.bike_lean_angle_state))
        else:
            game_state_manager.bike_lean_angle_state = 0.0
    elif abs(game_state_manager.vehicle_speed) > 0.01:
        turn_factor = 1.0 if game_state_manager.vehicle_speed > 0 else -1.0
        if b'a' in game_state_manager.keys_pressed:
            if game_state_manager.banana_trap_active:
                game_state_manager.vehicle_angle -= current_turn_speed * turn_factor * delta_time * 60
            else:
                game_state_manager.vehicle_angle += current_turn_speed * turn_factor * delta_time * 60
        if b'd' in game_state_manager.keys_pressed:
            if game_state_manager.banana_trap_active:
                game_state_manager.vehicle_angle += current_turn_speed * turn_factor * delta_time * 60
            else:
                game_state_manager.vehicle_angle -= current_turn_speed * turn_factor * delta_time * 60
    angle_rad = math.radians(movement_angle)
    new_x = game_state_manager.vehicle_position_x + game_state_manager.vehicle_speed * math.cos(angle_rad) * delta_time * 60
    new_y = game_state_manager.vehicle_position_y + game_state_manager.vehicle_speed * math.sin(angle_rad) * delta_time * 60
    half_grid = track_grid_size / 2
    if is_in_water(new_x, new_y):
        game_state_manager.player_health = 0
        game_state_manager.is_game_over = True
        game_state_manager.vehicle_speed = 0.0
        game_state_manager.bike_lean_angle_state = 0.0
        game_state_manager.game_final_time = max(0, game_total_time - (current_time - game_state_manager.game_start_time))
    elif new_x < -half_grid or new_x > half_grid or new_y < -half_grid or (new_y > half_grid):
        game_state_manager.vehicle_speed = 0.0
        game_state_manager.bike_lean_angle_state = 0.0
        if check_boundary_collision():
            game_state_manager.vehicle_position_x = game_state_manager.last_valid_position_x
            game_state_manager.vehicle_position_y = game_state_manager.last_valid_position_y
            game_state_manager.vehicle_angle = game_state_manager.last_valid_angle
            game_state_manager.respawn_timer = respawn_display_duration
            game_state_manager.is_flicker_active = True
            game_state_manager.flicker_total_count = 0
            game_state_manager.bike_lean_angle_state = 0.0
    elif check_collision(new_x, new_y) and (not check_collision(game_state_manager.vehicle_position_x, game_state_manager.vehicle_position_y)):
        game_state_manager.vehicle_speed = 0.0
        game_state_manager.bike_lean_angle_state = 0.0
        game_state_manager.player_health = max(0, game_state_manager.player_health - player_health_penalty)
        game_state_manager.last_collision_time = time.time()
        game_state_manager.vehicle_position_x = game_state_manager.last_valid_position_x
        game_state_manager.vehicle_position_y = game_state_manager.last_valid_position_y
        game_state_manager.vehicle_angle = game_state_manager.last_valid_angle
        game_state_manager.respawn_timer = respawn_display_duration
        game_state_manager.is_flicker_active = True
        game_state_manager.flicker_total_count = 0
        game_state_manager.flicker_timer = 0.0
        game_state_manager.bike_lean_angle_state = 0.0
        if game_state_manager.player_health <= 0:
            game_state_manager.is_game_over = True
            game_state_manager.game_final_time = max(0, game_total_time - (current_time - game_state_manager.game_start_time))
    elif check_powerup_collision(new_x, new_y):
        game_state_manager.is_powerup_active = True
        game_state_manager.powerup_timer = 0.0
        game_state_manager.original_max_speed_setting = vehicle_max_speed * powerup_speed_multiplier_factor
        game_state_manager.vehicle_speed *= powerup_speed_multiplier_factor
    elif check_powerdown_collision(new_x, new_y):
        if game_state_manager.game_start_time:
            game_state_manager.game_start_time -= powerdown_time_penalty
            if game_total_time - (current_time - game_state_manager.game_start_time) <= 0:
                game_state_manager.is_game_over = True
                game_state_manager.game_final_time = 0
    elif check_banana_pill_collision(new_x, new_y):
        game_state_manager.banana_trap_active = True
        game_state_manager.banana_trap_timer = 0.0
    else:
        game_state_manager.vehicle_position_x = new_x
        game_state_manager.vehicle_position_y = new_y
        if is_on_track(game_state_manager.vehicle_position_x, game_state_manager.vehicle_position_y):
            game_state_manager.last_valid_position_x = game_state_manager.vehicle_position_x
            game_state_manager.last_valid_position_y = game_state_manager.vehicle_position_y
            game_state_manager.last_valid_angle = game_state_manager.vehicle_angle




def keyboard_up(key, position_x_value, position_y_value):
    if key in game_state_manager.keys_pressed:
        game_state_manager.keys_pressed.remove(key)
    if not game_state_manager.is_game_over and (not game_state_manager.is_start_screen):
        glutPostRedisplay()

def keyboard(key, position_x_value, position_y_value):
    keyboard_condition(key)


def keyboard_condition(key):
    if game_state_manager.is_start_screen:
        if key == b'b':
            game_state_manager.selected_vehicle_type = 'bike'
            game_state_manager.is_start_screen = False
            game_state_manager.camera_angle_offset = 90.0
        elif key == b'c':
            game_state_manager.selected_vehicle_type = 'car'
            game_state_manager.is_start_screen = False
            game_state_manager.camera_angle_offset = 90.0
        glutPostRedisplay()
        return
    game_state_manager.keys_pressed.add(key)
    if key == b'\x1b':
        glutLeaveMainLoop()
    if key == b'r':
        reset_game()
    if key == b'f' and (not game_state_manager.is_game_over):
        game_state_manager.is_first_person_view = not game_state_manager.is_first_person_view
    if not game_state_manager.is_game_over:
        glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if game_state_manager.is_start_screen:
        draw_start_screen()
    else:
        setup_camera()
        draw_grid()
        draw_oval_track()
        draw_potholes()
        draw_cones()
        draw_powerups()
        draw_powerdowns()
        draw_banana_pills()
        if not game_state_manager.is_game_over:
            draw_vehicle()
        draw_hud()
    glutSwapBuffers()

def specialKeyListener(key, position_x_value, position_y_value):
    specialkeylistenerfunction(key, position_x_value, position_y_value)
    glutPostRedisplay()

def specialkeylistenerfunction(key, position_x_value, position_y_value):
        if not game_state_manager.is_game_over and (not game_state_manager.is_start_screen):
            if key == GLUT_KEY_UP:
                game_state_manager.camera_distance = max(camera_min_distance, game_state_manager.camera_distance - camera_zoom_step)
                time_value = (game_state_manager.camera_distance - camera_min_distance) / (camera_max_distance - camera_min_distance)
                game_state_manager.camera_height = camera_min_height + time_value * (camera_max_height - camera_min_height)
            elif key == GLUT_KEY_DOWN:
                game_state_manager.camera_distance = min(camera_max_distance, game_state_manager.camera_distance + camera_zoom_step)
                time_value = (game_state_manager.camera_distance - camera_min_distance) / (camera_max_distance - camera_min_distance)
                game_state_manager.camera_height = camera_min_height + time_value * (camera_max_height - camera_min_height)
            elif key == GLUT_KEY_LEFT:
                game_state_manager.camera_angle_offset += camera_rotation_step
            elif key == GLUT_KEY_RIGHT:
                game_state_manager.camera_angle_offset -= camera_rotation_step


def reset_game():
    game_state_manager.vehicle_position_x = track_inner_radius_x + track_lane_width / 2
    game_state_manager.vehicle_position_y = 0.0
    game_state_manager.vehicle_speed = 0.0
    game_state_manager.vehicle_angle = 0.0
    game_state_manager.previous_angle = 0.0
    game_state_manager.flicker_timer = 0.0
    game_state_manager.player_health = player_max_health
    game_state_manager.camera_distance = camera_initial_distance
    game_state_manager.camera_height = camera_initial_height
    game_state_manager.camera_angle_offset = 0.0
    game_state_manager.last_valid_position_x = game_state_manager.vehicle_position_x
    game_state_manager.last_valid_position_y = game_state_manager.vehicle_position_y
    game_state_manager.last_valid_angle = game_state_manager.vehicle_angle
    game_state_manager.cone_positions = []
    game_state_manager.pothole_positions = []
    game_state_manager.powerup_positions = []
    game_state_manager.powerdown_positions = []
    game_state_manager.banana_trap_positions = []
    game_state_manager.is_game_over = False
    game_state_manager.is_start_screen = True
    game_state_manager.selected_vehicle_type = None
    game_state_manager.bike_lean_angle_state = 0.0
    game_state_manager.game_start_time = None
    game_state_manager.game_final_time = None
    game_state_manager.is_first_person_view = False
    game_state_manager.is_powerup_active = False
    game_state_manager.powerup_timer = 0.0
    game_state_manager.banana_trap_active = False
    game_state_manager.banana_trap_timer = 0.0
    game_state_manager.original_max_speed_setting = vehicle_max_speed
    angle_step = 2 * math.pi / cone_total_count
    for i in range(cone_total_count):
        angle = i * angle_step
        time_value = random.uniform(0, 1)
        x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
        y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
        position_x_value = x_radius * math.cos(angle)
        position_y_value = y_radius * math.sin(angle)
        start_x = track_inner_radius_x + track_lane_width / 2
        start_y = 0.0
        dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)
        if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
            game_state_manager.cone_positions.append((position_x_value, position_y_value))
    for i in range(pothole_total_count):
        max_attempts = 100
        for var in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                valid = True
                for center_x, center_y in game_state_manager.cone_positions:
                    dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for position_x, position_y in game_state_manager.pothole_positions:
                    dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                if valid:
                    game_state_manager.pothole_positions.append((position_x_value, position_y_value))
                    break
    for i in range(powerup_total_count):
        max_attempts = 100
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                valid = True
                for center_x, center_y in game_state_manager.cone_positions:
                    dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for position_x, position_y in game_state_manager.pothole_positions:
                    dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for ppx, ppy in game_state_manager.powerup_positions:
                    dist = math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                if valid:
                    game_state_manager.powerup_positions.append((position_x_value, position_y_value))
                    break
    for i in range(powerdown_total_count):
        maximum_attempts = 100
        for _ in range(maximum_attempts):
            angle = random.uniform(0, 2 * math.pi)
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                valid = True
                for center_x, center_y in game_state_manager.cone_positions:
                    dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for position_x, position_y in game_state_manager.pothole_positions:
                    dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for ppx, ppy in game_state_manager.powerup_positions:
                    dist = math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for pdx, pdy in game_state_manager.powerdown_positions:
                    dist = math.sqrt((position_x_value - pdx) ** 2 + (position_y_value - pdy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                if valid:
                    game_state_manager.powerdown_positions.append((position_x_value, position_y_value))
                    break
    for i in range(banana_trap_total_count):
        maximum_attempts = 100
        for _ in range(maximum_attempts):
            angle = random.uniform(0, 2 * math.pi)
            time_value = random.uniform(0, 1)
            x_radius = track_inner_radius_x + time_value * (track_outer_radius_x - track_inner_radius_x)
            y_radius = track_inner_radius_y + time_value * (track_outer_radius_y - track_inner_radius_y)
            position_x_value = x_radius * math.cos(angle)
            position_y_value = y_radius * math.sin(angle)
            start_x = track_inner_radius_x + track_lane_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((position_x_value - start_x) ** 2 + (position_y_value - start_y) ** 2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and (dist_to_start > minimum_obstacle_distance):
                valid = True
                for center_x, center_y in game_state_manager.cone_positions:
                    dist = math.sqrt((position_x_value - center_x) ** 2 + (position_y_value - center_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for position_x, position_y in game_state_manager.pothole_positions:
                    dist = math.sqrt((position_x_value - position_x) ** 2 + (position_y_value - position_y) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for ppx, ppy in game_state_manager.powerup_positions:
                    dist = math.sqrt((position_x_value - ppx) ** 2 + (position_y_value - ppy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for pdx, pdy in game_state_manager.powerdown_positions:
                    dist = math.sqrt((position_x_value - pdx) ** 2 + (position_y_value - pdy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                for bpx, bpy in game_state_manager.banana_trap_positions:
                    dist = math.sqrt((position_x_value - bpx) ** 2 + (position_y_value - bpy) ** 2)
                    if dist < minimum_obstacle_distance:
                        valid = False
                        break
                if valid:
                    game_state_manager.banana_trap_positions.append((position_x_value, position_y_value))
                    break
    game_state_manager.respawn_timer = 0.0
    game_state_manager.flicker_total_count = 0
    game_state_manager.laps_completed_count = 0
    game_state_manager.has_crossed_start_line = False
    game_state_manager.last_collision_time = 0.0

def check_boundary_collision():
    return check_boundary_collision_condition()


def check_boundary_collision_condition():
    current_time = time.time()
    if current_time - game_state_manager.last_collision_time < 0.5:
        return False
    half_grid = track_grid_size / 2
    kart_half_width = 1.9
    kart_half_length = 2.5
    if abs(game_state_manager.vehicle_position_x) + kart_half_width >= half_grid or abs(game_state_manager.vehicle_position_y) + kart_half_length >= half_grid:
        game_state_manager.player_health = max(0, game_state_manager.player_health - player_health_penalty)
        game_state_manager.last_collision_time = current_time
        if game_state_manager.player_health <= 0:
            game_state_manager.is_game_over = True
        return True
    return False


def check_banana_pill_collision(position_x_value, position_y_value):
    return check_banana_pill_collision_condition(position_x_value, position_y_value)

def check_banana_pill_collision_condition(position_x_value, position_y_value):
    kart_x = position_x_value
    kart_y = position_y_value
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    for banana_pill_x, banana_pill_y in game_state_manager.banana_trap_positions:
        dist = math.sqrt((kart_x - banana_pill_x) ** 2 + (kart_y - banana_pill_y) ** 2)
        if dist < banana_trap_radius + max(kart_half_width, kart_half_length):
            to_remove = (banana_pill_x, banana_pill_y)
            break
    if to_remove:
        game_state_manager.banana_trap_positions.remove(to_remove)
        return True
    return False

def check_powerdown_collision(position_x_value, position_y_value):
    return check_powerdown_collision_condition(position_x_value, position_y_value) 



def check_powerdown_collision_condition(position_x_value, position_y_value):
    kart_x = position_x_value
    kart_y = position_y_value
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    for powerdown_x, powerdown_y in game_state_manager.powerdown_positions:
        dist = math.sqrt((kart_x - powerdown_x) ** 2 + (kart_y - powerdown_y) ** 2)
        if dist < powerdown_radius + max(kart_half_width, kart_half_length):
            to_remove = (powerdown_x, powerdown_y)
            break
    if to_remove:
        game_state_manager.powerdown_positions.remove(to_remove)
        return True
    return False


def check_powerup_collision(position_x_value, position_y_value):
    return check_powerup_collision_condition(position_x_value, position_y_value)

def check_powerup_collision_condition(position_x_value, position_y_value):
    kart_x = position_x_value
    kart_y = position_y_value
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    for powerup_x, powerup_y in game_state_manager.powerup_positions:
        dist = math.sqrt((kart_x - powerup_x) ** 2 + (kart_y - powerup_y) ** 2)
        if dist < powerup_radius + max(kart_half_width, kart_half_length):
            to_remove = (powerup_x, powerup_y)
            break
    if to_remove:
        game_state_manager.powerup_positions.remove(to_remove)
        return True
    return False




def check_collision(position_x_value, position_y_value):
    return check_collision_condition(position_x_value, position_y_value)

def check_collision_condition(position_x_value, position_y_value):
    current_time = time.time()
    if current_time - game_state_manager.last_collision_time < 0.5:
        return False
    kart_x = position_x_value
    kart_y = position_y_value
    kart_half_width = 1.9
    kart_half_length = 2.5
    half_cone_size = cone_base_length / 2
    for cone_x, cone_y in game_state_manager.cone_positions:
        if abs(kart_x - cone_x) < kart_half_width + half_cone_size and abs(kart_y - cone_y) < kart_half_length + half_cone_size:
            return True
    for pothole_x, pothole_y in game_state_manager.pothole_positions:
        dist = math.sqrt((kart_x - pothole_x) ** 2 + (kart_y - pothole_y) ** 2)
        if dist < pothole_radius + max(kart_half_width, kart_half_length):
            return True
    return False

def is_in_water(position_x_value, position_y_value):
    norm_x_inner = position_x_value / track_inner_radius_x
    norm_y_inner = position_y_value / track_inner_radius_y
    inner_dist = math.sqrt(norm_x_inner ** 2 + norm_y_inner ** 2)
    return inner_dist < 1.0

def is_on_track(position_x_value, position_y_value):
    norm_x = position_x_value / track_outer_radius_x
    norm_y = position_y_value / track_outer_radius_y
    outer_dist = math.sqrt(norm_x ** 2 + norm_y ** 2)
    norm_x_inner = position_x_value / track_inner_radius_x
    norm_y_inner = position_y_value / track_inner_radius_y
    inner_dist = math.sqrt(norm_x_inner ** 2 + norm_y_inner ** 2)
    return outer_dist <= 1.0 and inner_dist >= 1.0

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_screen_width / window_screen_height, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    setup_camera_condition()


def setup_camera_condition():
    if game_state_manager.is_first_person_view:
        pass
    else:
        angle_rad = math.radians(game_state_manager.vehicle_angle + game_state_manager.camera_angle_offset)
        if game_state_manager.selected_vehicle_type == 'car':
            cam_x = game_state_manager.vehicle_position_x - game_state_manager.camera_distance * math.cos(angle_rad)
            cam_y = game_state_manager.vehicle_position_y - game_state_manager.camera_distance * math.sin(angle_rad)
            camera_height = game_state_manager.camera_height + 6
            look_x = game_state_manager.vehicle_position_x + math.cos(angle_rad) * 5
            look_y = game_state_manager.vehicle_position_y + math.sin(angle_rad) * 5
            look_z = track_surface_height + 2.5
        elif game_state_manager.selected_vehicle_type == 'bike':
            cam_x = game_state_manager.vehicle_position_x - game_state_manager.camera_distance * 1.5 * math.cos(angle_rad)
            cam_y = game_state_manager.vehicle_position_y - game_state_manager.camera_distance * 1.5 * math.sin(angle_rad)
            camera_height = game_state_manager.camera_height + 12
            look_x = game_state_manager.vehicle_position_x + math.cos(angle_rad) * 6
            look_y = game_state_manager.vehicle_position_y + math.sin(angle_rad) * 6
            look_z = track_surface_height + 3.5
        gluLookAt(cam_x, cam_y, camera_height, look_x, look_y, look_z, 0, 0, 1)

def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_screen_width, 0, window_screen_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(10, window_screen_height - 50)
    glVertex2f(10 + game_state_manager.player_health * 2, window_screen_height - 50)
    glVertex2f(10 + game_state_manager.player_health * 2, window_screen_height - 70)
    glVertex2f(10, window_screen_height - 70)
    glEnd()
    speed = abs(game_state_manager.vehicle_speed)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)
    glVertex2f(10, window_screen_height - 110)
    glVertex2f(10 + speed * 50, window_screen_height - 110)
    glVertex2f(10 + speed * 50, window_screen_height - 130)
    glVertex2f(10, window_screen_height - 130)
    glEnd()
    draw_text(10, window_screen_height - 30, f'Health: {game_state_manager.player_health}%')
    draw_text(10, window_screen_height - 90, f'Speed: {speed:.1f}')
    draw_text(window_screen_width - 150, window_screen_height - 30, f'Laps: {game_state_manager.laps_completed_count}/5')
    draw_hud_condition()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_hud_condition():
    if game_state_manager.game_start_time:
        if game_state_manager.is_game_over and game_state_manager.game_final_time is not None:
            time_remaining = game_state_manager.game_final_time
        else:
            time_remaining = max(0, game_total_time - (time.time() - game_state_manager.game_start_time))
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        draw_text(window_screen_width - 150, window_screen_height - 50, f'Time: {minutes:02d}:{seconds:02d}')
    if game_state_manager.is_powerup_active:
        powerup_time_left = max(0, powerup_effect_duration - game_state_manager.powerup_timer)
        draw_text(10, window_screen_height - 150, f'Speed Boost: {powerup_time_left:.1f}s')
    if game_state_manager.is_game_over:
        if game_state_manager.laps_completed_count >= required_laps_count:
            draw_text(window_screen_width / 2 - 50, window_screen_height / 2 + 10, 'winner winner chicken dinner!')
        else:
            draw_text(window_screen_width / 2 - 60, window_screen_height / 2 + 10, 'Game Over!')
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 0.0)
        glVertex2f(window_screen_width / 2 - 150, window_screen_height / 2 - 50)
        glVertex2f(window_screen_width / 2 + 150, window_screen_height / 2 - 50)
        glVertex2f(window_screen_width / 2 + 150, window_screen_height / 2 + 50)
        glVertex2f(window_screen_width / 2 - 150, window_screen_height / 2 + 50)
        glEnd()



def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_screen_width, 0, window_screen_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    draw_text(window_screen_width / 2 - 60, window_screen_height / 2 + 50, 'Select Vehicle:')
    draw_text(window_screen_width / 2 - 60, window_screen_height / 2 + 10, "Press 'b' for Bike")
    draw_text(window_screen_width / 2 - 60, window_screen_height / 2 - 30, "Press 'c' for Car")
    glMatrixMode(GL_PROJECTION)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(window_screen_width / 2 - 200, window_screen_height / 2 - 100)
    glVertex2f(window_screen_width / 2 + 200, window_screen_height / 2 - 100)
    glVertex2f(window_screen_width / 2 + 200, window_screen_height / 2 + 100)
    glVertex2f(window_screen_width / 2 - 200, window_screen_height / 2 + 100)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_text(position_x_value, position_y_value, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_screen_width, 0, window_screen_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(position_x_value, position_y_value)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


    



def draw_vehicle():
    if game_state_manager.respawn_timer <= 0 or (game_state_manager.is_flicker_active and game_state_manager.flicker_total_count % 2 == 0):
        glPushMatrix()
        if game_state_manager.selected_vehicle_type == 'car':
            glTranslatef(game_state_manager.vehicle_position_x, game_state_manager.vehicle_position_y, track_surface_height + 1.5)
        else:
            glTranslatef(game_state_manager.vehicle_position_x, game_state_manager.vehicle_position_y, track_surface_height + 4.5)
        if game_state_manager.selected_vehicle_type == 'car':
            glRotatef(90, 0, 0, 1)
    
        glRotatef(game_state_manager.vehicle_angle, 0, 0, 1)
        glRotatef(90.0, 0, 0, 1)
        if game_state_manager.selected_vehicle_type == 'car':
            glScalef(0.15, 0.15, 0.15)
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            glTranslatef(0, -10, 20)
            glScalef(35, 40, 15)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            glTranslatef(0, -40, 15)
            glScalef(38, 20, 10)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            glTranslatef(0, 14, 15)
            glScalef(38, 10, 10)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(0.3, 0.3, 0.8)
            glPushMatrix()
            glTranslatef(0, -30, 25)
            glRotatef(-45, 1, 0, 0)
            glScalef(34, 1, 10)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(0.3, 0.3, 0.8)
            glPushMatrix()
            glTranslatef(0, 12, 25)
            glRotatef(45, 1, 0, 0)
            glScalef(34, 1, 10)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(1.0, 1.0, 1.0)
            glPushMatrix()
            glTranslatef(-15, -50, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(15, -50, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(1.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-15, 20, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(15, 20, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-22, -35, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(-17, -35, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)
            glTranslatef(0.0, 0.0, 0.5)
            glColor3f(0.5, 0.5, 0.5)
            gluSphere(gluNewQuadric(), 2.0, 10, 10)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(22, -35, 0)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(17, -35, 0)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)
            glTranslatef(0.0, 0.0, 0.5)
            glColor3f(0.5, 0.5, 0.5)
            gluSphere(gluNewQuadric(), 2.0, 10, 10)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-22, 13, 0.5)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(-17, 13, 0.5)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)
            glTranslatef(0.0, 0.0, 0.5)
            glColor3f(0.5, 0.5, 0.5)
            gluSphere(gluNewQuadric(), 2.0, 10, 10)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(22, 13, 0.5)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(17, 13, 0.5)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)
            glTranslatef(0.0, 0.0, 0.5)
            glColor3f(0.5, 0.5, 0.5)
            gluSphere(gluNewQuadric(), 2.0, 10, 10)
            glPopMatrix()
        elif game_state_manager.selected_vehicle_type == 'bike':
            glScalef(0.1, 0.1, 0.1)
            glRotatef(game_state_manager.bike_lean_angle_state, 1, 0, 0)
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(0, 0, 30)
            glPushMatrix()
            glTranslatef(20, 0, 20)
            glRotatef(-15, 0, 1, 0)
            glScalef(3.0, 0.6, 0.6)
            glutSolidCube(40)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(20, 0, 0)
            glRotatef(-25, 0, 1, 0)
            glScalef(2.5, 0.5, 0.5)
            glutSolidCube(40)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-30, 0, 20)
            glRotatef(30, 0, 1, 0)
            glScalef(2.0, 0.5, 0.5)
            glutSolidCube(40)
            glPopMatrix()
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-25, 0, 50)
            glScalef(1.8, 0.8, 0.3)
            glutSolidCube(35)
            glPopMatrix()
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(70, 0, 25)
            glRotatef(60, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 4, 4, 55, 10, 10)
            glPopMatrix()
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(70, 0, 30)
            glRotatef(60, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6, 6, 45, 10, 10)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(80, 0, 75)
            glColor3f(0.7, 0.7, 0.7)
            glutSolidCube(10)
            glPushMatrix()
            glTranslatef(0, -25, 0)
            glRotatef(90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2)
            gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 2)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(0, 25, 0)
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2)
            gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 2)
            glPopMatrix()
            glPopMatrix()
            glColor3f(0.3, 0.3, 0.3)
            glPushMatrix()
            glTranslatef(0, 0, 15)
            glScalef(1.0, 0.8, 0.8)
            glutSolidCube(40)
            glPushMatrix()
            glTranslatef(0, 0, 25)
            glColor3f(0.4, 0.4, 0.4)
            glScalef(0.8, 0.7, 0.5)
            glutSolidCube(30)
            glPopMatrix()
            glPopMatrix()
            glColor3f(0.5, 0.5, 0.5)
            glPushMatrix()
            glTranslatef(-10, 0, 20)
            glRotatef(70, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 5, 5, 30, 8, 2)
            glPopMatrix()
            glColor3f(0.6, 0.6, 0.6)
            glPushMatrix()
            glTranslatef(-40, 0, 15)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 7, 8, 60, 10, 3)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(90, 0, 0)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 45, 45, 8, 20, 5)
            glColor3f(0.75, 0.75, 0.75)
            glTranslatef(0.0, 0.0, 0.5)
            gluCylinder(gluNewQuadric(), 15.0, 15.0, 0.5, 10, 1)
            glTranslatef(0.0, 0.0, 0.25)
            glColor3f(0.6, 0.6, 0.6)
            gluSphere(gluNewQuadric(), 5.0, 10, 10)
            glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-75, 4.65, 0)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 35, 35, 8, 20, 5)
            glColor3f(0.75, 0.75, 0.75)
            glTranslatef(0, 0, 4)
            glTranslatef(0.0, 0.0, 0.5)
            gluCylinder(gluNewQuadric(), 15.0, 15.0, 0.5, 10, 1)
            glTranslatef(0.0, 0.0, 0.25)
            glColor3f(0.6, 0.6, 0.6)
            gluSphere(gluNewQuadric(), 5.0, 10, 10)
            glPopMatrix()
            glColor3f(0.8, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(20, 0, 60)
            glPushMatrix()
            glScalef(1.8, 1.0, 0.8)
            glutSolidCube(30)
            glPopMatrix()
            glTranslatef(0, 0, 15)
            glScalef(1.8, 1.0, 0.3)
            glutSolidCube(30)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(95, 0, 40)
            glRotatef(20, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 15, 13, 10, 16, 4)
            glColor3f(0.9, 0.9, 0.7)
            glTranslatef(0, 0, 9)
            glRotatef(90, 0, 1, 0)
            glScalef(13.0, 13.0, 0.5)
            gluSphere(gluNewQuadric(), 1.0, 16, 16)
            glPopMatrix()
            glColor3f(0.8, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-80, 0, 40)
            glScalef(0.3, 1.0, 0.5)
            glutSolidCube(15)
            glPopMatrix()
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-20, 15, 30)
            glRotatef(15, 0, 0, 1)
            glScalef(1.5, 0.1, 0.8)
            glutSolidCube(40)
            glPopMatrix()
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-20, -15, 30)
            glRotatef(-15, 0, 0, 1)
            glScalef(1.5, 0.1, 0.8)
            glutSolidCube(40)
            glPopMatrix()
        glPopMatrix()

def draw_banana_pills():
    segments = 12
    draw_banana_pills_loop(segments)

def draw_banana_pills_loop(segments):
    for position_x_value, position_y_value in game_state_manager.banana_trap_positions:
        glPushMatrix()
        glTranslatef(position_x_value, position_y_value, track_surface_height + 0.05)
        glColor3f(1.0, 0.5, 0.0)
        glBegin(GL_QUADS)
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = banana_trap_radius * math.cos(angle1)
            py1 = banana_trap_radius * math.sin(angle1)
            px2 = banana_trap_radius * math.cos(angle2)
            py2 = banana_trap_radius * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()



def draw_powerdowns():
    segments = 12
    for position_x_value, position_y_value in game_state_manager.powerdown_positions:
        glPushMatrix()
        glTranslatef(position_x_value, position_y_value, track_surface_height + 0.05)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = powerdown_radius * math.cos(angle1)
            py1 = powerdown_radius * math.sin(angle1)
            px2 = powerdown_radius * math.cos(angle2)
            py2 = powerdown_radius * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

def draw_powerups():
    segments = 12
    for position_x_value, position_y_value in game_state_manager.powerup_positions:
        glPushMatrix()
        glTranslatef(position_x_value, position_y_value, track_surface_height + 0.05)
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = powerup_radius * math.cos(angle1)
            py1 = powerup_radius * math.sin(angle1)
            px2 = powerup_radius * math.cos(angle2)
            py2 = powerup_radius * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

def draw_potholes():
    segments = 12
    for position_x_value, position_y_value in game_state_manager.pothole_positions:
        glPushMatrix()
        glTranslatef(position_x_value, position_y_value, track_surface_height + 0.05)
        glColor3f(0.5, 0.3, 0.1)
        glBegin(GL_QUADS)
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = pothole_radius * math.cos(angle1)
            py1 = pothole_radius * math.sin(angle1)
            px2 = pothole_radius * math.cos(angle2)
            py2 = pothole_radius * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

def draw_cones():
    segments = 12
    for position_x_value, position_y_value in game_state_manager.cone_positions:
        glPushMatrix()
        glTranslatef(position_x_value, position_y_value, track_surface_height)
        base_height = 2
        half_size = cone_base_length / 2
        glColor3f(1.0, 0.5, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(-half_size, half_size, base_height)
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(half_size, half_size, 0)
        glVertex3f(-half_size, half_size, 0)
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(-half_size, half_size, base_height)
        glVertex3f(-half_size, half_size, 0)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(half_size, half_size, 0)
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(-half_size, half_size, 0)
        glVertex3f(-half_size, half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(half_size, half_size, 0)
        glEnd()
        num_stripes = 4
        section_height = cone_height_size / (num_stripes * 2)
        for i in range(num_stripes * 2):
            z_bottom = base_height + i * section_height
            z_top = base_height + (i + 1) * section_height
            radius_bottom = cone_base_length / 2 * (1 - (z_bottom - base_height) / cone_height_size)
            radius_top = cone_base_length / 2 * (1 - (z_top - base_height) / cone_height_size)
            if i % 2 == 0:
                glColor3f(1.0, 0.5, 0.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            for j in range(segments):
                angle1 = 2.0 * math.pi * j / segments
                angle2 = 2.0 * math.pi * (j + 1) / segments
                x_bottom1 = radius_bottom * math.cos(angle1)
                y_bottom1 = radius_bottom * math.sin(angle1)
                x_bottom2 = radius_bottom * math.cos(angle2)
                y_bottom2 = radius_bottom * math.sin(angle2)
                x_top1 = radius_top * math.cos(angle1)
                y_top1 = radius_top * math.sin(angle1)
                x_top2 = radius_top * math.cos(angle2)
                y_top2 = radius_top * math.sin(angle2)
                glVertex3f(x_bottom1, y_bottom1, z_bottom)
                glVertex3f(x_bottom2, y_bottom2, z_bottom)
                glVertex3f(x_top2, y_top2, z_top)
                glVertex3f(x_top1, y_top1, z_top)
            glEnd()
        glPopMatrix()

def draw_oval_track():
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    for i in range(track_segment_count):
        angle1 = 2.0 * math.pi * i / track_segment_count
        angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
        inner_x1 = track_inner_radius_x * math.cos(angle1)
        inner_y1 = track_inner_radius_y * math.sin(angle1)
        inner_x2 = track_inner_radius_x * math.cos(angle2)
        inner_y2 = track_inner_radius_y * math.sin(angle2)
        glVertex3f(inner_x1, inner_y1, 0)
        glVertex3f(inner_x2, inner_y2, 0)
        glVertex3f(inner_x2, inner_y2, track_surface_height)
        glVertex3f(inner_x1, inner_y1, track_surface_height)
        outer_x1 = track_outer_radius_x * math.cos(angle1)
        outer_y1 = track_outer_radius_y * math.sin(angle1)
        outer_x2 = track_outer_radius_x * math.cos(angle2)
        outer_y2 = track_outer_radius_y * math.sin(angle2)
        glVertex3f(outer_x1, outer_y1, 0)
        glVertex3f(outer_x2, outer_y2, 0)
        glVertex3f(outer_x2, outer_y2, track_surface_height)
        glVertex3f(outer_x1, outer_y1, track_surface_height)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.5, 1.0)
    for i in range(track_segment_count):
        angle1 = 2.0 * math.pi * i / track_segment_count
        angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
        inner_x1 = track_inner_radius_x * math.cos(angle1)
        inner_y1 = track_inner_radius_y * math.sin(angle1)
        inner_x2 = track_inner_radius_x * math.cos(angle2)
        inner_y2 = track_inner_radius_y * math.sin(angle2)
        glVertex3f(0, 0, track_surface_height)
        glVertex3f(inner_x1, inner_y1, track_surface_height)
        glVertex3f(inner_x2, inner_y2, track_surface_height)
        glVertex3f(0, 0, track_surface_height)
    glEnd()
    glBegin(GL_QUADS)
    for i in range(track_segment_count):
        angle1 = 2.0 * math.pi * i / track_segment_count
        angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
        inner_x1 = track_inner_radius_x * math.cos(angle1)
        inner_y1 = track_inner_radius_y * math.sin(angle1)
        outer_x1 = track_outer_radius_x * math.cos(angle1)
        outer_y1 = track_outer_radius_y * math.sin(angle1)
        inner_x2 = track_inner_radius_x * math.cos(angle2)
        inner_y2 = track_inner_radius_y * math.sin(angle2)
        outer_x2 = track_outer_radius_x * math.cos(angle2)
        outer_y2 = track_outer_radius_y * math.sin(angle2)
        glColor3f(0.3, 0.3, 0.3)
        glVertex3f(outer_x1, outer_y1, track_surface_height)
        glVertex3f(inner_x1, inner_y1, track_surface_height)
        glVertex3f(inner_x2, inner_y2, track_surface_height)
        glVertex3f(outer_x2, outer_y2, track_surface_height)
    glEnd()
    glBegin(GL_LINES)
    for i in range(track_segment_count):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.0, 0.0, 0.0)
            angle1 = 2.0 * math.pi * i / track_segment_count
            angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
            outer_x1 = track_outer_radius_x * math.cos(angle1)
            outer_y1 = track_outer_radius_y * math.sin(angle1)
            outer_x2 = track_outer_radius_x * math.cos(angle2)
            outer_y2 = track_outer_radius_y * math.sin(angle2)
            glVertex3f(outer_x1, outer_y1, track_surface_height + 0.1)
            glVertex3f(outer_x2, outer_y2, track_surface_height + 0.1)
    glEnd()
    glBegin(GL_LINES)
    for i in range(track_segment_count):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 1.0)
            else:
                glColor3f(0.0, 0.0, 0.0)
            angle1 = 2.0 * math.pi * i / track_segment_count
            angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
            inner_x1 = track_inner_radius_x * math.cos(angle1)
            inner_y1 = track_inner_radius_y * math.sin(angle1)
            inner_x2 = track_inner_radius_x * math.cos(angle2)
            inner_y2 = track_inner_radius_y * math.sin(angle2)
            glVertex3f(inner_x1, inner_y1, track_surface_height + 0.1)
            glVertex3f(inner_x2, inner_y2, track_surface_height + 0.1)
    glEnd()
    curb_width = 10
    glBegin(GL_QUADS)
    for i in range(track_segment_count):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 0.0)
            else:
                glColor3f(0.2, 0.2, 0.8)
            angle1 = 2.0 * math.pi * i / track_segment_count
            angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
            outer_x1 = (track_outer_radius_x + curb_width) * math.cos(angle1)
            outer_y1 = (track_outer_radius_y + curb_width) * math.sin(angle1)
            outer_x2 = (track_outer_radius_x + curb_width) * math.cos(angle2)
            outer_y2 = (track_outer_radius_y + curb_width) * math.sin(angle2)
            curb_x1 = track_outer_radius_x * math.cos(angle1)
            curb_y1 = track_outer_radius_y * math.sin(angle1)
            curb_x2 = track_outer_radius_x * math.cos(angle2)
            curb_y2 = track_outer_radius_y * math.sin(angle2)
            glVertex3f(curb_x1, curb_y1, track_surface_height + 0.2)
            glVertex3f(curb_x2, curb_y2, track_surface_height + 0.2)
            glVertex3f(outer_x2, outer_y2, track_surface_height + 0.2)
            glVertex3f(outer_x1, outer_y1, track_surface_height + 0.2)
    glEnd()
    glBegin(GL_QUADS)
    for i in range(track_segment_count):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            angle1 = 2.0 * math.pi * i / track_segment_count
            angle2 = 2.0 * math.pi * (i + 1) / track_segment_count
            inner_x1 = (track_inner_radius_x - curb_width) * math.cos(angle1)
            inner_y1 = (track_inner_radius_y - curb_width) * math.sin(angle1)
            inner_x2 = (track_inner_radius_x - curb_width) * math.cos(angle2)
            inner_y2 = (track_inner_radius_y - curb_width) * math.sin(angle2)
            curb_x1 = track_inner_radius_x * math.cos(angle1)
            curb_y1 = track_inner_radius_y * math.sin(angle1)
            curb_x2 = track_inner_radius_x * math.cos(angle2)
            curb_y2 = track_inner_radius_y * math.sin(angle2)
            glVertex3f(curb_x1, curb_y1, track_surface_height + 0.2)
            glVertex3f(curb_x2, curb_y2, track_surface_height + 0.2)
            glVertex3f(inner_x2, inner_y2, track_surface_height + 0.2)
            glVertex3f(inner_x1, inner_y1, track_surface_height + 0.2)
    glEnd()
    glBegin(GL_QUADS)
    finish_line_angle = 0
    inner_x = track_inner_radius_x * math.cos(finish_line_angle)
    inner_y = track_inner_radius_y * math.sin(finish_line_angle)
    outer_x = track_outer_radius_x * math.cos(finish_line_angle)
    outer_y = track_outer_radius_y * math.sin(finish_line_angle)
    track_direction_x = -math.sin(finish_line_angle)
    track_direction_y = math.cos(finish_line_angle)
    line_length = 30
    rows = 5
    cols = 5
    track_lane_width = math.sqrt((outer_x - inner_x) ** 2 + (outer_y - inner_y) ** 2)
    square_width = track_lane_width / cols
    square_height = line_length / rows
    for row in range(rows):
        for col in range(cols):
            pos_factor = col / cols
            base_x = inner_x + (outer_x - inner_x) * pos_factor
            base_y = inner_y + (outer_y - inner_y) * pos_factor
            next_pos_factor = (col + 1) / cols
            next_x = inner_x + (outer_x - inner_x) * next_pos_factor
            next_y = inner_y + (outer_y - inner_y) * next_pos_factor
            row_start = -line_length / 2 + row * square_height
            row_end = -line_length / 2 + (row + 1) * square_height
            if (row + col) % 2 == 0:
                glColor3f(0.0, 0.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            x1 = base_x + track_direction_x * row_start
            y1 = base_y + track_direction_y * row_start
            x2 = next_x + track_direction_x * row_start
            y2 = next_y + track_direction_y * row_start
            x3 = next_x + track_direction_x * row_end
            y3 = next_y + track_direction_y * row_end
            x4 = base_x + track_direction_x * row_end
            y4 = base_y + track_direction_y * row_end
            glVertex3f(x1, y1, track_surface_height + 0.1)
            glVertex3f(x2, y2, track_surface_height + 0.1)
            glVertex3f(x3, y3, track_surface_height + 0.1)
            glVertex3f(x4, y4, track_surface_height + 0.1)
    glEnd()

def draw_grid():
    cell_size = track_grid_size / track_grid_divisions
    half_grid = track_grid_size / 2
    glBegin(GL_QUADS)
    for i in range(-track_grid_divisions // 2, track_grid_divisions // 2):
        for j in range(-track_grid_divisions // 2, track_grid_divisions // 2):
            x1 = i * cell_size
            y1 = j * cell_size
            x2 = (i + 1) * cell_size
            y2 = (j + 1) * cell_size
            if (i + j) % 2 == 0:
                glColor3f(0.4, 0.8, 0.4)
            else:
                glColor3f(0.0, 0.5, 0.0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()
    wall_height = 50
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, wall_height)
    glVertex3f(-half_grid, half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, 0)
    glVertex3f(half_grid, -half_grid, 0)
    glVertex3f(half_grid, -half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, 0)
    glVertex3f(-half_grid, half_grid, 0)
    glVertex3f(-half_grid, half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, wall_height)
    glVertex3f(half_grid, -half_grid, 0)
    glVertex3f(half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, wall_height)
    glVertex3f(half_grid, -half_grid, wall_height)
    glEnd()

def init():
    glClearColor(0.529, 0.808, 0.922, 1.0)
    glEnable(GL_DEPTH_TEST)
if __name__ == '__main__':
    main()