import os
import sys

es = set()
for line in file('result/360_entity.txt'):
    p = line.split("\t")
    es.add(p[0])
print ""
for line in file('result/360entity_data.txt'):
    e = line.split('\t')[0]
    if not e in es:
        print e