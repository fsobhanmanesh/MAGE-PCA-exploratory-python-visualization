from sklearn.decomposition import SparsePCA

import numpy as np
dot = np.dot

if __name__ == "__main__":
    import sys

    csv = "..\..\IOdata\largearray.csv"
    #csv = "c:/iris44.csv"  # wikipedia Iris_flower_data_set
        # 5.1,3.5,1.4,0.2  # ,Iris-setosa ...
    N = 40
    K = 450000
    
    seed = 1
    exec "\n".join( sys.argv[1:] )  # N= ...
    np.random.seed(seed)
    np.set_printoptions( 1, threshold=100, suppress=True )  # .1f
    try:
        A = np.genfromtxt( csv, delimiter="," )
        N, K = A.shape
    except IOError:
        print('error')
        A = np.random.normal( size=(N, K) )  # gen correlated ?

    print(len(A[1]), N, K)
    
    print "A:", A
    #pca = PCA(n_components=4)
    pca = SparsePCA(n_components=None, alpha=1, ridge_alpha=0.01, max_iter=1000, tol=1e-08, method='lars', n_jobs=1, U_init=None, V_init=None, verbose=False, random_state=None)
    scores=pca.fit_transform(A)
    pca_variance = pca.explained_variance_ratio_
    coeff = pca.components_
    #A1=pca.inverse_transform(coeff)
    print(pca_variance)
    print("coeff",coeff)
    #score = pca.transform(A)
    print("score",scores)
    #print A1
    