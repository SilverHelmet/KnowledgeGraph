import os
import glob
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

error_cnt = 0
error_cnt2 = 0
def extract_entity(filepath, outf):
    global error_cnt , error_cnt2
    print "extract_entity from [%s]" %filepath
    cnt = 0
    for line in file(filepath):
        cnt += 1
        if cnt % 10000 == 0:
            print "\tcnt = %d" %cnt
        obj = json.loads(line)['item']
        if len(obj) == 0:
            error_cnt += 1
        elif len(obj) >= 2:
            error_cnt += 1
        else:
            obj = obj[0]
            entity = obj['ename']
            eid = obj['eid']
            sid = obj['sid']
            outf.write('%s\t%s\t%s\n' %(entity, eid, sid))
    


outf = file("result/360entity_data.txt", 'w')
for filepath in glob.glob("data/360/data/baike*txt"):
    extract_entity(filepath, outf)
outf.close()

print "errorcnt = %d" %error_cnt
print "error_cnt2 = %d" %error_cnt2
    
