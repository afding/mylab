#!/usr/bin/env python


#ref: https://bitbucket.org/tebeka/ml-class/src/a03c2ba7f4d6?at=default

from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
import en_vec
from util import *


def plot(X, y, clf, title=''):
    data = np.append(X, y, 1)
    pos = data[data[:,-1]==1]
    neg = data[data[:,-1]==0]
    plt.scatter(pos[:,0], pos[:,1], marker='+', color='black')
    plt.scatter(neg[:,0], neg[:,1], marker='o', facecolor='yellow')
    
    plt.contour(*calc_contour(data, clf.predict))
    plt.title(title)
    plt.show()    
    
def info(score, C, gamma):
    return 'score=%s C=%s gamma=%s' %(score, C, gamma)
        
def svm_best(X,y,Xtest,ytest, params=None, **kw):
    """
    return best params of svm:  score, C, gamma
    """
    params = params or (0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30)
    results=[]
    for C in params:
        for gamma in params:  # gamma= 1 / sigma
            clf=svm.SVC(C=C,gamma=gamma, **kw)
            clf.fit(X,y.ravel()>0)  #y to vector
            res = clf.score(Xtest,ytest.ravel()>0), C, gamma
            print info(*res)
            results.append(res)  
    return max(results)
    
    
def solve(fdata, ftest=None, kernel='rbf'):
    """
    kernels: 'rbf', 'linear', 'poly', ... doc in svm.SVC 
    """
    raw = loadmat(fdata)
    X,y = raw['X'], raw['y']
    if ftest:
        raw = loadmat(ftest)
        Xtest,ytest = raw['Xtest'], raw['ytest']
    else:
        X,y,Xtest,ytest = self_test(X,y)
    best, C, gamma = svm_best(X,y,Xtest,ytest, kernel=kernel)   
    clf=svm.SVC(C=C,gamma=gamma,kernel=kernel)
    clf.fit(X,y.ravel()>0)
    print clf
    plot(X,y,clf, title=info(best, C, gamma))
    return clf
    

def spam_train():
    return solve('ex6/spamTrain.mat',ftest= 'ex6/spamTest.mat')
    
    
def test_email(C=1, gamma=0.01):
    raw = loadmat('ex6/spamTrain.mat')
    X,y = raw['X'], raw['y']
    clf=svm.SVC(C=C,gamma=gamma)
    clf.fit(X,y.ravel()>0)
    score=clf.score(X,y.ravel()>0)
    print score
    voc = en_vec.load_voc('ex6/vocab.txt')
    for ftest in ('emailSample1.txt', 'emailSample2.txt', 'spamSample1.txt','spamSample2.txt'):
        with open('ex6/'+ ftest) as f:
            text = f.read()
            x = en_vec.vectorize(voc, text)  
            print ftest, clf.predict(x)
        
if __name__ == '__main__':
    solve('ex6/ex6data2.mat')
#    solve('ex6/ex6data3.mat', 'poly')
#    spam_train()
#    test_email()

