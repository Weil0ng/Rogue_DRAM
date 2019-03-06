import argparse
import logging
from distributions import SupportedDistributions

args=None

def get_parser():
    parser = argparse.ArgumentParser()
    return parser

def parse_args(parser):
    args = parser.parse_args()
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(format='%(levelname)s: %(message)s', level=numeric_level)
    return args

def addCommonOptions(parser):
    parser.add_argument('--log', action='store', dest='loglevel',
            default='info', help='Set log level to: info, debug, verbose.')

def addModelOptions(parser):
    parser.add_argument('--dist', action='store', dest='dist',
            default='Normal', choices=SupportedDistributions.dists.keys(),
            help='Select distribution to sample from.')
    parser.add_argument('--unit', action='store', dest='unit',
            default='', help='Unit of random variable.')
    parser.add_argument('--mean', action='store', type=float, default=0.,
            help='Mean value to construct the distribution with.')
    parser.add_argument('--std', action='store', type=float, default=.1,
            help='Standard deviation to construct the distribution with.')
    parser.add_argument('--lower', action='store', type=float, default=None,
            help='Enforced lower bound.')
    parser.add_argument('--upper', action='store', type=float, default=None,
            help='Enforced upper bound.')
    parser.add_argument('--N', action='store', type=int, default=10,
            help='Sample size.')
    parser.add_argument('--gpc', action='store', type=float, default=None,
            help='gPC order.')
    parser.add_argument('--saltelli', action='store_true', default=False,
            help='Use Saltelli sample.')

def addIOOptions(parser):
    parser.add_argument('--config', action='store', default=None,
            help='Config files to construct distributions from.')
    parser.add_argument('--model-path', action='store', default='gpc_model',
            help='File path to dump gpc model from matlab.')
    parser.add_argument('--sample-path', action='store', default=None,
            help='File path to store samples.')
    parser.add_argument('--ini', action='store', default=None,
            help='File path to ini template.')
