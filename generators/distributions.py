import copy
import logging
import mcerp3
import numpy as np
import scipy.stats as ss
from timeit import default_timer as timer

class Distribution(object):
    def create(self):
        assert self.mean is not None
        assert self.std is not None
        assert self.name
        logging.debug('Generating {} distribution, mean = {}, std = {}, enforced_bounds={}'.format(
            self.name, self.mean, self.std, 'None' if self.lower is None and self.upper is None else '({}, {})'.format(
                '-oo' if self.lower is None else self.lower,
                'oo' if self.upper is None else self.upper)))
        start = timer()
        self.build()
        end = timer()
        logging.debug('{} samples taken in {}s'.format(mcerp3.npts, end - start))
        return end - start
 
    def sample(self, mean, std, lower = None, upper = None, N = 10):
        assert N >= 1
        mcerp3.npts = N
        self.mean = mean
        self.std = std
        self.lower = lower
        self.upper = upper
        time = self.create()
        assert len(self.dist._mcpts) == N + 1
        return self.dist._mcpts

    def dump(self, unit='', path=None):
        if self.dist:
            logging.debug('Dump {} samples of {} distibution, mean = {}, std = {}'.format(
                len(self.dist._mcpts), self.name, self.dist.mean, self.dist.std))
            logging.debug(' '.join(['%.2f' % v + unit for v in self.dist._mcpts]))
        else:
            logging.debug('{} is empty, try sample from it first.'.format(self.name))

class NormalDistribution(Distribution):
    def __init__(self):
        self.name = 'Normal'
        self.mean = None
        self.std = None
        self.lower = None
        self.upper = None

    def build(self):
        logging.debug('Resample')
        assert self.std > 0
        if self.upper is not None and self.lower is not None:
            assert self.upper >= self.lower
        if self.lower is None and self.upper is None:
            self.dist = mcerp3.N(self.mean, self.std)
        else:
            self.dist = mcerp3.UncertainVariable(ss.truncnorm(
                a = -np.inf if self.lower is None else (self.lower - self.mean) / self.std,
                b = np.inf if self.upper is None else (self.upper - self.mean) / self.std,
                loc = self.mean, scale = self.std))
        self.dist._mcpts = np.asarray([self.mean] + [p for p in self.dist._mcpts])

class BinomialDistribution(Distribution):
    def __init__(self):
        self.name = 'Binomial'
        self.mean = None
        self.std = None
        self.p = None
        self.n = None

    def build(self):
        logging.debug('Resample')
        assert self.mean > 0
        assert self.std > 0
        assert self.mean > self.std * self.std, 'Not a valid ({}, {}) for Binomial'.format(self.mean, self.std)
        assert self.lower is None and self.upper is None, 'Not valid bounds ({}, {})'.format(self.lower, self.upper)
        self.n = int(round(self.mean * self.mean / (self.mean - self.std * self.std)))
        self.p = 1 - self.std * self.std * 1. / self.mean
        assert self.n > 0 and self.p > 0, 'N: {}, P: {}'.format(self.n, self.p)
        self.dist = mcerp3.Binomial(self.n, self.p)
        self.dist._mcpts = np.asarray([int(self.mean)] + [int(p) for p in self.dist._mcpts])

class Constant(Distribution):
    def __init__(self):
        self.name = 'Constant'
        self.mean = None
        self.std = None

    def build(self):
        logging.debug('Resample')
        assert self.std == 0
        self.dist = mcerp3.N(0, 1)
        self.dist._mcpts = np.asarray([int(self.mean)] * (1 + len(self.dist._mcpts)))

class Uniform(Distribution):
    def __init__(self):
        self.name = 'Uniform'
        self.mean = None
        self.std = None
        self.lower = None
        self.upper = None
    
    def build(self):
        logging.debug('Resample')
        assert self.std > 0
        self.dist = mcerp3.U(self.lower, self.upper)
        self.dist._mcpts = np.asarray([self.mean] + [p for p in self.dist._mcpts])

class SupportedDistributions(object):
    dists = {'Gaussian': NormalDistribution(),
            'Normal': NormalDistribution(),
            'Truncated_gaussian': NormalDistribution(),
            'Binomial': BinomialDistribution(),
            'Constant': Constant(),
            'Uniform': Uniform()
            }
