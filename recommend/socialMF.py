import random
import numpy as np
from collections import defaultdict
from matplotlib import pyplot as plt


def sigmoid(z):
    return 1.0 / (1 + np.exp(-z))

def dsigmoid(z):
    return np.exp(-z)/(1+np.exp(-z))**2

def average(R):
    res=0.0
    count=0
    for u in R:
        for i in R[u]:
            count+=1
            res+=R[u][i]
    return count>0 and res/count or 0.0

def normalize(T):
    for u in T:
        All = sum(T[u].values())
        if All>0:
            for v in T[u]:
                T[u][v] /= All
    return T 

def socialMF(R,N,M, T, K, lambdaU,lambdaV,lambdaT, 
        steps=10**3, learn_rate=0.1, tol=1e-3):
    def costL(U,V,*args):
        R,T,Rr=args
        cost=0.0
        for u in R:
            for i in R[u]:
                cost += 0.5 * (R[u][i] - sigmoid(U[u].dot(V[i])))**2
        cost += lambdaU/2 * np.linalg.norm(U)+lambdaV/2 * np.linalg.norm(V)
        for u in T:
            e = np.copy(U[u]) #1xK
            for v in T[u]:
                e -= T[u][v]*U[v]
            cost += lambdaT/2 * e.dot(e.T)
        return cost

    def gradient(U,V, *args):
        R,T,Rr=args
        dU = np.zeros(U.shape)
        dV = np.zeros(V.shape)
#        for u in random.shuffle(R.keys()):
        for u in R:
            for i in R[u]:
                tmp = U[u].dot(V[i])
                dU[u] += V[i] * dsigmoid(tmp) * (sigmoid(tmp)-R[u][i]) 
            dU[u] += lambdaU * U[u]
            e = np.copy(U[u]) #1xK
            for v in T[u]:
                e -= T[u][v] * U[v]
            dU[u] += lambdaT * e
            e2 = np.zeros_like(U[u])
            for v in T[u]:
                if v in T and u in T[v]:
                    e = np.copy(U[v])
                    for w in T[v]:
                        e-= T[v][w] * U[w]
                    e2 += T[v][u] * e 
            dU[u] -= lambdaT * e2

        for i in Rr:
            for u in Rr[i]:
                tmp = U[u].dot(V[i])
                dV[i] += U[u] * dsigmoid(tmp) * (sigmoid(tmp)-Rr[i][u])
            dV[i] += lambdaV * V[i]
        return dU,dV

    def GD(x0):
        U,V=x0
        args=R,T,Rr
        res=[]
        old_e = 1e5
        t0=10
        for step in xrange(steps):
            dU,dV = gradient(U,V,*args)
            rate=learn_rate/(t0+step)
            U -= rate * dU
            V -= rate * dV
            e = costL(U,V,*args)
            print step, e
            res.append(e)
#            old_e = e
            if e < tol:
                break
        plt.plot(res)
        plt.show()
        print 'step:%d, e: %f' %(step, e)
        return U, V

    def f(x, *args):
        x=x.reshape(N+M,K)
        u, v = x[:N,], x[N:,]
        return costL(u, v, *args)

    def gradf(x, *args):
        x=x.reshape(N+M,K)
        u, v = x[:N,], x[N:,]
        gu,gv=gradient(u,v,*args)
        x_ = np.vstack((gu,gv)).ravel()
        return x_

    def optim(x0):
        from scipy import optimize
        x0=np.vstack(x0).ravel()
        args=R,T,Rr
        x = optimize.fmin_cg(f, x0, fprime=gradf, args=args)
        x=x.reshape(N+M,K)
        u, v = x[:N,], x[N:,]
        return  u,v

    U = np.random.normal(size=(N,K))
    V = np.random.normal(size=(M,K))
    Rr = reverseR(R)
    T=normalize(T)
    x0=U,V
    return GD(x0) 
#    return optim(x0)

def gen_data(fname):
    for line in open(fname):
        try:
            yield [int(i)-1 for i in line.split()] #index start from 1
        except:
            print line

def reverseR(R):
    Rr=defaultdict(dict)
    for u in R:
        for i in R[u]:
            Rr[i][u] = R[u][i]
    return Rr


def test(R,N,M,T,K,max_r,lambdaU,lambdaV,lambdaT):
    print 'N:%d, M:%d, K:%d,lambdaU:%s, lambdaV:%s,lambdaT:%s' \
            %(N,M,K,lambdaU,lambdaV,lambdaT)
    #raw_input('Press any key to start...')
    U,V = socialMF(R,N,M,T,K,lambdaU,lambdaV,lambdaT)  
    vfn = np.vectorize(sigmoid)
    print R 
    print 'R_hat:\n', vfn(U.dot(V.T)) *max_r


def t_toy():
    R0 = [
         [5,3,0,1],
         [4,0,0,1],
         [1,1,0,5],
         [1,0,0,4],
         [0,1,5,4],
        ]
    max_r = 5.0
    T0 = [[3,5],[1,3,4],[2],[1,5],[3]]
    N,M,K=5,4,2
    lambdaU,lambdaV,lambdaT=0.02, 0.02, 0.0

    R=defaultdict(dict)
    T=defaultdict(dict)
    for i in xrange(len(R0)):
        for j in xrange(len(R0[0])):
            if R0[i][j]>0:
                R[i][j]=1.0 * R0[i][j] / max_r
    for i in xrange(len(T0)):
        for j in T0[i]:
            T[i][j-1]=1.0
    test(R,N,M,T,K,max_r,lambdaU,lambdaV,lambdaT)

def t_epinion():
    #data from: http://www.trustlet.org/wiki/Epinions_datasets
    N,M = 0,0
    max_r = 5.0
    R=defaultdict(dict)
    T=defaultdict(dict)
    print 'get T'
    limit = 10**2
    for u,v,_ in gen_data('./epinions/trust_data.txt'):
        if u>=limit or v>=limit:
            continue
        T[u][v]=1.0
        N=max(N,u,v)
    print 'get R'
    for u,i,r in gen_data('./epinions/ratings_data.txt'):
        if u>=limit or i>=limit:
            continue
        R[u][i] = r/max_r
        N=max(N,u)
        M=max(M,i)
    N+=1
    M+=1
    K=5
    lambdaU,lambdaV,lambdaT=0.1, 0.1, 1.0
    test(R,N,M,T,K,max_r,lambdaU,lambdaV,lambdaT)

def RMSE():
    pass

if __name__ == "__main__":
#   t_epinion()
   t_toy()

