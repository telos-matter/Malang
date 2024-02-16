#!/usr/bin/env python

if __name__ == '__main__':
    import argparse
    
    MAIN_FUNCTION_ARGS_NAME = 'args' # The name of the argument in the ArgumentParser that refers to the args that will be passed to the main function
    
    parser = argparse.ArgumentParser(
        prog='Malang',
        description='Runs a Malang file',
        epilog='https://github.com/telos-matter/Malang'
        )
    
    parser.add_argument('-d', '--debug', action='store_true', help='run with debug info.')
    parser.add_argument('-s', '--show', action='store_true', help='show the operation, a.k.a. the program. Use only with small programs.')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose about the program and the output.')
    parser.add_argument('-i', '--interpret', action='store_true', help='tries to interpret the output if possible. Either as ASCII chars or a boolean value.')
    parser.add_argument('file_path', help='the file to run.')
    parser.add_argument(MAIN_FUNCTION_ARGS_NAME, type=float, nargs='*', help='arguments to be passed to the main function.')
    
    options = vars(parser.parse_args())
    args = options[MAIN_FUNCTION_ARGS_NAME]
    del options[MAIN_FUNCTION_ARGS_NAME]
    
    from runner import run
    run(options, args)

else:
    raise Exception(f"This file is expected to be run as the main one")
