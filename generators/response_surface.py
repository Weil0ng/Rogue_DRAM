import logging
import os
import matlab.engine
import pickle
import re
from Config import Config

matlab_code_home = r'/Users/weil0ng/Stochastic-Testing-model'

class ResponseSurface(object):
    """ Response surface built from samples.
    """

    def __init__(self, name):
        self.name = name
        self.type = None
        self.train_x = []
        self.train_y = {}
        self.eval_func = None

    def is_number(self, n):
        try:
            float(n)
            return True
        except:
            return False

    def assert_same_vec(self, x, y):
        assert len(x) == len(y)
        for a, b in zip(x, y):
            assert a == b, 'Non-matching inputs:\n{}\n{}'.format(x, y)

    def add_train_x(self, x):
        assert x
        self.train_x = x

    def add_train_y(self, col, y):
        assert y
        self.train_y[col] = y

    def train(self):
        raise NotImplementedError

    def eval(self, x):
        assert self.eval_func, 'Model {} has not been trained yet!'.format(self.name)
        return self.eval_func(x)

class GPCRS(ResponseSurface):
    """ GPC models are built in two seperate processes:
        1. Create gpc model and get samples from matlab lib.
        2. Train gpc model (same model from 1) with response values from file.

        This is the training part. Use gen_samples --gpc order to perform step 1.
    """

    def __init__(self, name, config_path):
        """ We need to load the model from the sampling process (should already be persisted from the sample process.)
        """

        super(GPCRS, self).__init__(name)
        self.type = 'GPC'
        self.model = None
        self.stats = None
        assert config_path

        with open(config_path, 'r') as f:
            config_strs = [s.strip('\n') for s in f.readlines() if not s.startswith('#')]
            configs = [Config(config_str.split()) for config_str in config_strs]
            self.xnames = [c.name for c in configs]
            self.name2config = dict([(c.name, c) for c in configs])

        try:
            self.engine = matlab.engine.connect_matlab()
        except:
            logging.debug('Starting Matlab engine...')
            self.engine = matlab.engine.start_matlab()
        self.engine.addpath(r'../gpc_interface/')
        for root, subdirs, files in os.walk(matlab_code_home):
            if not '.git' in root:
                self.engine.addpath(root)

    def load_model(self, model_path):
        """ We need to load the model from the sampling process (should already be persisted from the sample process.)
        """
        
        assert self.engine
        self.type = 'GPC'
        self.model = None
        self.stats = None
        assert model_path

        self.model_path = model_path
        with open(model_path, 'r') as f:
            logging.debug('loading model from: {}'.format(model_path))
            self.model = pickle.load(f)
            logging.debug('model loaded')

    def get_moments(self):
        assert self.model
        return self.model['meanVal'], self.model['stdVal']

    def add_train_x(self, sample_path):
        """ Make sure samples are in the right order.
        """
        assert sample_path
        with open(sample_path, 'r') as f:
            logging.debug('loading x values from: {}'.format(sample_path))
            lines = [l.strip('\n') for l in f.readlines()]
            logging.debug('x values loaded')
        assert lines, 'ERROR: empty samples in {}'.format(sample_path)
        # Keep record of input vector, i.e., [param_name].
        self.input_dimensions = lines[0].split()[::2]
        Xs = [[float(re.sub(r'[^0-9\.]', '', w)) for w in l.split()[1::2]] for l in lines]
        model_Xs = [map(self.name2config[n].transform, x) for n, x in zip(self.xnames, self.model['Scaled_SamplePoints'])]
        ref_Xs = zip(*model_Xs)
        assert len(Xs) == len(ref_Xs)
        for i in range(len(Xs)):
            self.assert_same_vec(Xs[i], ref_Xs[i])
        logging.debug('x-value check pass (sample_file vs. model_file)')
        super(GPCRS, self).add_train_x(Xs)

    def add_train_y(self, path):
        """ Add Ys for training.

        Extract datapoints for key from stats_path.
        """

        # Use cached stats if possible.
        if not self.stats:
            assert path
            with open(path, 'r') as f:
                # id val1 val2 ...
                logging.debug('loading y values from: {}'.format(path))
                self.stats = [l.split()[1:] for l in f.readlines()]
                logging.debug('y values loaded')
                assert self.stats, 'empty file: {}'.format(path)

        # Now we are assued that the Y values are of the right number/in the right order.
        assert len(self.stats) == len(self.train_x)
        
        for col in range(len(self.stats[0])):
            Ys = [float(y[col]) for y in self.stats]
            super(GPCRS, self).add_train_y(col, Ys)

    def train(self):
        logging.debug('training with {} samples'.format(len(self.train_y.values()[0])))
        assert self.model
        for col in self.train_y:
            y = self.train_y[col]
            logging.debug('training for col {}, lebels: {}'.format(col, y))
            self.model = self.engine.gpc_model(self.model, y)
            save_model_path = self.model_path[:self.model_path.rfind(r'.mod')] + '_' + str(col) + '.tmod'
            with open(save_model_path, 'w') as f:
                pickle.dump(self.model, f)
                print 'COL {}: trained model pickled to {}'.format(col, save_model_path)

    def eval(self, inputs):
        # Make sure inputs are of the same dimension as the training input.
        assert inputs
        assert len(inputs[0]) == len(self.xnames)
        y = [self.engine.eval_STmodel(self.model, x) for x in inputs]
        return y

    def SA(self):
        assert self.model
        dim = len(self.xnames)
        if dim > 1:
            Si, Si2, Ti = self.engine.sensitivity_fun(self.model, dim, nargout=3)
            name2si = dict([(n, s) for n, s in zip(self.xnames, *Si)])
            name2ti = dict([(n, t) for n, t in zip(self.xnames, *Ti)])
            return name2si, name2ti
        else:
            return {self.xnames[0]: 1.}, {self.xnames[0]: 1.}
