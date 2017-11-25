paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
baike_filtered_summary_with_infobox.json \
result/rel_extraction/baike_ename_title.tsv \
result/360/360_entity_info_processed.json
"

for path in $paths
do
    scp lhr@dlib:~/KnowledgeGraph/${path}.sample ${path}
done

cat result/rel_extraction/baike_names.tsv|uniq > tmp
mv tmp result/rel_extraction/baike_names.tsv
