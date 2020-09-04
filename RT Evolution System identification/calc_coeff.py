import numpy as np
import pandas as pd
from numpy import newaxis
from sklearn.linear_model import Lasso
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import LassoCV
import matplotlib.pyplot as plt
import math

from sklearn.model_selection import GridSearchCV
##
from ship_class import ship
ship = ship()
df_main = pd.read_csv('test_1.csv', sep=',')
# df_main = df_main[30400:31600].reset_index(inplace=False)
df_main.timestamp = pd.to_datetime(df_main.timestamp, format='%Y-%m-%d %H:%M:%S.%f')
df_main = df_main.dropna()
# df_main.rsa_0 = df_main.rsa_0+10.0
def thrust_cone(x_eng, y_eng, az_eng, cone_deg, flow_distance, x_down, y_down):
    #check axis!!!!!!! coherent to choosen axis system
    top_corner = [y_eng, x_eng]
    right_corner = [y_eng + np.sin(np.deg2rad(az_eng - cone_deg/2.))*flow_distance, x_eng + np.cos(np.deg2rad(az_eng - cone_deg/2.))*flow_distance]
    left_corner = [y_eng + np.sin(np.deg2rad(az_eng + cone_deg/2.))*flow_distance, x_eng + np.cos(np.deg2rad(az_eng + cone_deg/2.))*flow_distance]
    triangle_list = [top_corner, right_corner, left_corner]
    x1, y1, x2, y2, x3, y3, xp, yp = top_corner[0], top_corner[1], right_corner[0], right_corner[1], left_corner[0], left_corner[1], y_down, x_down
    c1 = (x2 - x1) * (yp - y1) - (y2 - y1) * (xp - x1)
    c2 = (x3 - x2) * (yp - y2) - (y3 - y2) * (xp - x2)
    c3 = (x1 - x3) * (yp - y3) - (y1 - y3) * (xp - x3)
    if (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0):
    # if max([pos[0] for pos in triangle_list])>=y_down>=min([pos[0] for pos in triangle_list]) and max([pos[1] for pos in triangle_list])>=x_down>=min([pos[1] for pos in triangle_list]):
        return (1 - np.deg2rad(abs((azimuth([y_eng, x_eng],[y_down,x_down])-az_eng))))
    else:
        return 0

def azimuth(point1, point2):
    angle = np.arctan2(point2[0] - point1[0], point2[1] - point1[1])
    return np.degrees(angle) if angle >= 0 else np.degrees(angle) + 360
    #add thrust fraction here

def thruster_interaction_coefficient(x_eng, y_eng, az_eng, cone_deg, flow_distance, x_down, y_down, az_down):  # give engine number: shipclass engine number
    thrust_cone_boolean = thrust_cone(x_eng, y_eng, az_eng, cone_deg, flow_distance, x_down, y_down)
    x_d_ratio = np.sqrt((x_down-x_eng)**2+abs(y_down-y_eng)) / ship.D_p
    t_engine = (1 - 0.75**(x_d_ratio**(2/3)))/(thrust_cone_boolean)
    # print(abs(az_eng-az_down), 1)
    t = t_engine+(1-t_engine)*(((abs(az_eng-az_down))**3)/(((130.)/(t_engine**3)) + ((abs(az_eng-az_down))**3)))
    if math.isnan(t):
        return 0
    else:
        return 1-t

#azimuth 2 port side
df_main['u_a_2'] = ((df_main.u+df_main.r*abs(ship.y_2))*np.cos(np.deg2rad(df_main.delta_psi)) + (df_main.v+df_main.r*abs(ship.x_2))*np.sin(np.deg2rad(df_main.delta_psi))) #(1-ship.w)*
df_main['u_a_1'] = ((df_main.u-df_main.r*abs(ship.y_1))*np.cos(np.deg2rad(df_main.delta_psi)) + (df_main.v-df_main.r*abs(ship.x_1))*np.sin(np.deg2rad(df_main.delta_psi))) #(1-ship.w)*
df_main['u_a_0'] = ((df_main.u)*np.cos(np.deg2rad(df_main.delta_psi)) + ((df_main.r*abs(ship.x_0))*np.sin(np.deg2rad(df_main.delta_psi))) ) #(1-ship.w)*

df_main['beta_2'] = np.rad2deg(np.arctan2(df_main.u_a_2, (0.7*np.pi*df_main.rpm_2*ship.D_p)))
df_main['beta_2'] = df_main.beta_2.apply(lambda x: x-360 if x>360 else x)

df_main['beta_1'] = np.rad2deg(np.arctan2(df_main.u_a_1, (0.7*np.pi*df_main.rpm_1*ship.D_p)))
df_main['beta_1'] = df_main.beta_1.apply(lambda x: x-360 if x>360 else x)

df_main['beta_0'] = np.rad2deg(np.arctan2(df_main.u_a_0, (0.7*np.pi*df_main.rpm_0*ship.D_p)))
df_main['beta_0'] = df_main.beta_0.apply(lambda x: x-360 if x>360 else x)

