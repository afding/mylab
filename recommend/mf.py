#!/usr/bin/python
#
# Created by Albert Au Yeung (2010)
#
# An implementation of matrix factorization
#
import numpy as np

###############################################################################

"""
@INPUT:
    R     : a matrix to be factorized, dimension N x M
    P     : an initial matrix of dimension N x K
    Q     : an initial matrix of dimension M x K
    K     : the number of latent features
    steps : the maximum number of steps to perform the optimisation
    alpha : the learning rate
    beta  : the regularization parameter
@OUTPUT:
    the final matrices P and Q
"""
def matrix_factorization(R, K, steps=5000, alpha=0.2, beta=0.02, tol=1e-3):
    N,M=R.shape
    P = np.random.rand(N,K)
    Q = np.random.rand(M,K)
    Q = Q.T
    alpha /=(N*M)
    for step in xrange(steps):
        for i in xrange(N):
            for j in xrange(M):
                if R[i][j] > 0:
                    eij = R[i][j] - P[i,:].dot(Q[:,j])
                    for k in xrange(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        #R_hat = P.dot(Q)
        #error with regularization
        e = 0
        for i in xrange(N):
            for j in xrange(M):
                if R[i][j] > 0:
                    e += (R[i][j] - P[i,:].dot(Q[:,j]))**2
        e += beta/2*(np.linalg.norm(P)+np.linalg.norm(Q))
        #print e
        if e < tol:
            break
    print step,e
    return P, Q.T


if __name__ == "__main__":
    R = [
         [5,3,0,1],
         [4,0,0,1],
         [1,1,0,5],
         [1,0,0,4],
         [0,1,5,4],
        ]
    R = np.array(R)
    K = 2
    P, Q = matrix_factorization(R, K)
    print P.dot(Q.T)
