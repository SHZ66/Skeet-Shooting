from numpy import *

def initSplash(m0, M, v0, v1, n = 8, f = .5):
# initSplash: Calculate initial velocities for pieces (of equal mass) in the event of a splash
#             * constant momentum, constant kinetic energy
# INPUT - m0: bullet mass (float), M: target total mass (float), n: number of pieces the target breaks into (int),
#       - v0: bullet initial velocity (float vector), v1: bullet velocity after collision (float vector),
#       - f: fraction of kinetic energy assigned to randomize w's (0 < f < 1)
#       * (1 - f): fraction of kinetic energy assigned to randomize u's
# OUTPUT - V: velocities of pieces (n by 2 matrix)

    # calculate the upperbound for sum(Err^2)
    p0 = m0 * (v0 - v1)
    p0_2 = p0.dot(p0)
    p0_len = sqrt(p0_2)
    E0 = .5 * m0 * (v0.dot(v0) - v1.dot(v1))
    #ub = m0 * n / M * (v0.dot(v0) - v1.dot(v1)) - n * p0_2 / (M * M)
    ub = 2 * E0 * n / M - n * p0_2 / (M * M)
    # initialize w's
    # f: f percent of upperbound goes to Err (Err = f * ub)
    W = p0_len / M + rand_fixed_ss(n, f * ub)   # W = |p0| + Err
    # initialize u's
    # the sum of squares of u's is (1-f)*ub
    U = rand_fixed_ss(n, (1-f) * ub)
    # take the directions into account...
    e0 = p0 / p0_len
    e1 = array([-e0[1], e0[0]])
    W = W.reshape(n, 1).dot(e0.reshape(1, 2))
    U = U.reshape(n, 1).dot(e1.reshape(1, 2))
    return W + U

def rand_fixed_sum(n, summ = 1.0, err_ub = 0.3):
    l = summ / float(n)
    E = random.rand(n) * err_ub * l
    R = empty(n)
    R[0] = l - E[-1] + E[0]
    for i in xrange(1, n):
        R[i] = l - E[i - 1] + E[i]
    return R

def rand_fixed_ss(N, ss):
    X = random.rand(N)
    mu1 = mean(X)
    X -= mu1
    f = sqrt(ss/X.dot(X))
    return f * X

def randn_fixed_ss(N, ss):
    X = random.randn(N)
    mu1 = mean(X)
    X -= mu1
    f = sqrt(ss/X.dot(X))
    return f * X

if __name__ == '__main__':    
    #W = initSplash(array([2, 3]))
    #print W
    #print mean(W)

    #m0 = 1.0
    #M = 1.0
    #v0 = array([5.0, 0])
    #print (m0/M - 1)/(1+m0/M)
    #v1 = array([0.9 * 5, 0])
    #E0 = .5 * m0 * (v0.dot(v0) - v1.dot(v1))
    #p0 = m0 * (v0 - v1)
    #print E0
    #print p0.dot(p0) / 2 / M

    #X = rand_fixed_ss(10, 4)
    #print X
    #print mean(X)
    #print X.dot(X)

    m0 = 1.0
    M = 15.0
    v0 = array([2, 1])
    v1 = array([1, .5])
    n = 5
    V = initSplash(m0, M, v0, v1, n)
    print V
    print 'Initial momentum = ' + str(m0 * (v0 - v1))
    print 'Splash momentum = ' + str(M/n * sum(V, 0))
    print 'Initial kinetic energy = ' + str(.5 * m0 * ((v0).dot(v0) - v1.dot(v1)))
    print 'Splash kinetic energy = ' + str(.5 * M/n * trace(V.dot(V.transpose())))
