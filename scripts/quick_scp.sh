paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
result/rel_extraction/baike_filtered_summary_with_infobox.json \
result/rel_extraction/baike_ename_title.tsv \
result/360/360_entity_info_processed.json
"

sample_dir="result/samples"
for path in $paths
do
    filename=$(basename $path)
    scp lhr@dlib:~/KnowledgeGraph/${sample_dir}/${filename} ${path}
done

cat result/rel_extraction/baike_names.tsv|uniq > tmp
mv tmp result/rel_extraction/baike_names.tsv
