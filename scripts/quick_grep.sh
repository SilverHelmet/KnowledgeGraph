urls="\
baike.so.com/doc/4786053-5002045.html
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
result/rel_extraction/baike_filtered_summary_with_infobox.json \
result/rel_extraction/baike_ename_title.tsv \
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