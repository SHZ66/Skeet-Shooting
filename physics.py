from numpy import *

def initSplash(m0, M, v0, v1, n = 8):
# Calculate initial velocities for pieces (of equal mass) in the event of a splash
    # calculate the upperbound for sum(E)
    ub = m0 * n / M * (v0.dot(v0) - v1.dot(v1)) - n * m0 * m0 / (M * M) * (v0 - v1).dot(v0 - v1)
    # initialize w's
    # f: f percent of upperbound goes to E
    f = 0.5
    E = rand_const_sum(n, f * ub)

    v0_len = sqrt(v0.dot(v0))
    E2 = random.rand(n) * 0.3 * v0_len
    W = empty(n)
    W[0] = v0_len - E[-1] + E[0]
    for i in xrange(1, n):
        W[i] = v0_len - E[i - 1] + E[i]
    return W

def rand_const_sum(n, summ = 1.0, err_ub = 0.3):
    l = summ / float(n)
    E = random.rand(n) * err_ub * l
    R = empty(n)
    R[0] = l - E[-1] + E[0]
    for i in xrange(1, n):
        R[i] = l - E[i - 1] + E[i]
    return R

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

X = rand_const_sum(5, 10)
print X
print sum(X)