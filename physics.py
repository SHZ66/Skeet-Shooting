from numpy import *

def initSplash(v0, n = 8):
# Calculate initial velocities for pieces (of equal mass) in the event of a splash
    # initialize w's
    W = zeros(n)
    l = n * sqrt(v0.dot(v0))
    R = random.rand(n - 1)
    for i in xrange(n - 1):
        V2[i] = R[i] * l
        l -= V2[i]
    V2[-1] = l
    return V2

#V2 = initSplash(array([2, 3]))
#print V2
#print sum(V2)