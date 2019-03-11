from options import *
from response_surface import GPCRS

def build_gpc_model():
    global args
    assert args.model_path
    model = GPCRS('gem5_gpc_model', args.config)
    model.load_model(args.model_path)
    model.add_train_x(args.sample_path)
    model.add_train_y(args.output_path)
    model.train()

def main():
    global args
    parser = get_parser()
    addCommonOptions(parser)
    addIOOptions(parser)
    args = parse_args(parser)

    build_gpc_model()

if __name__ == '__main__':
    main()
