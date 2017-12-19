#encoding: utf-8
import os
import glob
import re
from src.IOUtil import table_dir, Print
from src.util import add_to_dict_list
from src.extractor.resource import Resource
from src.mapping.fb_date import BaikeDatetime
from src.extractor.structure import Knowledge


delimeters = [u';', u'；', u'、', u'，', u',', u'/']

def find_award(text, name2urls, ner):
    if text in name2urls:
        return [(text, 'Nz')]
    
    ltp_result = ner.ltp.parse(text)
    str_entities = ner.recognize(text, ltp_result, None)
    names = []
    for str_entity in str_entities:
        name = ltp_result.text(str_entity.st, str_entity.ed)
        names.append((name, 'Nz'))
    return names

def find_entities(text, name2urls):
    global delimeters
    uni_text = text.decode('utf-8')
    names = []
    if uni_text.startswith(u"《") and uni_text.endswith(u'》'):
        names.append((uni_text[1:-1], 'Nb'))
    elif text in name2urls:
        names.append((uni_text, 'Nz'))
    else:
        max_sep = delimeters[0]
        for sep in delimeters:
            if len(uni_text.split(sep)) > len(uni_text.split(max_sep)):
                max_sep = sep

        values = uni_text.split(max_sep)
        for value in values:
            names.append((value, 'Nz'))

    names = [(value.encode('utf-8'), etype) for value, etype in names]
    return names



class TableRelationParser:
    re_type_rel = re.compile(r'\((?P<type>[^\)]+)\)(?P<rel>.+)')
    def __init__(self, line):
        self.need_cols = set()

        p = line.strip().split(' ')
        if p[0] == 'if':
            self.valid_func = p[1:4]
            assert p[2] in ['has', 'type']
            self.need_cols.add(p[1])
            self.subj_name = p[4]
            self.obj_name = p[5]
            self.rels = p[6:]
        else:
            self.valid_func = None
            self.subj_name = p[0]
            self.obj_name = p[1]
            self.rels = p[2:]

        self.rels = [self.parse_rel(rel) for rel in self.rels]
        self.need_cols.add(self.subj_name)
        self.need_cols.add(self.obj_name)
        if 'entity' in self.need_cols:
            self.need_cols.remove('entity')

    def parse_rel(self, rel):
        res = TableRelationParser.re_type_rel.match(rel)
        if res:
            return res.group('type'), res.group('rel')
        else:
            return None, rel

    def check_valid_names(self, row):
        for name in self.need_cols:
            if name not in row:
                return False
            if len(row[name]) == 0:
                return False
        return True

    def check_valid(self, row, entity_types):
        if not self.valid_func:
            return True
        if self.valid_func[1] == 'has':
            return self.valid_func[2] in row[self.valid_func[0]]
        if self.valid_func[1] == 'type':
            return self.valid_func[2] in entity_types
        return False

    def choose_relation(self, subj_types):
        for fb_type, rel in self.rels:
            if fb_type is None or fb_type in subj_types:
                return rel
        return None

        
