urls="\
baike.so.com/doc/9251204-9584628.html \
baike.so.com/doc/1303554-1378305.html \
baike.so.com/doc/4835038-5051941.html
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
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