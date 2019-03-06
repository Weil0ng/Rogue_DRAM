import math
import functools
import logging

def getSALibDistName(config_name):
    if config_name == 'Normal' or config_name == 'Gaussian' or config_name == 'Binomial':
        return 'norm', (functools.partial(lambda x: float(x)) if config_name == 'Normal' else \
                functools.partial(lambda x: int(round(x))))
    else:
        return None, None

class Config(object):
    def __init__(self, params):
        assert len(params) > 3, 'Incomplete configuration: {}'.format(' '.join(params))
        self.name = params[0]
        self.dist = params[1]
        self.salib_dist, self.salib_dtype_func = getSALibDistName(self.dist)

        self.lb = None
        self.ub = None
        if len(params) > 5:
            try:
                self.lb = float(params[5])
            except:
                assert params[5] == 'None'
        if len(params) > 6:
            try:
                self.ub = float(params[6])
            except:
                assert params[6] == 'None'

        if self.dist == 'Uniform':
            assert self.lb is not None and self.ub is not None
            self.mean = 0.5 * (self.lb + self.ub)
            self.std = 1./ 12 * ((self.ub - self.lb) ** 2)
        else:
            self.mean = float(params[2])
            self.std = float(params[3])
        self.unit = params[4] if len(params) > 4 and params[4] != 'None' else ''
        self.transform = eval(' '.join(params[7:])) if len(params) > 7 else None
    
    def dump(self):
        logging.debug('{}: {}({}, {}){} on ({}, {})'.format(self.name, self.dist, self.mean, self.std, self.unit,
            self.lb, self.ub))

    def get_gpc_spec(self):
        if self.dist == 'Binomial':
            assert self.mean > self.std * self.std, 'Not a valid ({}, {}) for Binomial'.format(self.mean, self.std)
            assert self.lb is None and self.ub is None, 'Not valid bounds ({}, {})'.format(self.lb, self.ub)
            self.n = float(round(self.mean * self.mean / (self.mean - self.std * self.std)))
            self.p = 1 - self.std * self.std * 1. / self.mean
            assert self.n > 0 and self.p > 0, 'N: {}, P: {}'.format(self.n, self.p)
            return (self.n, self.p)
        else:
            if self.lb is not None and self.ub is not None:
                return (self.mean, self.std, self.lb, self.ub)
            elif self.lb is not None and self.ub is None:
                return (self.mean, self.std, self.lb)
            elif self.lb is None and self.ub is not None:
                # TODO: temp hack since no support for one-sided trunc.
                return (self.mean, self.std, -1. * 1e10, self.ub)
            else:
                assert self.lb is None and self.ub is None
                return (self.mean, self.std)