class TableRule:
    def __init__(self, first_line):
        self.name = first_line.strip().split(' ')[1]
        self.load_stat = "None"
        self.value_valid_funcs = []
        self.name_map = {}
        self.preferred_types = {}
        self.extra_names = {}
        self.forced_type_names = set()
        self.rel_parsers = []
        self.register_tables = set()
        self.context_col_names = set()

    def load_line(self, line):
        if line.startswith('##'):
            return True

        if line.startswith('#'):
            self.load_stat = line.strip()[1:]
            return False

        if self.load_stat == 'value':
            self.add_value_limit(line)
        elif self.load_stat == 'name_map':
            self.add_name_map(line)
        elif self.load_stat == 'type':
            self.add_preferred_type(line)
        elif self.load_stat == 'relation':
            self.add_relation(line)
        elif self.load_stat == 'table':
            self.register_table(line)
        return False

    def add_value_limit(self, line):
        p = line.strip().split(" ")
        assert len(p) == 3

        key, comp, value = p
        if comp == '=':
            valid_func = lambda row: row.get(key, value) == value
            self.value_valid_funcs.append(valid_func)
        else:
            print 'error symbol %s' %comp

    def is_valid_row(self, row):
        for valid_func in self.value_valid_funcs:
            if not valid_func(row):
                return False
        return True

    def add_name_map(self, line):
        p = line.strip().split(' ')
        assert len(p) == 2 and p[0] not in self.name_map
        self.name_map[p[0]] = p[1]

    def add_preferred_type(self, line):
        line = line.strip()
        if line.endswith("*"):
            line = line[:-1]
            p = line.strip().split(' ')
            self.forced_type_names.add(p[0])
        else:
            p = line.strip().split(' ')
        assert len(p) >= 2

        names = p[0].split('&')
        assert len(names) <= 2
        self.preferred_types[names[0]] = p[1:]
        if len(names) == 2:
            self.extra_names[names[0]] = names[1]

    def is_valid_types(self, types):
        for etype in self.preferred_types['entity']:
            if etype == "None" or etype in types:
                return True
        return False


    def add_relation(self, line):
        relation_parser = TableRelationParser(line)
        self.rel_parsers.append(relation_parser)

    def register_table(self, line):
        self.register_tables.add(line.strip())

    def has_types(self, types1, types2):
        types1 = set(types1)
        for fb_type in types2:
            if fb_type in types1:
                return True
        return False

    def link_cell(self, col_name, row, row_values, context, page_info, entity_types, elinker):
        if col_name == "entity":
            return [(page_info.url, page_info.ename, entity_types)]

        col_entities = row_values[col_name]

        f_type = self.preferred_types[col_name][0]
        if f_type == 'str':
            return [(e[0], row[col_name], ['text']) for e in col_entities]
        elif f_type == 'time':
            return [(e[0], row[col_name], ['datetime']) for e in col_entities]
        else:
            preferred_types = self.preferred_types[col_name]
            baike_entities = []
            for entity in col_entities:
                name, etype = entity
                removed = False
                if name in context:
                    context.remove(name)
                    removed = True
                
                baike_entity = elinker.link_table_name(name, etype, context, page_info, preferred_types)
                if baike_entity:
                    baike_entities.append((baike_entity.baike_url, name, baike_entity.types))
                elinker.add_table_map(name + " ".join(preferred_types), baike_entity)

                if removed:
                    context.add(name)

            if col_name in self.forced_type_names:
                baike_entities = [e for e in baike_entities if self.has_types(e[2], preferred_types)]

            return baike_entities
                

    def unfold_row(self, row, name2urls, ner):
        unfold_row_values = {}
        for name in row:
            if not name in self.preferred_types:
                continue
            f_type = self.preferred_types[name][0]
            if f_type == 'str':
                values = [(row[name], 'text')]
            elif f_type == 'time':
                baike_date = BaikeDatetime.parse(row[name])
                if baike_date:
                    values = [(baike_date, 'Nt')]
                else:
                    values = []
            elif name in self.forced_type_names:
                values = find_award(row[name], name2urls, ner)
            else:
                values = find_entities(row[name], name2urls)
                # if name in self.extra_names:
                #     extra_name = self.extra_names[name]
                #     if extra_name in row:
                #         values.append(row[extra_name], 'Nz')
            unfold_row_values[name] = values
        return unfold_row_values

    def parse_row(self, row, page_info, entity_types, elinker, ner):
        if not self.is_valid_row(row):
            return []

        unfold_row_values = self.unfold_row(row, elinker.name2bk, ner)

        context = set()
        for name in self.context_col_names:
            if name in row:
                for value in unfold_row_values[name]:
                    context.add(value[0])
        context.update(page_info.names)

        knowledges = []
        parsed_name_pairs = set()
        link_cache = {}

        for rel_parser in self.rel_parsers:
            if not rel_parser.check_valid_names(row):
                continue

            if not rel_parser.check_valid(row, entity_types):
                continue

            pair_key = rel_parser.subj_name + " # " + rel_parser.obj_name
            if pair_key in parsed_name_pairs:
                continue

            if not rel_parser.subj_name in link_cache:
                entities = self.link_cell(rel_parser.subj_name, row, unfold_row_values, context, page_info, entity_types, elinker)
                link_cache[rel_parser.subj_name] = entities
            if not rel_parser.obj_name in link_cache:
                entities = self.link_cell(rel_parser.obj_name, row, unfold_row_values, context, page_info, entity_types, elinker)
                link_cache[rel_parser.obj_name] = entities
            
            subj_entities = link_cache[rel_parser.subj_name]
            obj_entities = link_cache[rel_parser.obj_name]

            new_kns = []
            for subj_entity in subj_entities:
                for obj_entity in obj_entities:
                    rel = rel_parser.choose_relation(subj_entity[1])
                    if rel:
                        new_kns.append(Knowledge(subj_entity[1], 'None', obj_entity[1], subj_entity[0], rel, obj_entity[0]))

            if len(new_kns) > 0:
                parsed_name_pairs.add(pair_key)
                knowledges.extend(new_kns)


        return knowledges

    def transfer_col_name(self, col_names):
        new_col_names = []
        for x in col_names:
            if x in self.name_map:
                new_col_names.append(self.name_map[x])
            else:
                new_col_names.append(x)
        return new_col_names

    def init_context_name(self):
        for name in self.preferred_types:
            first_type = self.preferred_types[name][0]
            if first_type in ['str', 'time']:
                continue
            if name in self.forced_type_names:
                continue
            self.context_col_names.add(name)
        self.context_col_names.remove('entity')

    def check(self, schema):
        assert self.load_stat == 'table'
        all_names = set()
        for table in self.register_tables:
            for x in table.split(" # "):
                all_names.add(x)
        all_names.add('entity')

        for key_name in self.name_map:
            value = self.name_map[key_name]
            assert key_name in all_names
            assert value in all_names

        for name in self.preferred_types:
            assert not name in self.name_map
            types = self.preferred_types[name]
            assert name in all_names or name == 'entity'
            for fb_type in types:
                assert fb_type in schema.type_attrs or fb_type in ['time', 'str', 'None']

        for rel_parser in self.rel_parsers:
            for x in rel_parser.need_cols:
                assert x not in self.name_map
                assert x in all_names
            assert rel_parser.subj_name in self.preferred_types
            for rel in rel_parser.rels:
                fb_type, fb_rels = rel
                assert fb_type in schema.type_attrs or fb_type is None
                if len(fb_rels) == 2:
                    assert schema.expected_type(fb_rels[0]) == schema.schema_type(fb_rels[1])

                for fb_rel in fb_rels.split("^"):
                    assert fb_rel in schema.property_attrs
    
