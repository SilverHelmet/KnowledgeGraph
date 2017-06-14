import sys

if __name__ == "__main__":
    for line in sys.stdin:
        p = line.strip().split("\t")
        baike_cnt = int(p[1])
        fb_cnt = int(p[2])
        if fb_cnt >= baike_cnt * 2:
            print line.strip()

