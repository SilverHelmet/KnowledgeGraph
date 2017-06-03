# python -u -m src.360process.process_entity_info >& log/process_entity_info.log
python -u -m src.mapping.name_mapping >& log/name_mapping.log
python -u -m src.mapping.stat_mapping >& log/stat_mapping.log
python -u -m src.mapping.one2one_mapping_cnt >& log/one2one_3.log
pytyhon -u -m src.mapping.predicate_mapping >& log/predicate_mapping.log