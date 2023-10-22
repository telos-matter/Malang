
if __name__ == '__main__':
    import sys

    '''Right now there is only the possibility to compile
    and run a source file
    I want later on to add possibility to compile alone
    and then to run a compiled source file'''
    
    USAGE = """Usage: python3 malang.py <file>"""

    if len(sys.argv) < 2:
        raise Exception(f"ERROR: Expected file path of the program to compile and run\n{USAGE}")
    
    from compiler import runSourceFile
    filePath = sys.argv[1]
    runSourceFile(filePath= filePath)

# TODO add possibility to store compiled version as math equation