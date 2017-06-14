import glob
import sys
import os
import json
reload(sys)
sys.setdefaultencoding("utf-8")

def stat_info(filepath, stat):
    filename = os.path.basename(filepath)
    print "stat [%s]" %filename
    cnt = 0
    for line in file(filepath, 'r'):
        cnt += 1
        if cnt % 100000 == 0:
            print "\tcnt = %d" %cnt
        url, ename, obj = line.strip().split('\t')
        obj = json.loads(obj)
        stat['entity'] += 1
        if "info_model" in obj:
            model = obj['info_model']
            for key in model:
                if "name" in key:
                    name = key['name']
                    if not name in stat:
                        stat[name] = 0
                    stat[name] += 1

def main():
    stat ={"entity": 0}
    outf = file("result/info_stat.tsv", 'w')
    for filepath in glob.glob("data_info/*txt"):
        stat_info(filepath, stat)        
        # filename = os.path.basename(filepath)
    for name in sorted(stat.keys(), key = lambda x: stat[x], reverse = True):
        outf.write("%s\t%d\n" %(name, stat[name]))
    outf.close()
    



if __name__ == "__main__":
    main()