paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result_rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json \
"

for path in $paths
do
    scp lhr@dlib:~/Knowledge/${path}.sample ${path}
done
