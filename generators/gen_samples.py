from Config import Config
from collections import defaultdict
from distributions import SupportedDistributions
from options import *
import functools
import numpy as np
import pickle

matlab_code_home = r'/Users/weil0ng/Stochastic-Testing-model'

def read_config(path):
    with open(path, 'r') as f:
        config_strs = [s.strip('\n') for s in f.readlines() if not s.startswith('#')]
        configs = [Config(config_str.split()) for config_str in config_strs]
        input_order = [config.name for config in configs]
        name2config = dict([(c.name, c) for c in configs])
    # samples: param name -> list of sample values
    samples = {}
    if args.saltelli:
        samples = saltelli_sample(configs, args.N)
    elif args.gpc:
        logging.debug('gPC sampling...with order {}'.format(args.gpc))
        model_spec = [(config.name, config.dist) + config.get_gpc_spec() for config in configs]
        samples = gpc_sample(model_spec, args.gpc)
    else:
        for config in configs:
            config.dump()
            dist, samples[config.name] = sample(config.dist, config.mean, config.std,
                    config.lb, config.ub, args.N)
            logging.debug('{} sampled from:'.format(config.dist))
            dist.dump()
    # feed: param name -> list of 'param_name value'
    feed = {}
    for k in samples:
        if name2config[k].transform:
            transformed_samples = [name2config[k].transform(v) for v in samples[k]]
            samples[k] = transformed_samples
        feed[k] = [k + ' ' + repr(v) + name2config[k].unit for v in samples[k]]
        if not args.gpc:
            assert len(feed[k]) == args.N + 1, 'feed len {} != {}'.format(len(feed[k]), args.N + 1)
    # gem5_feed: list of 'param_name1 value1 param_name2 value2 ...'
    gem5_feed = map(lambda x: ' '.join(x), zip(*[feed[inp] for inp in input_order]))
    if args.sample_path:
        print '{} samples saved to {}'.format(len(gem5_feed), args.sample_path)
        with open(args.sample_path, 'w') as f:
            f.write('\n'.join(gem5_feed) + '\n')
        f.close()
    else:
        print 'samples:\n{}'.format(gem5_feed)

def saltelli_sample(configs, N):
    """ Call SALib to sample.
    
    Have to use corresponding sampling strategy
    to perform SA later, except for Delta (Plischke et al. 2013).
    """
    from SALib.sample import saltelli
    sa_problem = {'num_vars': len(configs),
            'names': [c.name for c in configs],
            'dists': [c.salib_dist for c in configs],
            'bounds': [[c.mean, c.std] for c in configs] # These are not really bounds if dist is not uniform, but mean and std.
            }
    assert N % (2 * len(configs) + 2) == 0, 'N ({}) not valid for saltelli sample, consider {}'.format(
            N, (N / (2 * len(configs) + 2) + 1) * (2 *len(configs) + 2))
    saltelli_n = int(N / (2 * len(configs) + 2))
    assert saltelli_n > 0
    logging.debug('SA problem def: {}\nSaltelli sample with N={}'.format(sa_problem, saltelli_n))
    saltelli_samples = saltelli.sample(sa_problem, saltelli_n)
    samples = {}
    for idx, c in enumerate(configs):
        samples[c.name] = map(c.salib_dtype_func, [c.mean] + saltelli_samples[:, idx].tolist())
    return samples

def gpc_sample(model_spec, order):
    """ Call gpc matlab code.

    model_spec: []  List of tuples, first ele is param name, followed by dist, mean and std.
    order: gpc order, must be of type float.
    """

    import os
    import matlab.engine
    engine = matlab.engine.start_matlab()
    engine.addpath(r'../gpc_interface/')
    for root, subdirs, files in os.walk(matlab_code_home):
        if not '.git' in root:
            engine.addpath(root)
    #engine = matlab.engine.connect_matlab()
    #result, gpc_model = engine.gpc_sample([(pn, dn, float(m), float(s)) for (pn, dn, m, s) in model_spec], order, nargout=2)
    logging.debug('gpc sample with spec: {}'.format(model_spec))
    result, gpc_model = engine.gpc_sample(model_spec, order, nargout=2)
    save_model_path = args.model_path
    with open(save_model_path, 'wb') as f:
        print 'GPC model saved to {}'.format(save_model_path)
        pickle.dump(gpc_model, f)
        f.close()
    samples = {}
    for i in range(len(model_spec)):
        samples[model_spec[i][0]] = result[i]
    return samples

def sample(dist, mean, std, lower, upper, N):
    assert dist in SupportedDistributions.dists, dist
    dist = SupportedDistributions.dists[dist]
    return dist, dist.sample(mean, std, lower=lower, upper=upper, N=N)

def main():
    global args
    parser = get_parser()
    addCommonOptions(parser)
    addModelOptions(parser)
    addIOOptions(parser)
    args = parse_args(parser)
    
    if args.config:
        read_config(args.config)
    else:
        dist, _ = sample(args.dist, args.mean, args.std, args.lower, args.upper, args.N)
        dist.dump(unit=args.unit)

if __name__ == '__main__':
    main()
