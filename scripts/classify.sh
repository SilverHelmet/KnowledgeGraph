# python -u -m src.baike_process.process_entity_info >& log/process_entity_info.log 
# python -u -m src.mapping.classify.calc_infobox_mapping_score >& log/calc_mapping_score.log

# gen predicate mapping
# python -u -m src.mapping.classify.gen_good_one2one_mapping >& log/gen_good_one2one.log
# python -u -m src.mapping.classify.gen_baike_class_to_fb
# python -u -m src.mapping.predicate_mapping >& log/predicate_mapping.log
# python -m src.mapping.collect_predicate_mapping_result


python -u -m src.mapping.classify.simple_classify >& log/simple_classify.log
python -u -m src.mapping.classify.merge_classify_result >& log/merge_classify_result.log


# gen final predicate mapping
mapping_result='result/360/mapping/classify/mapping_result.tsv'
predicate_out='result/360/mapping/final_info_predicate_mapping.tsv'
predicate_collect_out='result/360/mapping/final_predicates_map.json'
python -u -m src.mapping.classify.gen_baike_class_to_fb $mapping_resul  'result/360/mapping/classify/final_baike_cls2fb_type.json'
python -u -m src.mapping.predicate_mapping $mapping_result $predicate_out >& log/final_predicate_mapping.log
python -u -m src.mapping.collect_predicate_mapping_result $predicate_collect_out 
