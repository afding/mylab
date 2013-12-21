from math import *
import random
import matplotlib.pyplot as plt

class robot:
    def __init__(self, length = 20.0):
        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0
        self.length = length
        self.steering_noise = 0.0
        self.distance_noise = 0.0
        self.steering_drift = 0.0

    def set_coordinate(self, x, y, orientation):
        self.x = float(x)
        self.y = float(y)
        self.orientation = float(orientation) % (2.0 * pi)

    def set_noise(self, s_noise, d_noise):
        # this is often useful in particle filters
        self.steering_noise = float(s_noise)
        self.distance_noise = float(d_noise)

    def set_steering_drift(self, drift):
        self.steering_drift = drift

    # move: 
    #    steering = front wheel steering angle, limited by max_steering_angle
    def move(self, steering, distance, 
             tolerance = 1e-3, max_steering_angle = pi / 4.0):
        steering = min(max_steering_angle, steering)
        steering = max(-max_steering_angle, steering)
        distance = max(0,distance)
        # apply noise
        steering2 = random.gauss(steering, self.steering_noise)
        distance2 = random.gauss(distance, self.distance_noise)
        # apply steering drift
        steering2 += self.steering_drift
        # Execute motion
        turn = tan(steering2) * distance2 / self.length
        if abs(turn) < tolerance:
            # approximate by straight line motion
            self.x += distance2 * cos(self.orientation)
            self.y += distance2 * sin(self.orientation)
            self.orientation = (self.orientation + turn) % (2.0 * pi)
        else:
            # approximate bicycle model for motion
            radius = distance2 / turn
            cx = self.x - (sin(self.orientation) * radius)
            cy = self.y + (cos(self.orientation) * radius)
            self.orientation = (self.orientation + turn) % (2.0 * pi)
            self.x = cx + (sin(self.orientation) * radius)
            self.y = cy - (cos(self.orientation) * radius)

    def __repr__(self):
        return '[x=%.5f y=%.5f orient=%.5f]'  % (self.x, self.y, self.orientation)

def run(params, print_flag = False):
    rob = robot()
    rob.set_coordinate(0.0, 1.0, 0.0)
    rob.set_noise(0.1,0.1)
    rob.set_steering_drift(10./180*pi) #10 degree system erro
    speed = 1.0 
    time_interval = 1.0
    N = 100
    err=0.0
    int_err=0.0
    crosstrack_err = rob.y
    data=[]
    for i in range(N*2):
        dif_err = rob.y - crosstrack_err
        crosstrack_err = rob.y
        int_err += crosstrack_err
        steer = -params[0]* crosstrack_err - params[1]* dif_err - params[2]* int_err
        rob.move(steer, speed*time_interval)
        data.append((rob.x, rob.y))
        if i>=N:
            err += crosstrack_err **2
    if print_flag:
        plt.plot(*zip(*data))
        plt.show()
    return err/N 
    
def twiddle(tol=1e-2):
    n_params=3
    params = [0,] * n_params
    dparams = [1.,] * n_params
    print params, dparams
    best_err= run(params)
    n=0
    while sum(dparams)>tol:
        for i in range(n_params):
            params[i]+=dparams[i]
            err=run(params)
            if err<best_err:
                best_err=err
                dparams[i]*=1.1
            else:
                params[i] -=2.0*dparams[i]
                err=run(params)
                if err<best_err:
                    best_err=err
                    dparams[i]*=1.1
                else:
                    params[i]+=dparams[i]
                    dparams[i]*=0.9
        n+=1
        print 'Twiddle #', n, params, ' --> ', best_err
    print ' '
    return params

best=twiddle()
run(best,True)
