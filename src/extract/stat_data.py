import glob
import sys
import os
import json


def stat_data(filepath, stat):
    filename = os.path.basename(filepath)
    print "stat [%s]" %filename
    cnt = 0
    for line in file(filepath, 'r'):
        cnt += 1
        stat['entity'] += 1
        if cnt % 100000 == 0:
            print "\tcnt = %d" %cnt
        obj = json.loads(line)['item']
        if len(obj) >= 1:
            obj = obj[0]
        else:
            continue
        for tag in obj['tags']:
            if not tag in stat:
                stat[tag] = 0
            stat[tag] += 1
        
        
        

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")

    outf = file('result/data_stat.tsv', 'w')
    stat = {"entity": 0}
    for filepath in glob.glob('data/*txt'):
        stat_data(filepath, stat)
    
    for name in sorted(stat.keys(), key = lambda x: stat[x], reverse = True):
        outf.write("%s\t%d\n" %(name, stat[name]))
    outf.close()

    