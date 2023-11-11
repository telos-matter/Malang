
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='Malang',
        description='Runs a Malang file',
        epilog='https://github.com/telos-matter/Malang'
        )
    
    parser.add_argument('-d', '--debug', action='store_true', help='Run with debug info')
    parser.add_argument('-i', '--interpret', action='store_true', help='Interpret the output as TRUE or FALSE if possible') # This would be fire with list, cuz we'll be able to show "Hello World!"
    parser.add_argument('file_path')
    
    args = vars(parser.parse_args())
    
    from compiler import compile
    compile(args)
