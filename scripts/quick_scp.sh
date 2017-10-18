paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json
"

for path in $paths
do
    scp lhr@dlib:~/KnowledgeGraph/${path}.sample ${path}
done

cat result/rel_extraction/baike_names.tsv|uniq > tmp
mv tmp result/rel_extraction/baike_names.tsv
