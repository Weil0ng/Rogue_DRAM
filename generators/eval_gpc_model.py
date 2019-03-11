import numpy as np
import pickle
import re
from options import *
from response_surface import GPCRS

def test_gpc_model(config_path, model_path, input_path, output_path):
    assert config_path and model_path and input_path and output_path
    model = GPCRS('gem5_gpc_model', config_path)
    model.load_model(model_path)
    with open(input_path, 'r') as f:
        logging.debug('loading x values from: {}'.format(input_path))
        lines = [l.strip('\n') for l in f.readlines()]
        logging.debug('{} samples loaded'.format(len(lines)))
        f.close()
    assert lines, 'ERROR: empty samples in {}'.format(sample_path)
    # Keep record of input vector, i.e., [param_name].
    input_dimensions = lines[0].split()[::2]
    xs = [[float(re.sub(r'[^0-9\.]', '', w)) for w in l.split()[1::2]] for l in lines]
    ys = model.eval(xs)
    with open(output_path, 'w') as f:
        f.write('\n'.join([str(y) for y in ys]))
        f.close()
    print 'Predictions written to {}'.format(output_path)

def main():
    global args
    parser = get_parser()
    addCommonOptions(parser)
    addIOOptions(parser)
    args = parse_args(parser)

    test_gpc_model(args.config, args.model_path, args.sample_path, args.output_path)

if __name__ == '__main__':
    main()
