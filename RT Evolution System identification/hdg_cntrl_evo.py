#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 16:32:59 2020

@author: erwinlodder
"""
import numpy as np
import time
from manoeuvre_model_evo import ship_model
from ship_class import ship
from pid_small import PID
import matplotlib.pyplot as plt
ship = ship()
coef_ = np.genfromtxt('foo_evo_general.csv', delimiter=',')


# P_range = np.arange(0,10.2,0.2)
# I_range = np.arange(0,10.2,0.2)
# D_range = np.arange(0,10.2,0.2)

#initialise ship
u, v, r, hdg = 0,0,0,0
ship_model = ship_model(0,0,0, ship, coef_)
max_rpm_second = 1.2
rpm = 0 

class MA_filter:
    def __init__(self, periods):
        self.filter_array = np.zeros(periods)    
    def filter(self, input_):
        self.filter_array = np.roll(self.filter_array, 1)
        self.filter_array[0] = input_
        return np.average(self.filter_array)

# (speed, time)
speed_u = [(0, 0), (3, 20), (6, 140), (5, 250), (1, 450)]
end_input = 0
speed_u_position = 0
current_speed_setting = 0
t = 0
dt = 0.4 #future: add noise
t_end = 600
pid_speed = PID(P=1.6, I=0.0, D=10.653, Ibounds_speed=(0,6.3)) # -0.04646

#
u_ref = []
u_real = []
rpm_set = []
periods = 1

rpm_array = MA_filter(periods)
# rpm_1_set = MA_filter(periods)
# rpm_2_set = MA_filter(periods)

while t<t_end:
    # calculate speed input
    if end_input==0:
        if speed_u[speed_u_position][1] <= t:
            
            current_speed_setting = speed_u[speed_u_position][0]
            pid_speed.setPoint_speed(current_speed_setting)
            speed_u_position += 1
            if speed_u_position==len(speed_u):
                end_input  = 1
        
        
        
    control_input = pid_speed.update(u, dt)
    sign_control_input = np.sign(control_input)
    # calculate speed control iput
    if abs(abs(control_input)-abs(rpm))/dt>max_rpm_second:
        
        rpm = dt*sign_control_input*max_rpm_second + rpm
        if abs(rpm)>abs(pid_speed.Integrator_max):
            rpm = np.sign(rpm)*abs(pid_speed.Integrator_max)
        # elif rpm<
    # print(rpm)
    # model
    rpm_0, rpm_1, rpm_2 = rpm, rpm, rpm#rpm_array.filter(rpm), rpm_array.filter(rpm), rpm_array.filter(rpm)
    rsa_0,rsa_1,rsa_2 = 180,180,180
    if rpm<0.0:
        rpm_0 ,rpm_1, rpm_2 = 1.0,1.0,1.0
        rsa_0,rsa_1,rsa_2 = 0,0,0
        
    
    # if rpm>0.0:
    #     rpm_1, rpm_2, rpm_3 = rpm+8.8, rpm+8.8, rpm+8.8
    # else:
    
    
    u, v, r, hdg, delta_x_0, delta_y_0, delta_r_0, u_dot, v_dot, r_dot = ship_model.manoeuvre_model_rt_evolution(u, v, r, hdg,
                                                                                                   rpm_0, rpm_1, rpm_2,
                                                                                                   rsa_0,rsa_1,rsa_2,#rudder 
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

plt.savefig('tuner_borkum.png')
plt.show()










