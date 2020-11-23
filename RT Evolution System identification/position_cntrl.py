import numpy as np
import time
import math
from manoeuvre_model_evo import ship_model
from ship_class import ship
from pid_small import PID
import matplotlib.pyplot as plt

def azimuth(point1, point2):
    angle = np.arctan2(point2[0] - point1[0], point2[1] - point1[1])
    return np.degrees(angle) if angle >= 0 else np.degrees(angle) + 360
    #add thrust fraction here
    
coef_ = np.genfromtxt('foo_evo_general.csv', delimiter=',')
acc_lim = np.genfromtxt('acc_limits.csv', delimiter=',')

# P_range = np.arange(0,10.2,0.2)
# I_range = np.arange(0,10.2,0.2)
# D_range = np.arange(0,10.2,0.2)

x = np.arange(0,90.5, 0.5)
y = 2.5+np.log(x**0.6)
coefs = np.polynomial.polynomial.polyfit(x[1:],y[1:],3)
ffit = np.polynomial.polynomial.polyval(x, coefs)


fit_function = np.polynomial.polynomial.Polynomial(coefs)    # instead of np.poly1d
# plt.plot(y)
# plt.plot(fit_function(x))

#initialise ship
u, v, r, hdg = 0.0,0,0,0
ship_ = ship()
ship_model_ = ship_model(0,0,0, ship_, coef_,acc_lim)

# (distance, time)
#(zometeen x,y,time)
input_ = [(0,0,0), (50.,50., 2)]#, (50., 100., 100)]#,(100., 100., 200),(100., 0., 300)]#], (0., 100., 180)]#, (0., 0., 190)]#, (20,70), (10, 150)]
end_input = 0
input_position = 0
current_input_setting = 0
t = 0
dt = 0.4 #future noise
t_end = 200
pid_position_x = PID(P=0.1, I=0.0, D=2.918, Ibounds_speed=(-90,90))
pid_position_y = PID(P=0.1, I=0.0, D=2.918, Ibounds_speed=(-90,90))

pid_line_correction = PID(P=0.0, I=0.0, D=0., Ibounds_speed=(-90,90))
# pid_position_x = PID(P=1.0, I=.0, D=10.0, Ibounds_speed=(-90,90))
# pid_position_y = PID(P=1.0, I=.0, D=10.0, Ibounds_speed=(-90,90))

# pid_line_correction = PID(P=2.0, I=.0, D=8., Ibounds_speed=(-90,90))
# pid_line_correction.setPoint_position(0)

x, x_old = 0, 0 
y, y_old = 0, 0

