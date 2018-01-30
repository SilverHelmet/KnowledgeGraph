mkdir ~/360task/result
mkdir ~/360task/result/rel_extraction
cp ~/KnowledgeGraph/result/rel_extraction/baike_names.tsv \
~/KnowledgeGraph/result/rel_extraction/baike_ename_title.tsv \
~/KnowledgeGraph/result/rel_extraction/baike_static_info.tsv \
~/KnowledgeGraph/result/rel_extraction/baike_filtered_summary_with_infobox.json \
~/360task/result/rel_extraction
cp -r ~/KnowledgeGraph/result/rel_extraction/extra_name \
~/KnowledgeGraph/result/rel_extraction/extra_type \
~/KnowledgeGraph/result/rel_extraction/tables \
~/KnowledgeGraph/result/rel_extraction/dict \
~/KnowledgeGraph/result/rel_extraction/dataset \
~/360task/result/rel_extraction

mkdir ~/360task/docs
cp ~/KnowledgeGraph/docs/final_type_attrs.json \
~/KnowledgeGraph/docs/stopwords.txt \
~/KnowledgeGraph/docs/human_add_predicate_map.json \
~/KnowledgeGraph/docs/one2one_name_attr.txt \
~/KnowledgeGraph/docs/important_domains.txt \
~/KnowledgeGraph/docs/human_add_type_attr.json \
~/KnowledgeGraph/docs/human_add_language.txt \
~/KnowledgeGraph/docs/final_property_attrs.json \
~/360task/docs

cp -r ~/KnowledgeGraph/src ~/KnowledgeGraph/scripts ~/KnowledgeGraph/lib ~/360task


