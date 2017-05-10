import sys
from ..IOUtil import Print

if __name__ == "__main__":
    in_path = sys.argv[1]
    last_line = None
    for cnt, line in enumerate(file(in_path), start = 1):
        line = line.split('\t')[0]
        if cnt > 1:
            if last_line > line:
                print "error", cnt, last_line, line
        if cnt % 1000000 == 0:
            Print('load cnt = %d' %cnt)
        last_line = line