rpm_1, rpm_2 = 0,0
#
input_ref = []
position_real = []
traj_x, traj_y, hdg_list = [], [], []
x = 0
a = None
traj_angle_position = 0
while t<t_end:
    # calculate speed input
    # print(end_input)
    if end_input==0:
        if input_[input_position+1][2] <= t:
            # print(input_position)
            current_input_setting_x = input_[input_position+1][0]
            current_input_setting_y = input_[input_position+1][1]
            
            traj_angle_position = azimuth((x,y), (input_[input_position+1][0],input_[input_position+1][1]))
            
            # def function_check_side(x, y):
            #     m = (input_[input_position+1][1]-input_[input_position][1])/(input_[input_position+1][0]-input_[input_position][0])
            #     slope = -1/m
            #     b = input_[input_position+1][1] - slope*input_[input_position+1][0]
                
            #     second_point_x, second_point_y = input_[input_position+1][0]+10, (input_[input_position+1][0]+10)*slope + b
            #     v1 = (input_[input_position+1][0]-second_point_x, input_[input_position+1][1]-second_point_y)   # Vector 1
            #     v2 = (input_[input_position+1][0]-x, input_[input_position+1][1]-y)   # Vector 1
            #     xp = v1[0]*v2[1] - v1[1]*v2[0]  # Cross product
            #     if xp > 0:
            #         return -1
            #     else:
            #         return 1
            # a = function_check_side(x, y)
            # print(a)
            # print(function_check_side(x, y))
            print(traj_angle_position)
            # print(current_input_setting_x)
            # print('a', current_input_setting, input_position,x,y)
            # print(input_[input_position][0] - x)
            pid_position_x.setPoint_position(current_input_setting_x)
            pid_position_y.setPoint_position(current_input_setting_y)
            input_position += 1
            if input_position==len(input_)-1:
                end_input = 1
                # print('here')
                
                # input_position -= 1 
            
    # print(np.sqrt(((input_[input_position][0] - x)**2)+((input_[input_position][1] - y)**2)))    
    # if t%10==0:
    #     pid_position.setPoint_position(np.sqrt((input_[input_position][0]-x)**2 + (input_[input_position][1]-y)**2)) 
    
    control_input_line_correction = pid_line_correction.update((traj_angle_position - azimuth((x,y), (input_[input_position][0],input_[input_position][1]))), dt)
    sign_control_resultant = 1
    
    # if a:
    #     input_position -= 1
    #     check_side = function_check_side(x, y)
    #     input_position += 1
    #     if a!=check_side:
    #         sign_control_resultant = -1
            # sign_control_resultant = np.sign(control_input_x+control_input_x)  
            
    
    
    control_input_x = pid_position_x.update(x, dt)
    control_input_y = pid_position_y.update(y, dt)
    sign_control_input_x = np.sign(control_input_x)
    sign_control_input_y = np.sign(control_input_y)
    # if control_input_x<0.0 or control_input_y<0.0:
        
    #     control_input_line_correction = -1*pid_line_correction.update((traj_angle_position - azimuth((x,y), (input_[input_position][0],input_[input_position][1]))), dt)
    # else:
        

    direction_gen_x = azimuth((x,0), (input_[input_position][0],0))
    direction_gen_y = azimuth((0,y), (0,input_[input_position][1]))
    
    direction_gen_delta = abs(direction_gen_x-direction_gen_y)
    if direction_gen_delta >360.0:
        direction_gen_delta = direction_gen_delta%360.0
    elif direction_gen_delta<0.0:
        direction_gen_delta = direction_gen_delta+360
        
      
    control_input_resultant =  np.sqrt(control_input_x**2 + control_input_y**2 + 2*control_input_x*control_input_y*np.cos(np.deg2rad(direction_gen_delta)))
    
    
    
    angle_resultant =  np.rad2deg(np.arctan((control_input_y*np.sin(np.deg2rad(direction_gen_delta)))/(control_input_x+control_input_y*np.cos(np.deg2rad(direction_gen_delta)))))
    angle_resultant = direction_gen_x-angle_resultant
    if math.isnan(angle_resultant):
        angle_resultant=0
    # print(control_input_resultant, angle_resultant)
    # print(control_input_line_correction, angle_resultant)
    az_deflection = control_input_resultant
    
    # print(az_deflection)
    rpm_1 = fit_function(abs(az_deflection))
    rpm_2 = fit_function(abs(az_deflection))
    rsa_1 = (angle_resultant-hdg) - 90 + 180 + az_deflection + control_input_line_correction
    rsa_2 = (angle_resultant-hdg) + 90 + 180 - az_deflection +  control_input_line_correction
    
    
    
    # print(rsa1,rsa_2)
    if abs(az_deflection)>abs(40.):
        az_deflection = np.sign(az_deflection)*abs(40)
        rsa_1 = (angle_resultant-hdg) - 90 + 180 + az_deflection +control_input_line_correction
        rsa_2 = (angle_resultant-hdg) + 90 + 180 - az_deflection +control_input_line_correction
        rpm_1 = fit_function(abs(az_deflection))
        rpm_2 = fit_function(abs(az_deflection))
    
    
    # print(control_input)
    if rsa_1>360.0:
        rsa_1 = rsa_1 - 360.0
    elif rsa_1<0.0 :
        rsa_1 = rsa_1 + 360.0
    if rsa_2>360.0:
        rsa_2 = rsa_2 - 360.0
    elif rsa_2<0.0 :
        rsa_2 = rsa_2 + 360.0
    # print(rsa_1,rsa_2)
    # calculate speed control iput
    # if abs(abs(control_input)-abs(rpm))/dt>max_rpm_second:
        
    #     rpm = dt*sign_control_input*max_rpm_second + rpm
    # print(np.sqrt(((input_[input_position][0] - x)**2)+((input_[input_position][1] - y)**2)), control_input, direction_gen,az_deflection, hdg)

    # print(control_input_line_correction)
    # model
    u, v, r, hdg, delta_x_0, delta_y_0, delta_r_0, u_dot, v_dot, r_dot = ship_model_.manoeuvre_model_rt_evolution(u, v, r, hdg,
                                                                                               0., rpm_1, rpm_2,
                                                                                               180., rsa_1, rsa_2,
                                                                                               dt
                                                                                              )
    # print(u)
    # print('-', az_deflection, direction_gen)

    x = x + delta_x_0
    y = y+ delta_y_0
    input_ref.append(current_input_setting)
    # position_real.append(np.sqrt(((input_[input_position][0] - x)**2)+((input_[input_position][1] - y)**2)))
    # position_real.append(y)
    traj_x.append(x)
    traj_y.append(y)
    hdg_list.append(np.sqrt(u**2+v**2))
    # hdg_list.append(hdg)

    t = t + dt

input_ref_array = np.asarray(input_ref)
position_real_array = np.asarray(position_real)

# control_score = abs(input_ref_array-position_real_array)
# control_score = control_score.sum()

# print(control_score)

# plt.plot(input_ref_array)

plt.plot(traj_x, traj_y)
plt.scatter([0,50,50,100,100], [0,50,100,100,0])
# plt.plot(rpm_set)

plt.savefig('tuner.png')
plt.show()
plt.close()

plt.plot(hdg_list)
plt.show()

