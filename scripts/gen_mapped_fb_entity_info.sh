# python -u -m src.fb_process.extract_mediator >& log/extract_mediator.log 
python -u -m src.fb_process.filter_useful_ttl result/freebase/mediator_property.ttl  result/freebase/mediator_med_property.ttl property_mediator_ttl 50413655 >& log/filter_mediator_med_property.log 
python -u -m src.mapping.classify.gen_fb_property >& log/gen_fb_property.log 
python -u -m src.mapping.classify.gen_fb_property_name >& log/gen_fb_property_name.log 
python -u -m src.mapping.classify.calc_infobox_mapping_score >& log/calc_mapping_score.log