import sys

cnt = 0
predicts = set()
for line in file(sys.argv[1]):
    cnt += 1
    p = line.strip().split('\t')
    if cnt % 1000000 == 0:
        print "cnt = %d" %cnt
    predict = p[1]
    predicts.add(predict)


outf = file(sys.argv[2], 'w')
for p in sorted(predicts):
    outf.write(p + '\n')
outf.close()

