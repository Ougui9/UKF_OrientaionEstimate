from scipy import io
import numpy as np



# def deg2rad(deg):
#     return deg/180*np.pi
#
# def impData():
#     sensitivity_A = 0.33  # unit:mv/g
#     scale_A = 3.3 / 1023 / sensitivity_A
#     Az_addbias =1/scale_A
#
#     sensitivity_W = 3.33   # unit:mv/deg/s
#     scale_W = 3300 / 1023 / (sensitivity_W*180/np.pi)
#
#
#     data = io.loadmat('./imu/imuRaw1.mat')
#     raw_vals, ts = data['vals'], data['ts']
#     A,W=raw_vals[:3,:],raw_vals[3:,:]
#     A_bias=np.mean(A[:,:100],axis=1)
#     A_bias[-1]=A_bias+Az_addbias
#     A=(A-A_bias)*scale_A
#
#     W_bias = np.mean(W[:, :100], axis=1)
#     W = (W - W_bias) * scale_W
#
#
#
#     return A,W
#
#
# def gtData():
#
#
#     data=io.loadmat('./vicon/viconRot1.mat')
#     rots, ts_gt= data['rots'], data['ts']
#
#
#     return rots,ts_gt

def acc2rp(acc):
    # r=-np.arctan(acc[1]/np.sqrt(acc[0]**2+acc[2]**2))
    r = -np.arctan(acc[1] / acc[2])
    p=np.arctan(acc[0]/np.sqrt(acc[1]**2+acc[2]**2))
    y=np.zeros_like(r)
    return r,p,y

def vec2quat(vec):
    '''
    :param vec: (3, n)
    :return:(4, n)
    '''

    theta =np.linalg.norm(vec,axis=0)
    vec_unit=vec/theta
    q=np.zeros(np.array(list(vec.shape))+[1,0])
    q[0],q[1:]=np.cos(theta/2),vec_unit*np.sin(theta/2)
    q[np.isnan(q)]=0
    q[np.isinf(q)] = 0
    return q



def quatMulti(a,b):
    '''
    :param a: (4, 1)
    :param b: (4, n)
    :return:(4, n)
    '''
    a=a.astype(float)
    a0, a1, a2, a3 = a[0],a[1],a[2],a[3]
    b0, b1, b2, b3 = b[0],b[1],b[2],b[3]
    q=np.zeros([4,b.shape[1]])
    q[0],q[1],q[2],q[3]=-b1*a1 - b2*a2 - b3*a3 + b0*a0,\
                        b1*a0 + b2*a3 - b3*a2 + b0*a1,\
                        -b1*a3 + b2*a0 + b3*a1 + b0*a2,\
                        b1*a2 - b2*a1 + b3*a0 + b0*a3
    return q


def rpy2rot(r,p,y):
    rot=np.zeros([3,3,len(r)])
    a = y
    b = p
    c = r
    rot[0,0]=np.multiply(np.cos(a),np.cos(b))
    rot[0, 1] =np.multiply(np.multiply(np.cos(a),np.sin(b)),np.sin(c))-np.multiply(np.sin(a),np.cos(c))
    rot[0, 2] =np.multiply(np.multiply(np.cos(a),np.sin(b)),np.cos(c))+np.multiply(np.sin(a),np.sin(c))
    rot[1, 0] =np.multiply(np.sin(a),np.cos(b))
    rot[1, 1] =np.multiply(np.multiply(np.sin(a),np.sin(b)),np.sin(c))+np.multiply(np.cos(a),np.cos(c))
    rot[1, 2] =np.multiply(np.multiply(np.sin(a),np.sin(b)),np.cos(c))-np.multiply(np.cos(a),np.sin(c))
    rot[2, 0] =-np.sin(b)
    rot[2, 1] =np.multiply(np.cos(b),np.sin(c))
    rot[2, 2] =np.multiply(np.cos(b),np.cos(c))
    return rot

def vecNormorlize(x):
    '''
    :param x: (4, 1)
    :return: (4, 1)
    '''
    return x/np.linalg.norm(x)

def quat2matrix(q):
    '''

    :param q:(4, n)
    :return:(3, 3, n)
    '''
    q=q.reshape(-1,4)
    rot=np.zeros([3,3,len(q)])
    q=vecNormorlize(q)
    rot[0,0]=1-2*(q[0,2]**2 + q[0,3]**2)
    rot[0, 1] =2*(np.multiply(q[0,1],q[0,2]) + np.multiply(q[0,0],q[0,3]))
    rot[0, 2] =2*(np.multiply(q[0,1],q[0,3]) - np.multiply(q[0,0],q[0,2]))
    rot[1, 0] =2*(np.multiply(q[0,1],q[0,2]) - np.multiply(q[0,0],q[0,3]))
    rot[1, 1] =1-2*(q[0,1]**2 + q[0,3]**2)
    rot[1, 2] =2*(np.multiply(q[0,2],q[0,3]) + np.multiply(q[0,0],q[0,1]))
    rot[2, 0] =2*(np.multiply(q[0,1],q[0,3]) + np.multiply(q[0,0],q[0,2]))
    rot[2, 1] =2*(np.multiply(q[0,2],q[0,3]) - np.multiply(q[0,0],q[0,1]))
    rot[2, 2] =1-2*(q[0,0]**2 + q[0,1]**2)
    return rot