
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='Malang',
        description='Runs a Malang file',
        epilog='https://github.com/telos-matter/Malang'
        )
    
    parser.add_argument('file_path', help='the file to compile and run')
    parser.add_argument('-d', '--debug', action='store_true', help='run with debug info')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose about the program and the output')
    parser.add_argument('-i', '--interpret', action='store_true', help='tries to interpret the output if possible. Either as ASCII chars or a boolean value.')
    
    args = vars(parser.parse_args())
    
    from compiler import compile
    compile(args)

else:
    raise Exception(f"This file is expected to be run as the main one")
