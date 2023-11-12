
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='Malang',
        description='Runs a Malang file',
        epilog='https://github.com/telos-matter/Malang'
        )
    
    parser.add_argument('-d', '--debug', action='store_true', help='Run with debug info')
    parser.add_argument('-i', '--interpret', action='store_true', help='Tries to interpret the output if possible. For numbers with 3 digits or more it would interpret every 3 digits starting from right to left as an ASCII character. For 1 and 0 it would interpret them as TRUE and FALSE')
    parser.add_argument('file_path')
    
    args = vars(parser.parse_args())
    
    from compiler import compile
    compile(args)
