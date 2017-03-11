import sys
import os
import glob

def extract_entity(filepath, outf):
    print "extract entity from [%s]" %filepath
    for cnt, line in enumerate(file(filepath)):
        if cnt % 10000 == 0:
            print "\tcnt = %d" %cnt
        p = line.split("\t")
        outf.write(p[1] + "\t" + p[0]+ '\n')

if __name__ == "__main__":
    outf = file('result/360_entity.txt', 'w')
    for filepath in glob.glob('data/360/data_info/*txt'):
        extract_entity(filepath, outf)

    outf.close()