# python -u -m src.rel_extraction.extract_baike_names >& log/extract_baike_names.log

# python -u -m src.rel_extraction.dict.gen_title_rel_dict >& log/gen_title_rel_dict.log 
# python -u -m src.rel_extraction.dict.extra_profession_dict >& log/extra_prof.log
# python -u -m src.rel_extraction.dict.gen_location_dict >& log/gen_location_dict.log 


# extract ename & title
# python -u -m src.rel_extraction.extract_ename_title >& log/extract_ename_title.log

# extract baike summary; filter baike bad summary, merge summary and infobox
# python -u -m src.mapping.classify.extract_baike_summary >& log/extract_baike_summary.log

# extract extra name from summary
# python -u -m src.rel_extraction.extract_summary_extra_name >& log/extract_summary_extra_name.log
# python -u -m src.rel_extraction.dict.collect_team_suffix >& log/collect_team_suffix.log 
# python -u -m src.rel_extraction.extract_team_extra_name >& log/extract_summary_team_extra_name.log 
# python -u -m src.rel_extraction.dict.gen_team_suffix_dict >& log/gen_team_suffix_dict.log


# genenrate extra type
python -u -m src.rel_extraction.extract_son_name_map >& log/extract_son_name_map.log
python -u -m src.rel_extraction.gen_extra_son_type >& log/gen_extra_son_type.log


# extract important domain's name 
python -u -m src.rel_extraction.dict.gen_vertical_domain_dict >& log/gen_vertical_dict.log