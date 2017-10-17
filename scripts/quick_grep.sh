urls="\
baike.so.com/doc/8066286-8383267.html \
baike.so.com/doc/125863-132966.html \
baike.so.com/doc/3568926-3753170.html
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