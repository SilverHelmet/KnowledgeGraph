urls="\
baike.so.com/doc/1939057-2051423.html \
baike.so.com/doc/1907411-2018222.html \
baike.so.com/doc/1924517-2036078.html \
baike.so.com/doc/10002015-10349837.html
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