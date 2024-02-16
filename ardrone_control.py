from pyardrone import ARDrone
from pyardrone.at import CONFIG

from keyboard import add_hotkey
from math import sin, cos, pi
import pygame

pygame.init()

drone = ARDrone()

drone.navdata_ready.wait()  # wait until NavData is ready
print("navdata ready")

drone.send(CONFIG('general:navdata_demo', True))
drone.send(CONFIG('', True))

pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)

def takeoff():
    drone.takeoff()
    print("takeoff")
    
def land():
    drone.land()
    print("land")
    
def emergency():
    drone.emergency()
    print("emergency land")
    
# Add the spacebar as an emergency landing
add_hotkey("space", emergency)

screen = pygame.display.set_mode((1000,1000))
font = pygame.font.SysFont("arial", 20)
font_bold = pygame.font.SysFont("arial", 24, True)

# Alititude meter drawing
alt_meter = pygame.surface.Surface((200,200), pygame.SRCALPHA)

pygame.draw.circle(alt_meter, (0,0,0), (100,100), 100)
pygame.draw.circle(alt_meter, (100,100,100), (100,100), 100, 10)
pygame.draw.circle(alt_meter, (255,255,255), (100,100), 8)
for height in range(0,10):
    height = height/10
    pygame.draw.line(alt_meter, (255,255,255), (100+(sin(pi*height*2)*70), 100-(cos(pi*height*2)*70)), (100+(sin(pi*height*2)*90), 100-(cos(pi*height*2)*90)), 3)

# Compass drawing
compass = pygame.surface.Surface((200,200), pygame.SRCALPHA)

pygame.draw.circle(compass, (0,0,0), (100,100), 100)
pygame.draw.circle(compass, (100,100,100), (100,100), 100, 10)
for dir in range(0,36):
    dir = dir/36
    pygame.draw.line(compass, (255,255,255), (100+(sin(pi*dir*2)*70), 100-(cos(pi*dir*2)*70)), (100+(sin(pi*dir*2)*90), 100-(cos(pi*dir*2)*90)), 1)
for dir in range(0,4):
    dir = dir/4
    pygame.draw.line(compass, (255,255,255), (100+(sin(pi*dir*2)*70), 100-(cos(pi*dir*2)*70)), (100+(sin(pi*dir*2)*90), 100-(cos(pi*dir*2)*90)), 5)

# Vertical drawing
vert_speed = pygame.surface.Surface((200,200), pygame.SRCALPHA)

pygame.draw.circle(vert_speed, (0,0,0), (100,100), 100)
pygame.draw.circle(vert_speed, (100,100,100), (100,100), 100, 10)
pygame.draw.circle(vert_speed, (255,255,255), (100,100), 8)
pygame.draw.line(vert_speed, (255,255,255), (10, 100), (40, 100), 4)
for height in range(21,35,2):
    height = height/36
    pygame.draw.line(vert_speed, (255,255,255), (100+(sin(pi*height*2)*70), 100-(cos(pi*height*2)*70)), (100+(sin(pi*height*2)*90), 100-(cos(pi*height*2)*90)), 3)

clock = pygame.time.Clock()

