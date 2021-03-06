urls="\
baike.so.com/doc/6759533-6974158.html \
baike.so.com/doc/5401418-25012047.html \
baike.so.com/doc/4542215-4752596.html
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
result/rel_extraction/baike_filtered_summary_with_infobox.json \
result/rel_extraction/baike_ename_title.tsv \
result/360/360_entity_info_processed.json \
"
sample_dir="result/samples"
for path in $paths
do
    filename=$(basename $path)
    echo $filename
    # rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${sample_dir}/${filename}
    done
done