""" This script tries to generate cacti configs from a sample file.

Cacti will be called to generate params to gem5 for perf evaluation.
"""

from options import *
import copy
import logging
import os
import re
import numpy as np
import pickle

def read_samples(sample_path):
    with open(sample_path, 'r') as f:
        logging.debug('loading samples from: {}'.format(sample_path))
        lines = [l.strip('\n') for l in f.readlines() if not l.startswith('#')]
        f.close()
    assert lines, 'ERROR: empty samples in {}'.format(sample_path)
    # Keep record of input vector, i.e., [param_name].
    params = lines[0].split()[::2]
    values = [[float(re.sub(r'[^0-9\.]', '', w)) for w in l.split()[1::2]] for l in lines]
    return dict([(p, vs) for p, vs in zip(params, zip(*values))])

def gen_inis(sample_path, ini_template, output_path):

    samples = read_samples(sample_path)
    logging.debug('samples: {}'.format(samples))

    with open(ini_template, 'r') as f:
        ini_configs = [l for l in f.readlines() if not l.startswith(';')]
        f.close()
    configs = [copy.copy(ini_configs) for i in range(len(samples.values()[0]))]

    seen = {}
    for i, line in enumerate(ini_configs):
        for k, vals in samples.iteritems():
            k = k[1:]
            if k in line:
                seen[k] = True
                val_pos = line.find('=')
                for cur, v in enumerate(vals):
                    configs[cur][i] = line[:val_pos+len('=')] + '{};'.format(v)
                break # Only one option per line
    for k in samples.keys():
        if k[1:] not in seen:
            print 'WARNING: {} not found in ini template'.format(k)
    
    # Make persistent.
    template_base_name = ini_template[ini_template.rfind('/')+1:]
    dest = os.getcwd() + '/' + output_path
    if not os.path.exists(dest):
        os.mkdir(dest)
    for i, config in enumerate(configs):
        with open(dest + '/' + template_base_name + '_' + str(i), 'w') as f:
            f.write('\n'.join(config))
            f.close()

def main():
    global args
    parser = get_parser()
    addCommonOptions(parser)
    addModelOptions(parser)
    addIOOptions(parser)
    args = parse_args(parser)
    
    assert args.sample_path and args.ini and args.output_path, \
            'Must specify --sample-path, --ini and --output-path'
    gen_inis(args.sample_path, args.ini, args.output_path)

if __name__ == '__main__':
    main()
