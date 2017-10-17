urls="\
baike.so.com/doc/1454208-10392305.html \
baike.so.com/doc/1454208-10410299.html \
baike.so.com/doc/1454208-24991848.html \
baike.so.com/doc/1454208-24852988.html \
baike.so.com/doc/1454208-24862852.html \
baike.so.com/doc/5328372-24915290.html \
baike.so.com/doc/1454208-24921790.html \
baike.so.com/doc/1454208-24936354.html \
baike.so.com/doc/1454208-1537614.html \
baike.so.com/doc/1454208-1537673.html \
baike.so.com/doc/1454208-1537755.html \
baike.so.com/doc/1454208-1537801.html \
baike.so.com/doc/1454208-11486109.html \
baike.so.com/doc/1454208-11488572.html \
baike.so.com/doc/1454208-11490452.html \
baike.so.com/doc/10886209-11412281.html \
baike.so.com/doc/8566767-8887491.html \
baike.so.com/doc/6761196-6975838.html \
baike.so.com/doc/1454208-24857618.html \
baike.so.com/doc/24007323-24583776.html \
baike.so.com/doc/8196475-8513463.html \
baike.so.com/doc/1454208-1537384.html \
baike.so.com/doc/1454208-1537473.html \
baike.so.com/doc/1454208-1537553.html \
baike.so.com/doc/1454208-1537900.html 
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json \
"
for path in $paths
do
    
    echo ${path}.sample
    # rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${path}.sample
    done
done