#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 16:32:59 2020

@author: erwinlodder
"""
import numpy as np
import time
from manoeuvre_model_rpa3 import ship_model
from ship_class import ship
from pid_small import PID
import matplotlib.pyplot as plt
ship = ship()
coef_ = np.genfromtxt('foo_rpa3.csv', delimiter=',')





P_range = np.arange(0,10.2,0.2)
I_range = np.arange(0,10.2,0.2)
D_range = np.arange(0,10.2,0.2)

#initialise ship
u, v, r, hdg = 0,0,0,0
ship_model = ship_model(0,0,0, ship, coef_)
max_rpm_second = 0.5
rpm = 0 




# (speed, time)
speed_u = [(0, 0), (5, 20), (9, 140), (2, 250)]
end_input = 0
speed_u_position = 0
current_speed_setting = 0
t = 0
dt = 0.4 #future noise
t_end = 400
pid_speed = PID(P=25.6, I=-0.04646, D=2.653)

#
u_ref = []
u_real = []
rpm_set = []
while t<t_end:
    # calculate speed input
    if end_input==0:
        if speed_u[speed_u_position][1] <= t:
            
            current_speed_setting = speed_u[speed_u_position][0]
            pid_speed.setPoint_speed(current_speed_setting)
            speed_u_position += 1
            if speed_u_position==len(speed_u):
                end_input  = 1
        
        
        
    control_input = pid_speed.update(u)
    sign_control_input = np.sign(control_input)
    # calculate speed control iput
    if abs(abs(control_input)-abs(rpm))/dt>max_rpm_second:
        
        rpm = dt*sign_control_input*max_rpm_second + rpm
        if abs(rpm)>abs(pid_speed.Integrator_max):
            rpm = np.sign(rpm)*abs(pid_speed.Integrator_max)
    # print(rpm)
    # model
    u, v, r, hdg, delta_x_0, delta_y_0, delta_r_0, u_dot, v_dot, r_dot = ship_model.manoeuvre_model_rpa_3(u, v, r, hdg,
                                                                                                   rpm,
                                                                                                   0,#rudder 
                                                                                                   dt,
                                                                                                   )
    
    u_ref.append(current_speed_setting)
    u_real.append(u)
    rpm_set.append(rpm)
    t = t + dt

u_ref_array = np.asarray(u_ref)
u_real_array = np.asarray(u_real)

u_score = abs(u_ref_array-u_real_array)
u_score = u_score.sum()

print(u_score)


plt.plot(u_ref)
plt.plot(u_real)
plt.plot(rpm_set)


plt.show()









