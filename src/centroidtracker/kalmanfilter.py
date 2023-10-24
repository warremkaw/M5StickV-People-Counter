import ulab as ul

# See https://machinelearningspace.com/2d-object-tracking-using-kalman-filter/
# for explanation on formulas
class KalmanFilter(object):
    def __init__(self, dt, u_x,u_y, std_acc, x_std_meas, y_std_meas):
        """
        :param dt: sampling time (time for 1 cycle)
        :param u_x: acceleration in x-direction
        :param u_y: acceleration in y-direction
        :param std_acc: process noise magnitude
        :param x_std_meas: standard deviation of the measurement in x-direction
        :param y_std_meas: standard deviation of the measurement in y-direction
        """

        # Define sampling time
        self.dt = dt

        # control input variables
        self.u = ul.array([[u_x],
                           [u_y]])

        # state matrix
        self.x = ul.array([[0],
                           [0],
                           [0],
                           [0]])

        # state transition matrix
        self.A = ul.array([[1, 0, self.dt, 0      ],
                           [0, 1, 0,       self.dt],
                           [0, 0, 1,       0      ],
                           [0, 0, 0,       1      ]])

        # control matrix
        self.B = ul.array([[(self.dt**2)/2, 0             ],
                           [0,              (self.dt**2)/2],
                           [self.dt,        0             ],
                           [0,              self.dt       ]])

        # transformation matrix
        self.H = ul.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])

        # process noise covariance matrix
        self.Q = ul.array([[(self.dt**4)/4, 0,              (self.dt**3)/2, 0             ],
                           [0,              (self.dt**4)/4, 0,              (self.dt**3)/2],
                           [(self.dt**3)/2, 0,              self.dt**2,     0             ],
                           [0,              (self.dt**3)/2, 0,              self.dt**2    ]])
        self.Q = self.Q * std_acc**2

        # measurement noice covaraince matrix
        self.R = ul.array([[x_std_meas**2, 0            ],
                           [0,             y_std_meas**2]])

        # error covariance matrix
        self.P = ul.eye(self.A.shape()[1])

    def predict(self):
        # Update time state
        self.x = ul.dot(self.A, self.x) + ul.dot(self.B, self.u)

        # Calculate error covariance
        AT = ul.array(self.A)
        AT.transpose()
        self.P = ul.dot(ul.dot(self.A, self.P), AT)+ self.Q

        # ul has round function for matrices/array like numpy does
        return ul.array([[round(x)] for x in self.x.flatten()[0:2]], dtype=ul.int16)

    def update(self, z):
        if z.shape() == (1,2):
            z.transpose()

        # Calculate the Kalman Gain
        HT = ul.array(self.H)
        HT.transpose()
        S = ul.dot(self.H, ul.dot(self.P, HT)) + self.R
        K = ul.dot(ul.dot(self.P, HT), ul.inv(S))

        # Update state
        self.x = self.x + ul.dot(K, (z - ul.dot(self.H, self.x)))

        # Update error covariance
        I = ul.eye(self.H.shape()[1])
        self.P = ul.dot(I - ul.dot(K, self.H), self.P)

        return ul.array([[round(x)] for x in self.x.flatten()[0:2]], dtype=ul.int16)