while 1:
    # Drone movement
    fw = 0
    bw = 0
    right = 0
    left = 0
    cw = 0
    ccw = 0
    up = 0
    down = 0
    
    left_right = round(joystick.get_axis(0),2)
    if left_right < 0:
        left = abs(left_right)
    elif left_right > 0:
        right = left_right
    
    fw_bw = round(joystick.get_axis(1),2)
    if fw_bw < 0:
        fw = abs(fw_bw)
    elif fw_bw > 0:
        bw = fw_bw
        
    cw_ccw = round(joystick.get_axis(2),2)
    if cw_ccw < 0:
        ccw = abs(cw_ccw)
    elif cw_ccw > 0:
        cw = cw_ccw
        
    up_down = round(joystick.get_axis(3),2)
    if up_down < 0:
        up = abs(up_down)
    elif up_down > 0:
        down = up_down
    
    try:
        drone.move(forward=fw, backward=bw, right=right, left=left, cw=cw, ccw=ccw, up=up, down=down)
    except Exception:
        drone.close()
        pygame.quit()
        exit()
    
    # Emergency land when both joysticks pressed
    if joystick.get_button(8) and joystick.get_button(9):
        emergency()
    
    # Battery level rendering
    if drone.state.vbat_low:
        screen.fill((80,0,0))
        screen.blit(font.render("LOW BATTERY", True, (255,255,255)), (10,10))
    
        # Land when low battery
        if drone.state.fly_mask:
            land()
        
    else:
        screen.fill((40,40,40))
        screen.blit(font.render(str(drone.navdata.demo.vbat_flying_percentage)+"%", True, (255,255,255)), (10,10))
    
    # Render speed
    screen.blit(font.render("vx:"+str(round(drone.navdata.demo.vx, 2)) + " vy:" + str(round(drone.navdata.demo.vy, 2)) + " vz:" + str(round(drone.navdata.demo.vz, 2)), True, (255,255,255)), (10,40))

    # Altitude calculation
    altitude = drone.navdata.demo.altitude*0.032808399
    
    # altitude rendering
    alt_text = font_bold.render(str(round(altitude)), True, (255,255,255))
    screen.blit(alt_meter, (650,250))
    pygame.draw.line(screen, (255,255,255), (750,350), (750+(sin(pi*altitude/1000*2)*85), 350-(cos(pi*altitude/1000*2)*85)), 7)
    pygame.draw.line(screen, (255,255,255), (750,350), (750+(sin(pi*altitude/10000*2)*50), 350-(cos(pi*altitude/10000*2)*50)), 10)
    screen.blit(alt_text, alt_text.get_rect(center=(750, 380)))
    
    # Compass calculation
    direction = 360-drone.navdata.demo.psi/1000
    
    # Compass rendering
    screen.blit(compass, (400,550))
    pygame.draw.line(screen, (255,0,0), (500,650), (500+(sin(pi*direction/360*2)*80), 650-(cos(pi*direction/360*2)*80)), 10)
    pygame.draw.line(screen, (255,255,255), (500,650), (500-(sin(pi*direction/360*2)*80), 650+(cos(pi*direction/360*2)*80)), 12)
    pygame.draw.circle(screen, (0,0,0), (500,650), 8)
    
    # Horizon calculation
    roll = -(drone.navdata.demo.phi/1000)
    pitch = drone.navdata.demo.theta/1000
    
    line_pos_1 = (500+(cos((roll/360+pitch/360)*2*pi)*95), 350+(sin((roll/360+pitch/360)*2*pi)*95))
    line_pos_2 = (500-(cos((roll/360-pitch/360)*2*pi)*95), 350-(sin((roll/360-pitch/360)*2*pi)*95))
    
    angle1 = (roll/360-pitch/360)*2*pi
    angle2 = pi+(roll/360+pitch/360)*2*pi
    
    horizon_positions = []
    for angle in range(round(angle1*100), round(angle2*100)):
        horizon_positions.append((500+(cos((angle/100)-pi))*95, 350+(sin(((angle/100)-pi)))*95))
    
    # Horizon rendering
    pygame.draw.circle(screen, (130,65,30), (500,350), 100)
    if len(horizon_positions) >= 3:
        pygame.draw.polygon(screen, (0,255,255), horizon_positions)
        
    pygame.draw.line(screen, (255,255,255), line_pos_1, line_pos_2, 5)
    
    pygame.draw.line(screen, (255,255,255), (430, 350), (410, 350), 3)
    pygame.draw.line(screen, (255,255,255), (570, 350), (590, 350), 3)
    pygame.draw.circle(screen, (100,100,100), (500,350), 100, 10)
    
    # Vertical speed calculation
    vert_spd = drone.navdata.demo.vz
    
    # Vertical speed drawing
    screen.blit(vert_speed, (650,550))
    pygame.draw.line(screen, (255,255,255), (750, 650), (750-(cos(pi*vert_spd/360*2)*80), 650-(sin(pi*vert_spd/360*2)*80)), 7)
    
    clock.tick()
    
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            drone.close()
            exit()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
                takeoff()
            elif event.button == 6:
                land()
        