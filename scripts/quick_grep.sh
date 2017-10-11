urls="\
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/1287918-24956577.html \
baike.so.com/doc/1287918-10571130.html \
baike.so.com/doc/2526484-2669235.html \
baike.so.com/doc/6149264-6362453.html \
baike.so.com/doc/3433066-3613205.html \
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result_rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json \
"
for path in $paths
do
    
    echo ${path}.sample
    rm ${path}.sample

    for url in $urls
    do
        grep ${url} ${path} >> ${path}.sample
    done
done