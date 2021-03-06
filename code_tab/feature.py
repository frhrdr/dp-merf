"""Module containing classes for extracting/constructing features from data"""

__author__ = 'wittawat'

from abc import ABCMeta, abstractmethod
import numpy as np
import scipy.stats as stats
import util as util


class FeatureMap(object):
    """Abstract class for a feature map function"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def gen_features(self, X):
        """Generate D features for each point in X.
        - X: nxd data matrix
        Return a n x D numpy array.
        """
        pass

    @abstractmethod
    def num_features(self, X=None):
        """
        Return the number of features that this map will generate for X.
        X is optional.
        """
        pass

    def __call__(self, X):
        return self.gen_features(X)


class MarginalCDFMap(FeatureMap):
    """
    A FeatureMap that returns a new set of variates generated by applying
    the empirical CDF of each variate to its corresponding variate.
    Also called, a copula transform or a probability integral transform.
    """
    def gen_features(self, X):
        """
        Cost O(dn*log(n)) where X in n x d.
        """
        n, d = X.shape
        Z = np.zeros((n, d))
        for j in range(d):
            Z[:, j] = stats.rankdata(X[:, j])/float(n)
        return Z

    def num_features(self, X):
        return X.shape[1]


class RFFKGauss(FeatureMap):
    """
    A FeatureMap to construct random Fourier features for a Gaussian kernel.
    """
    def __init__(self, sigma2, n_features, seed=1):
        """
        n_features: number of random Fourier features. The total number of
            dimensions will be n_features. Internally draw n_features/2
            frequency components. n_features has to be even.
        """
        if sigma2 <= 0:
            raise ValueError('sigma2 is not positive. Was {}'.format(sigma2))
        if not (n_features > 0 and n_features%2==0):
            raise ValueError('n_features has to be even positive integer (just for our convenience). Was {}'.format(n_features))
        self.sigma2 = sigma2
        self.n_features = n_features
        self.seed =  seed

    def gen_features(self, X):
        # The following block of code is deterministic given seed.
        # Fourier transform formula from
        # http://mathworld.wolfram.com/FourierTransformGaussian.html
        with util.NumpySeedContext(seed=self.seed):
            n, d = X.shape

            draws = self.n_features//2
            W = np.random.randn(draws, d)/np.sqrt(self.sigma2)
            # n x draws
            XWT = X.dot(W.T)
            Z1 = np.cos(XWT)
            Z2 = np.sin(XWT)
            Z = np.hstack((Z1, Z2))*np.sqrt(2.0/self.n_features)
        return Z

    def num_features(self, X=None):
        return self.n_features


# class RFFKGauss(FeatureMap):
#     """
#     A FeatureMap to construct random Fourier features for a Gaussian kernel.
#     """
#     def __init__(self, sigma2, n_features, W, seed=1):
#         """
#         n_features: number of random Fourier features. The total number of
#             dimensions will be n_features. Internally draw n_features/2
#             frequency components. n_features has to be even.
#         """
#         if sigma2 <= 0:
#             raise ValueError('sigma2 is not positive. Was {}'.format(sigma2))
#         if not (n_features > 0 and n_features%2==0):
#             raise ValueError('n_features has to be even positive integer (just for our convenience). Was {}'.format(n_features))
#         self.sigma2 = sigma2
#         self.n_features = n_features
#         self.seed =  seed
#         self.W = W
#
#     def gen_features(self, X):
#         # The following block of code is deterministic given seed.
#         # Fourier transform formula from
#         # http://mathworld.wolfram.com/FourierTransformGaussian.html
#         with util.NumpySeedContext(seed=self.seed):
#             # n, d = X.shape
#
#             # draws = self.n_features//2
#             # W = np.random.randn(draws, d)/np.sqrt(self.sigma2)
#             W = self.W
#             # n x draws
#             XWT = X.dot(W.T)
#             Z1 = np.cos(XWT)
#             Z2 = np.sin(XWT)
#             Z = np.hstack((Z1, Z2))*np.sqrt(2.0/self.n_features)
#         return Z
#
#     def num_features(self, X=None):
#         return self.n_features