urls="\
baike.so.com/doc/6742505-6957031.html \
baike.so.com/doc/496293-525481.html \
baike.so.com/doc/5492605-5730517.html \
baike.so.com/doc/3450004-3630414.html
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