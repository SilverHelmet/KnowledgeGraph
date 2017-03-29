from .extract_util import encode
import sys

if __name__ == "__main__":
    for line in sys.stdin:
        p = line.strip().split("\t")
        print encode(p[0])