class TableParser():
    def __init__(self, elinker, ner):
        self.elinker = elinker
        self.ner = ner
        self.table_rules = []
        self.table2rules = {}

    def init(self, paths = None):
        if paths is None:
            rules_dir = os.path.join(table_dir, 'rules')
            paths = glob.glob(rules_dir + "/*rule")

        path_str = " ".join([os.path.basename(x) for x in paths])
        Print('load table rule from [%s]' %path_str)
        for path in paths:
            self.load_from_file(path)

    def load_from_file(self, filepath):
        table_rule = None
        for line in file(filepath):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("##") and table_rule is None:
                table_rule = TableRule(line)
                self.table_rules.append(table_rule)
            else:
                finished = table_rule.load_line(line)
                if finished:
                    table_rule = None

    def load_extra_table(self, path = None):
        if path is None:
            path = os.path.join(table_dir, 'rules/extra_table.tsv')
        Print('load extra table from [%s]' %os.path.basename(path))
        for line in file(path):
            p = line.strip().split("\t")
            table = p[0]
            rule_names = p[1:]
            for rule in rule_names:
                find = False 
                for table_rule in self.table_rules:
                    if table_rule.name == rule:
                        find = True
                        table_rule.register_table(table)
                        break
                assert find

    def finish_load(self):
        for table_rule in self.table_rules:
            for table in table_rule.register_tables:
                table = sorted_table(table)
                if not table in self.table2rules:
                    self.table2rules[table] = []

                has_in = False
                for o_rule in self.table2rules[table]:
                    if o_rule.name == table_rule.name:
                        has_in = True
                if not has_in:
                    self.table2rules[table].append(table_rule)
            table_rule.init_context_name()

    def parse(self, table_obj, page_info, entity_types):
        table = sorted_table(" # ".join(table_obj['columns']))

        rules = self.table2rules.get(table, [])
        rules = [rule for rule in rules if rule.is_valid_types(entity_types)]
        
        if len(rules) != 1:
            return []


        rule = rules[0]
        knowledges = []
        columns = rule.transfer_col_name(table_obj['columns'])
        
        for row in table_obj['rows']:
            row_map = {}
            for name, value in zip(columns, row):
                row_map[name] = value
            row_knowledges = rule.parse_row(row_map, page_info, entity_types, self.elinker, self.ner)
            if len(row_knowledges) > 0:
                knowledges.append((" # ".join(row), row_knowledges))
        return knowledges
            

def sorted_table(table):
    cols = table.split(" # ")
    sorted_table = " # ".join(sorted(cols))
    return sorted_table

def encode_table(table):
    cols = table['columns']
    rows = table['rows']
    cols = [x.encode('utf-8') for x in cols]
    rows = [[x.encode('utf-8')for x in row] for row in rows]
    return {'columns':cols, 'rows': rows}


if __name__ == "__main__":
    rules_dir = os.path.join(table_dir, 'rules')
    table_parser = TableParser(None, None)
    paths = glob.glob(rules_dir + "/*rule")
    table_parser.init(paths)
