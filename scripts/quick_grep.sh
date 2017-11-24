urls="\
baike.so.com/doc/5341986-7572116.html \
baike.so.com/doc/5341986-5577429.html \
baike.so.com/doc/4237218-4439330.html \
baike.so.com/doc/4237218-4439337.html
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