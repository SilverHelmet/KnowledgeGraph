urls="\
baike.so.com/doc/4391556-4598176.html \
baike.so.com/doc/6707957-6921972.html \
baike.so.com/doc/6724155-6938295.html \
baike.so.com/doc/6411356-6625024.html \
baike.so.com/doc/6411356-6625024.html
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
    rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${path}.sample
    done
done