# first engine listed experiences thrust decrease, t_21 means thrust reduction ratio due to downstream flow caused by engine 1
df_main['t_21_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_1, ship.y_1, row['rsa_1'], 25.0, 100.0, ship.x_2, ship.y_2, row['rsa_2']), axis=1)
df_main['t_20_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_0, ship.y_0, row['rsa_0'], 25.0, 100.0, ship.x_2, ship.y_2, row['rsa_2']), axis=1)
df_main['f_p_40_2'] = (1-df_main['t_21_phi'])*(1-df_main['t_20_phi'])*(1-ship.t)*ship.beta_coef(df_main.beta_2)*0.5*ship.rho*(((((1-ship.w)*df_main.u)**2)+ (0.7*np.pi*df_main.rpm_2*ship.D_p)**2))*np.pi/4*ship.D_p**3
##
df_main['t_12_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_2, ship.y_2, row['rsa_2'], 25.0, 100.0, ship.x_1, ship.y_1, row['rsa_1']), axis=1)
df_main['t_10_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_0, ship.y_0, row['rsa_0'], 25.0, 100.0, ship.x_1, ship.y_1, row['rsa_1']), axis=1)
df_main['f_p_40_1'] = (1-df_main['t_12_phi'])*(1-df_main['t_10_phi'])*(1-ship.t)*ship.beta_coef(df_main.beta_1)*0.5*ship.rho*(((((1-ship.w)*df_main.u)**2)+ (0.7*np.pi*df_main.rpm_1*ship.D_p)**2))*np.pi/4*ship.D_p**3

df_main['t_02_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_2, ship.y_2, row['rsa_2'], 25.0, 100.0, ship.x_0, ship.y_0, row['rsa_0']), axis=1)
df_main['t_01_phi'] = df_main.apply(lambda row: thruster_interaction_coefficient(ship.x_1, ship.y_1, row['rsa_1'], 25.0, 100.0, ship.x_0, ship.y_0, row['rsa_0']), axis=1)
df_main['f_p_40_0'] = (1-df_main['t_02_phi'])*(1-df_main['t_01_phi'])*(1-ship.t)*ship.beta_coef(df_main.beta_0)*0.5*ship.rho*(((((1-ship.w)*df_main.u)**2)+ (0.7*np.pi*df_main.rpm_0*ship.D_p)**2))*np.pi/4*ship.D_p**3


# plt.plot(df_main.index.tolist()[:],df_main.u_a_1.tolist()[:])
plt.plot(df_main.index.tolist()[:],df_main.t_02_phi.tolist()[:])
# plt.plot(df_main.x_real.tolist()[:],df_main.y_real.tolist()[:])
# plt.plot(df_main.index.tolist()[:],df_main.u)

plt.show()



u = df_main.u.to_numpy()[:,newaxis]
v = df_main.v.to_numpy()[:,newaxis]
r = df_main.r.to_numpy()[:,newaxis]

u_dot = df_main.u_dot.to_numpy()[:,newaxis]
v_dot = df_main.v_dot.to_numpy()[:,newaxis]
r_dot = df_main.r_dot.to_numpy()[:,newaxis]

rsa = df_main.rsa.to_numpy()[:, newaxis]
f_p_40 = df_main.f_p_40.to_numpy()[:,newaxis]

# X = u uu uuu vv rr vr uvv rvu urr
# Y = v uv ur uur uuv vvv rrr rrv vvr abs(v)v abs(r)v rabs(v) abs(r)r
# N = r uv ur uur uuv vvv rrr rrv vvr abs(v)v abs(r)v rabs(v) abs(r)r
# X = np.concatenate([u_dot, u, u*u, u*v, u*r, u*np.radians(rsa),r*u, np.radians(rsa)*u, v*u, u*u*u, v*v, r*r, v*r, u*v*v, r*v*u, u*r*r], axis=1)
X = np.concatenate([u_dot, u*u], axis=1)
Y = np.concatenate([v_dot, u*v, u*r, u*u*r, u*u*v, v*v*v, r*r*r, r*r*v, v*v*r, abs(v)*v, abs(r)*v, r*abs(v), abs(r)*r], axis=1)
N = np.concatenate([r_dot, u*v, u*r, u*u*r, u*u*v, v*v*v, r*r*r, r*r*v, v*v*r, abs(v)*v, abs(r)*v, r*abs(v), abs(r)*r], axis=1)

y_x = ship.Mass*(u_dot-r*v)-2*f_p_40 #- F_r*np.sin(np.radians(rsa))
y_y = ship.Mass*(v_dot+r*u)-F_r*np.cos(np.radians(rsa))
y_r = ship.I_e*r_dot + F_r*ship.x_r*np.cos(np.radians(rsa))
pair = (X,y_x)
# for i in np.linspace(0.001, 1.0, num=100, endpoint=False):
# lasso = Lasso()
# parameters = {'alpha' : [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10, 20]}
# lasso_regressor = GridSearchCV(lasso, parameters, cv=1000) #, scoring='neg_mean_squared_error'
# lasso_regressor.fit(pair[0], pair[1])
# print(lasso_regressor.best_params_)
# print(lasso_regressor.best_score_)



lasso = RidgeCV()
lasso.fit(pair[0], pair[1] )
train_score=lasso.score(pair[0], pair[1])
print(train_score)



x = np.linspace(0, 1, len(y_x) + 1)[0:-1]

import numpy as np
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(df_main.lon, df_main.lat, 'g-')
ax2.plot(df, u_dot, 'b-')
ax1.set_xlabel('X data')
ax1.set_ylabel('Y1 data', color='g')
ax2.set_ylabel('Y2 data', color='b')

plt.show()



